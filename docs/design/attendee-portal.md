# Attendee Onboarding Portal

The Attendee Onboarding Portal gives every workshop attendee a single URL where they sign in
with their lab Microsoft account and immediately see their personal `.env` configuration — no
file distribution, no spreadsheets, no manual lookup.

## Purpose

Workshop attendees each receive a unique Foundry project and a set of connection variables.
Distributing those values individually does not scale well and is error-prone. The portal
solves this by serving each attendee's configuration dynamically, gated by their Entra ID
identity.

## Architecture

```text
                        ┌─────────────────────────────────────────────────────────┐
                        │  Azure Container Apps Environment                        │
                        │                                                          │
  Attendee browser  ──► │  ┌─────────────────────────────────────────────────┐    │
  (Entra ID login)       │  │  Container App: ca-portal-<env>                  │    │
                        │  │                                                  │    │
                        │  │  EasyAuth (AzureAD)  ──►  FastAPI app (port 8000)│    │
                        │  │                              │                   │    │
                        │  └──────────────────────────────┼───────────────────┘    │
                        │                                 │                        │
                        └─────────────────────────────────┼────────────────────────┘
                                                          │ managed identity
                                                          ▼
                                         ┌────────────────────────────┐
                                         │  Azure Storage Account      │
                                         │  Container: attendee-onboard│
                                         │  Blob: index.json           │
                                         │  Blobs: <upn>.md            │
                                         └────────────────────────────┘
```

### Components

| Component | Role |
|-----------|------|
| **Azure Container App** (`ca-portal-<env>`) | Hosts the FastAPI portal application. External ingress with HTTPS. Minimum zero replicas (scales to zero when idle). |
| **Container Apps EasyAuth** | Authenticates attendees via Entra ID (single-tenant). Injects the signed-in UPN as `X-MS-CLIENT-PRINCIPAL-NAME` on every proxied request. |
| **FastAPI application** (`tools/attendee-portal/src/app.py`) | Reads the EasyAuth UPN header, looks up the attendee record in `index.json`, and renders the personalised onboarding page. |
| **Azure Storage blob (`index.json`)** | The single source of truth for all attendee configuration. Written by `scripts/generate-attendee-onboarding.py` during post-provision. |
| **Azure Storage blobs (`<upn>.md`)** | Per-attendee markdown backup files uploaded alongside `index.json`. Used for offline distribution or when the portal is unavailable. |
| **User-assigned managed identity** | Authenticates the Container App to the Storage Account with the Storage Blob Data Reader role. Also used to pull the portal image from the shared Azure Container Registry. |
| **Entra app registration** | Created by `scripts/deploy-attendee-portal.py`. Provides the client credentials that EasyAuth uses to validate tokens. |

## Data Flow

```text
azd provision
  └─► scripts/generate-attendee-onboarding.py (post-provision hook)
        ├─► writes .azure/<env>/<upn_local>.md          (local audit files)
        ├─► uploads attendee-onboarding/index.json      (portal source data)
        └─► uploads attendee-onboarding/*.md            (markdown backup blobs)

Attendee visits portal URL
  └─► Container Apps EasyAuth intercepts, redirects to Entra ID login
        └─► Entra ID issues token, EasyAuth injects UPN header
              └─► FastAPI reads X-MS-CLIENT-PRINCIPAL-NAME
                    └─► _upn_key(upn) → looks up index.json
                          └─► renders personalised HTML page
                                ├─► "Download .env" button (/download-env)
                                └─► copy-to-clipboard for env vars and sign-in commands
```

## `index.json` Structure

`index.json` is a flat JSON object. Each key is the UPN local part (dots and underscores
replaced with hyphens, lowercased). A special `_meta` key holds generation metadata.

```json
{
  "_meta": {
    "generatedAt": "2026-06-21T00:00:00Z",
    "totalCount": 5,
    "resolvedCount": 5,
    "attendeePortalUrl": "https://ca-portal-<env>.azurecontainerapps.io"
  },
  "alice-smith": {
    "upn": "alice.smith@contoso.com",
    "projectName": "alice-smith",
    "role": "foundry-project-manager",
    "roleDisplayName": "Foundry Project Manager",
    "resolved": true,
    "envBlock": "AZURE_SUBSCRIPTION_ID=...\nFOUNDRY_PROJECT_NAME=alice-smith\n...",
    "markdownContent": "---\ntitle: Workshop Onboarding - alice-smith\n..."
  }
}
```

The `_upn_key()` function used to derive lookup keys must stay in sync between
`scripts/generate-attendee-onboarding.py` and `tools/attendee-portal/src/app.py`.

## Deployment

The portal is deployed in two stages:

### Stage 1 — Infrastructure (`azd provision`)

`infra/core/host/attendee-portal.bicep` provisions:

