# Organizer Quickstart

Use this quickstart when you provision one shared Microsoft Foundry environment for many
attendees. It is the high-level flow; see the [Organizer Guide](./guide-organizer.md) for
detailed steps, the RBAC model, and troubleshooting.

## Who does what

| Role | Responsibility |
|------|----------------|
| Organizer | Deploys infrastructure, assigns attendee access, shares project assignments, tears down. |
| Facilitator | Delivers the labs and sets pacing. See the [Facilitator Quickstart](./quickstart-facilitator.md). |
| Proctor | Floor support during delivery. See the [Proctor Guide](./guide-proctor.md). |
| Attendee | Runs the labs. See the [Attendee Quickstart](./quickstart-attendee.md). |

## Before the workshop

1. Clone this repository to your machine.

   ```bash
   git clone https://github.com/PlagueHO/foundry-agentic-workshop.git
   cd foundry-agentic-workshop
   ```

1. Confirm an Azure subscription where you hold **Owner or Contributor** to create resources
   and **Owner or User Access Administrator** to assign roles, with sufficient
   [Foundry model quota](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/quotas-limits)
   in your target region.
1. Install [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
   and [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).
1. Install [Python 3.13 or later](https://www.python.org/downloads/) (used by the pre-provision hook to
   resolve attendee UPNs to Microsoft Entra object IDs).
1. Install and start [Docker](https://www.docker.com/) (used to build and publish the shared MCP server
   image to Azure Container Apps; only required when `AZURE_CONTAINER_APPS_DEPLOY` is `true`, the default).
1. Collect the Microsoft Entra ID UPN for each attendee, organizer, facilitator, and proctor.
1. Decide the default Foundry role for attendees (see [Attendee access](#attendee-access)).

## Deploy

1. Sign in.

   ```bash
   az login
   azd auth login
   ```

1. Create an environment and set core variables.

   ```bash
   azd env new hol-shared
   azd env set AZURE_LOCATION australiaeast
   azd env set AZURE_RESOURCE_GROUP rg-foundry-hol-shared
   ```

1. Configure [attendee access](#attendee-access).

1. Provision.

   ```bash
   azd provision
   ```

## Attendee access

`AZURE_ATTENDEE_LIST` drives per-attendee project creation and UPN resolution. Set it as a single-line JSON array, then provision. The pre-provision hook resolves UPNs to Entra object IDs; Bicep assigns roles at deploy time.

```bash
azd env set AZURE_ATTENDEE_DEFAULT_ROLE foundry-project-manager
azd env set AZURE_ATTENDEE_LIST '[{"upn":"ana@contoso.com"},{"upn":"ben@contoso.com","role":"foundry-project-manager"}]'
```

| Role key | Capability | Scope |
|----------|------------|-------|
| `foundry-user` | Build agents, create connections, and use deployed models. Least privilege. Cannot complete Module 07 (Foundry IQ) or Module 12 (Publishing Agents). | Project |
| `foundry-project-manager` | Create Foundry IQ knowledge bases, publish agents, plus everything above. **Recommended default for lab deployments.** | Account |
| `foundry-account-owner` | Deploy models plus everything above. | Account |
| `foundry-owner` | Full build and manage. | Account |

Attendees cannot deploy models with either default role; you pre-deploy models during
provisioning. The [Organizer Guide](./guide-organizer.md#provisioning-audit) explains the
full role model and the provisioning audit CSVs.

## Share assignments

After provisioning, share the portal URL with attendees.

```bash
azd env get-value ATTENDEE_PORTAL_URL
```

Attendees visit the portal, sign in with their lab Microsoft account, and immediately see
their personal onboarding page. The page includes:

- **Your environment variables** — all `.env` values in a copyable code block, plus a **Download .env** button to save the file directly.
- **Sign in to Azure** — `az login` and `az account set` commands pre-populated with the subscription ID.
- **Validate setup** — the `python scripts/health-check.py` command ready to copy.
- **Next steps** and **Workshop Resources** — links to the Attendee Quickstart, lab modules, and Microsoft Foundry documentation.
- A role badge showing the attendee's assigned Foundry role.
- A **Sign out** button.

Per-attendee markdown files are also written locally to `.azure/<env>/<upn_local>.md` and
uploaded as backup blobs to the root of the `attendee-onboarding` Storage container.
Use them for offline distribution or if the portal is unavailable.

> [!TIP]
> If an attendee sees "No configuration found", the `index.json` blob may not have been
> uploaded yet. Re-run `azd provision` or run `python scripts/generate-attendee-onboarding.py`
> manually with the required environment variables set.

Refer attendees to the [Attendee Quickstart](./quickstart-attendee.md) for setup instructions.

## Teardown

```bash
azd down --force --purge
```
