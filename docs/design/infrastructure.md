# Infrastructure design

This document contains the design rationale for the infrastructure deployed to support the labs in this repository.

## Model-deployment profiles and quota preflight

Bicep cannot resolve a file path at deploy time from a parameter, so profile selection uses three
literal `loadJsonContent` calls chosen by a ternary expression gated on the `modelDeploymentProfile`
param. A custom inline set (`AZURE_MODEL_DEPLOYMENTS`) is injected via
`json(readEnvironmentVariable(...,'[]'))` and overrides the profile when non-empty.

### Profiles

| Profile | File | Deployments | Capacity |
|---|---|---|---|
| `minimal` | `infra/model-deployments.minimal.json` | `chat`, `embedding` | 50 each |
| `default` | `infra/model-deployments.default.json` | `chat`, `embedding`, `gpt54mini` | 50 each |
| `workshop` | `infra/model-deployments.workshop.json` | `chat`, `embedding`, `gpt54mini` | 200 each |
| `broad` | `infra/model-deployments.broad.json` | `chat`, `embedding`, `gpt54`, `gpt54mini`, `gpt54nano`, `gpt53codex` | 500 each |

`chat` and `embedding` are present in every profile - all labs depend only on these two
deployment names and are unaffected by profile choice.

### Selection

`AZURE_MODEL_DEPLOYMENT_PROFILE` selects the profile. The first preprovision hook
(`scripts/check-model-quota.py`) resolves `auto` to a concrete value by querying
`az cognitiveservices usage list` and picking the largest profile that fits, then
writing the result via `azd env set` before Bicep runs.

When no explicit profile is set, the script applies a mode-appropriate default: `default`
(50 K TPM) when `AZURE_INDIVIDUAL_MODE=true` (single learner), and `workshop` (200 K TPM)
for organizer deployments. An explicit `AZURE_MODEL_DEPLOYMENT_PROFILE` always overrides both.

### Quota preflight

The script validates model availability (`az cognitiveservices model list`) and quota
(`az cognitiveservices usage list`, matched by `OpenAI.<sku>.<model>`) for each deployment
in the selected profile. On shortfall it prints a required-vs-available table, recommends
the largest fitting profile, suggests an alternate region, and exits non-zero to block
`azd provision`. Set `AZURE_MODEL_QUOTA_CHECK=false` to skip.

## Hosted agents and the container registry

Some modules deploy a **hosted agent** - attendee container code that Foundry runs as a managed endpoint. Provisioning adds one shared **Azure Container Registry (ACR)** and the role assignments hosted agents need, so attendees can complete the module without any manual setup.

### What gets deployed

* A single Azure Container Registry shared by all attendees, with a `ContainerRegistry` connection on the Foundry account. The SKU defaults to `Basic` (override with `AZURE_CONTAINER_REGISTRY_SKU`).
* Each attendee project's managed identity receives **AcrPull** so Foundry can pull the agent image.
* Each attendee receives **AcrPush** on the registry so the Part 1 container path can push an image.
* Each attendee receives a **constrained Role Based Access Control Administrator** role on the Foundry account, conditioned so they can assign **only** the **Foundry User** role and **only** to service principals.

### Why the constrained RBAC Administrator role

Every hosted agent gets its own Microsoft Entra agent identity at deploy time, and that identity needs the **Foundry User** role on the Foundry account to call models at runtime. The identity does not exist until the agent version is created, so the role cannot be pre-assigned in Bicep - the attendee's deploy script assigns it. The constrained Role Based Access Control Administrator role (ABAC-conditioned) lets attendees make exactly that one assignment and nothing else, keeping the grant within least privilege.

### Avoiding attendee collisions

All attendees share one registry. The Part 1 deploy script tags each image with the attendee's project name (`acl-remedy-advisor-hosted-container:<project>`), and every hosted agent is scoped to its own project, so attendees never overwrite each other's images or agents.

### Customise the registry SKU

```bash
# Default is Basic; Standard or Premium raise throughput and storage limits
azd env set AZURE_CONTAINER_REGISTRY_SKU Standard
```