- A user-assigned managed identity.
- A Container App with a placeholder image (`mcr.microsoft.com/k8se/quickstart:latest`),
  zero minimum replicas, and the required environment variables (`AZURE_STORAGE_ACCOUNT_NAME`,
  `ATTENDEE_ONBOARDING_CONTAINER`, `PORT`, `AZURE_CLIENT_ID`).
- Role assignments: Storage Blob Data Reader on the storage account, AcrPull on the container
  registry (assigned by `main.bicep`).

### Stage 2 — Image deploy (`scripts/deploy-attendee-portal.py`)

Runs automatically as the `azd` post-provision hook. Steps:

1. `az acr login` — authenticate to the shared Azure Container Registry.
1. `docker build` — build the portal image from `tools/attendee-portal/`.
1. `docker push` — push to the registry with a timestamp tag.
1. `az containerapp update --image` — roll the Container App to the new revision.
1. Find or create the Entra app registration (`<container_app_name>-easyauth`) with the
   correct redirect URI.
1. `az ad app update --enable-id-token-issuance true` — required for Container Apps EasyAuth.
1. `az ad sp create` — create the service principal if it does not exist.
1. `az ad app credential reset` — get or rotate the client secret.
1. `az containerapp secret set` — store the client secret in the Container App.
1. `az containerapp auth microsoft update` — configure EasyAuth with the tenant ID and
   client secret reference.
1. `az containerapp auth update --enabled true --action RedirectToLoginPage` — enable
   authentication and set the default action.

The script is idempotent — it can be re-run safely at any time to re-apply EasyAuth or push
a new image.

### Prerequisites

- Docker Desktop running locally.
- Azure CLI signed in (`az login`).
- `azd` provisioned (`azd provision` completed at least once).

To skip the portal deployment, set `AZURE_CONTAINER_APPS_DEPLOY=false` before provisioning.

## Portal Application (`tools/attendee-portal/src/app.py`)

The portal is a minimal FastAPI application. It is intentionally stateless — every request
loads `index.json` from blob storage.

### Endpoints

| Endpoint | Auth required | Description |
|----------|--------------|-------------|
| `GET /` | Yes (EasyAuth) | Renders the personalised onboarding page. |
| `GET /download-env` | Yes (EasyAuth) | Returns the attendee's `.env` as a file download (`Content-Disposition: attachment; filename=".env"`). |
| `GET /healthz` | No | Liveness probe — returns `ok`. |

### Security

- All HTML output is escaped with `html.escape()` to prevent cross-site scripting.
- The `/healthz` endpoint is the only unauthenticated route; all others are protected by
  EasyAuth before the request reaches the application.
- The managed identity uses DefaultAzureCredential with the specific `AZURE_CLIENT_ID` so
  that the correct user-assigned identity is selected even in a multi-identity environment.
- EasyAuth is configured with `AzureADMyOrg` (single-tenant) to restrict login to the
  workshop tenant.

### UPN key derivation

```python
def _upn_key(upn: str) -> str:
    return upn.split('@')[0].lower().replace('.', '-').replace('_', '-')
```

This function must stay identical in both `generate-attendee-onboarding.py` and `app.py`.

## Branding and UI

The portal renders a full workshop-branded HTML page with:

- The workshop banner image (`docs/public/banners/microsoft-foundry-agentic-workshop.png`)
  served from the GitHub repository's raw content URL.
- A navigation bar with the workshop name and a **Sign out** button (links to `/.auth/logout`).
- The attendee's Foundry role displayed as a badge next to "Signed in as …".
- An unresolved-account warning when `resolved: false` in `index.json`.
- A **Download .env** button (green) below the copyable environment variables code block.
- A Workshop Resources section with links to the GitHub repository, Attendee Quickstart,
  lab modules, Microsoft Foundry documentation, and the Foundry portal (`ai.azure.com`).
- A skip-to-main-content link for keyboard and screen reader users.
- WCAG 2.2 Level AA colour contrast throughout.

## Infrastructure Reference

| Resource | Bicep module |
|----------|-------------|
| Container App | `infra/core/host/attendee-portal.bicep` via `br/public:avm/res/app/container-app:0.22.1` |
| Managed identity | `br/public:avm/res/managed-identity/user-assigned-identity:0.5.1` |
| Role assignments | `infra/main.bicep` (Storage Blob Data Reader, AcrPull) |

## Environment Variables

| Variable | Source | Purpose |
|----------|--------|---------|
| `AZURE_STORAGE_ACCOUNT_NAME` | Bicep output | Storage account hosting `index.json`. |
| `ATTENDEE_ONBOARDING_CONTAINER` | Bicep param (default `attendee-onboarding`) | Blob container name. |
| `PORT` | Bicep param (default `8000`) | Port the uvicorn server listens on. |
| `AZURE_CLIENT_ID` | Managed identity client ID | Selects the correct user-assigned MI for `DefaultAzureCredential`. |

## Troubleshooting

See the [Organizer Guide — Portal troubleshooting](../guide-organizer.md#portal-troubleshooting)
for a table of common symptoms and fixes.
