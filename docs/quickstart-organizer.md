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

1. Confirm an Azure subscription with sufficient model quota in your target region.
1. Install [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
   and [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).
1. Collect the attendee user principal names (UPNs) you will grant access to.
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
   azd env set AZURE_ATTENDEE_PROJECT_PREFIX attendee
   ```

1. Configure [attendee access](#attendee-access).

1. Provision.

   ```bash
   azd provision
   ```

## Attendee access

`AZURE_ATTENDEE_LIST` is the single source of truth for both per-attendee project creation
and role assignment. Set it as a single-line JSON array, then provision.

```bash
azd env set AZURE_ATTENDEE_DEFAULT_ROLE foundry-user
azd env set AZURE_ATTENDEE_LIST '[{"upn":"ana@contoso.com"},{"upn":"ben@contoso.com","role":"foundry-project-manager"}]'
```

| Role key | Capability | Scope |
|----------|------------|-------|
| `foundry-user` | Build agents, create connections, and use deployed models. Default, least privilege. | Project |
| `foundry-project-manager` | Publish agents, plus everything above. | Account |
| `foundry-account-owner` | Deploy models plus everything above. | Account |
| `foundry-owner` | Full build and manage. | Account |

Attendees cannot deploy models with the default role; you pre-deploy models during
provisioning. The [Organizer Guide](./guide-organizer.md#per-attendee-rbac) explains the
full model and the provisioning audit CSV.

## Share assignments

```bash
azd env get-value AZURE_ATTENDEE_PROJECT_NAMES
```

Give each attendee their assigned `FOUNDRY_PROJECT_NAME` (by default the local part of
their UPN, for example `alice-smith` from `alice.smith@contoso.com`; set
`AZURE_USE_UPN_PROJECT_NAMES=false` to use sequential `<prefix>-NN` names) and the shared
resource values they need for the [Attendee Quickstart](./quickstart-attendee.md).

## Teardown

```bash
azd down --force --purge
```
