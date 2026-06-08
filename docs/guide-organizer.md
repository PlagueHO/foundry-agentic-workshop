# Organizer Guide

This guide covers standing up and tearing down a shared Microsoft Foundry workshop environment: infrastructure deployment, per-attendee access, validation, and cleanup. For the condensed checklist, see the [Organizer Quickstart](./quickstart-organizer.md).

## Prerequisites

1. An Azure subscription to use to host the laboratory infrastructure where you have permission to create resources and assign roles.
   1. To create resources requires requires Owner or Contributor role on the subscription or resource group.
   1. To assign roles requires Owner or User Access Administrator on the subscription or resource group.
1. [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd).
1. [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).
1. Python 3.13 or later (the post-provision role assignment runs as a Python hook).
1. [Foundry Model quota](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/quotas-limits) in your target region for the models the labs use.
1. The Microsoft Entra ID UPN for each attendee, organizer, facilitator and proctor. The organizer, facilitator and proctors are optional.

## Typical workshop setup

This section walks through the most common scenario: a handful of standard attendees and one facilitator. The whole flow takes about five minutes. A single command - `azd provision` - deploys the Azure resources and assigns all roles; re-run it any time the roster changes.

### 1. Clone the repository

```bash
git clone https://github.com/PlagueHO/foundry-agentic-workshop.git
cd foundry-agentic-workshop
```

### 2. Sign in

Authenticate both CLIs against the subscription where you hold Owner or User Access
Administrator rights.

```bash
az login
azd auth login
```

### 3. Create an environment

Create an isolated azd environment to hold your workshop configuration. This also sets the
Azure region and resource group.

```bash
azd env new my-workshop
azd env set AZURE_LOCATION australiaeast
azd env set AZURE_RESOURCE_GROUP rg-my-workshop
```

### 4. Set your attendee list

`AZURE_ATTENDEE_LIST` is the single configuration variable that drives both project creation and role assignment. Set it to a single-line JSON array of attendees before provisioning.

The example below registers five standard attendees and one facilitator. By default, each attendee's project is named after the local part of their UPN (for example `alice`, `bob`, and `facilitator`); see the tip below if you prefer sequential names such as `attendee-01`.

```bash
azd env set AZURE_ATTENDEE_LIST '[{"upn":"alice@contoso.com"},{"upn":"bob@contoso.com"},{"upn":"carol@contoso.com"},{"upn":"david@contoso.com"},{"upn":"eve@contoso.com"},{"upn":"facilitator@contoso.com","role":"facilitator"}]'
```

The default role for entries without an explicit `role` is `foundry-user`, the least-privilege role for attendees. The `facilitator` role grants full account-level access.

> [!TIP]
> Store the formatted version in a local file for readability and paste the single-line form into `azd env set`. See [Scenario examples](#scenario-examples) for more roster patterns.

> [!TIP]
> By default, each attendee's Foundry project is named from the local part of their UPN — for example `alice.smith@contoso.com` becomes `alice-smith`. Dots and underscores are replaced with hyphens and the name is lowercased and capped at 32 characters. Set `AZURE_USE_UPN_PROJECT_NAMES=false` to revert to sequential `<prefix>-NN` names (for example `attendee-01`).

### 5. Provision

```bash
azd provision
```

This deploys all Azure resources, runs the post-provision hook to assign roles, and seeds the Azure AI Search indexes. Re-run this command any time you change `AZURE_ATTENDEE_LIST`, `AZURE_ATTENDEE_COUNT`, or the project prefix.

> [!NOTE]
> Screenshot placeholder- *the Foundry account and its projects in the Azure portal after provisioning.* Alt text: "Azure portal resource group showing the Foundry account and one project per attendee."

## Validate and share

After provisioning, confirm the environment is healthy and share connection details with
attendees.

### Confirm projects

```bash
azd env get-value AZURE_ATTENDEE_PROJECT_NAMES
```

Open the [Foundry portal](https://ai.azure.com) and confirm the projects and model deployments exist. Optionally sign in as a test attendee to verify the expected capabilities.

> [!NOTE]
> Screenshot placeholder- *the project list in the Foundry portal.* Alt text: "Microsoft Foundry portal showing one project per attendee."

### Share with attendees

Give each attendee:

* Their `FOUNDRY_PROJECT_NAME` (for example `attendee-01`).
* The shared connection values for `.env`: `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `FOUNDRY_RESOURCE_NAME`, and `AZURE_SEARCH_SERVICE_NAME`.

Refer them to the [Attendee Quickstart](./quickstart-attendee.md) for setup instructions.

---

## Attendee list reference

`AZURE_ATTENDEE_LIST` is a single-line JSON array persisted by `azd env set` and read by
both the Bicep deployment (project creation) and the post-provision hook (role assignment). Set it before provisioning; both consumers derive project names and role scopes from the same value.

The full JSON schema is at `shared/schemas/attendee-list.schema.json`.

### Fields

| Field | Required | Default | Purpose |
|-------|----------|---------|---------|
| `upn` | Yes |- | Microsoft Entra UPN; resolved to an object ID at provisioning time. |
| `role` | No | `AZURE_ATTENDEE_DEFAULT_ROLE` | Role key- see [Role catalog](#role-catalog). |
| `individualProject` | No | `true` | `true` = dedicated project; `false` = shares the first project in the list. |
| `projectName` | No | UPN local part or `<prefix>-NN` | Explicit project name (lowercase alphanumeric, hyphens, 2–64 chars). Takes priority over `AZURE_USE_UPN_PROJECT_NAMES`. |

### Scenario examples

**Anonymous projects- headcount only**

Use this when you have a seat count but no UPN list yet. Creates five blank projects with no role assignments. Switch to a named list once UPNs are available.

```bash
azd env set AZURE_ATTENDEE_COUNT 5
```

When `AZURE_ATTENDEE_LIST` is also set, it always takes precedence. Unset it first if you
want to switch back to the anonymous count mode.

---

**Standard attendees**

All attendees receive `foundry-user` (least privilege) and a dedicated `attendee-NN` project.

```json
[
  {"upn":"alice@contoso.com"},
  {"upn":"bob@contoso.com"},
  {"upn":"carol@contoso.com"}
]
```

```bash
azd env set AZURE_ATTENDEE_LIST '[{"upn":"alice@contoso.com"},{"upn":"bob@contoso.com"},{"upn":"carol@contoso.com"}]'
```

---

**Standard attendees with a facilitator**

The facilitator gets `Foundry Owner` at account scope and a `facilitator-01` project. Standard attendees are unaffected.

```json
[
  {"upn":"alice@contoso.com"},
  {"upn":"bob@contoso.com"},
  {"upn":"carol@contoso.com"},
  {"upn":"facilitator@contoso.com","role":"facilitator"}
]
```

---

**Workshop staff- facilitator, proctor, organizer**

Each staff role receives a project under its own prefix. Attendees and staff are numbered
independently, so `attendee-01`, `facilitator-01`, and `proctor-01` are distinct projects.

```json
[
  {"upn":"alice@contoso.com"},
  {"upn":"bob@contoso.com"},
  {"upn":"facilitator@contoso.com","role":"facilitator"},
  {"upn":"proctor@contoso.com","role":"proctor"},
  {"upn":"organizer@contoso.com","role":"organizer"}
]
```

---

**Mixed privilege levels**

Give specific attendees elevated roles while keeping everyone else on `foundry-user`.

```json
[
  {"upn":"alice@contoso.com"},
  {"upn":"bob@contoso.com","role":"foundry-project-manager"},
  {"upn":"carol@contoso.com","role":"foundry-account-owner"}
]
```

---

**Team projects**

Multiple attendees share a project by specifying the same `projectName`. Duplicates are
removed so only one project is created per unique name.

```json
[
  {"upn":"alice@contoso.com","projectName":"team-red"},
  {"upn":"bob@contoso.com","projectName":"team-red"},
  {"upn":"carol@contoso.com","projectName":"team-blue"},
  {"upn":"david@contoso.com","projectName":"team-blue"}
]
```

---

**Updating an existing roster**

Update `AZURE_ATTENDEE_LIST` and re-run `azd provision`. Existing projects are preserved;
new entries get projects and role assignments; role changes are applied.

```json
[
  {"upn":"alice@contoso.com","role":"foundry-project-manager"},
  {"upn":"bob@contoso.com"},
  {"upn":"new-attendee@contoso.com"}
]
```

### Validate before provisioning

Use `check-jsonschema` to catch typos and invalid role keys before provisioning:

```bash
pip install check-jsonschema
azd env get-value AZURE_ATTENDEE_LIST > /tmp/attendee-list.json
check-jsonschema --schemafile shared/schemas/attendee-list.schema.json /tmp/attendee-list.json
```

## Role catalog

Role keys map to Foundry built-in roles. See [Role-based access control for Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/concepts/rbac-foundry).

| Role key | Foundry role | Scope | Can | Cannot |
|----------|--------------|-------|-----|--------|
| `foundry-user` | Foundry User | Project | Build agents, create connections, use deployed models, Foundry IQ, and toolboxes. | Deploy models, publish agents. |
| `foundry-project-manager` | Foundry Project Manager | Account | Everything above plus publish agents. | Deploy models. |
| `foundry-account-owner` | Foundry Account Owner | Account | Everything above plus deploy models. |- |
| `foundry-owner` | Foundry Owner | Account | Full build and manage. |- |
| `facilitator` | Foundry Owner | Account | Full access under the facilitator project prefix. |- |
| `proctor` | Foundry Owner | Account | Full access under the proctor project prefix. |- |
| `organizer` | Foundry Owner | Account | Full access under the organizer project prefix. |- |

`foundry-user` is the default and is least privilege. Because the organizer pre-deploys models during provisioning, attendees do not need to deploy models themselves. Elevate roles only when a specific lab requires it.

```bash
# Elevate everyone to deploy models
azd env set AZURE_ATTENDEE_DEFAULT_ROLE foundry-account-owner

# Or elevate individual attendees
azd env set AZURE_ATTENDEE_LIST '[{"upn":"alice@contoso.com","role":"foundry-account-owner"},{"upn":"bob@contoso.com"}]'
```

### Staff project prefixes

Staff roles use their own prefix and are numbered independently of standard attendees. A `facilitator-01` project is always provisioned by default even when no facilitator appears in `AZURE_ATTENDEE_LIST` (controlled by `AZURE_ENSURE_FACILITATOR_PROJECT`).

| Role | Default prefix | Env var | Example project |
|------|---------------|---------|-----------------|
| Standard attendee | `attendee` | `AZURE_ATTENDEE_PROJECT_PREFIX` | `attendee-01` |
| `facilitator` | `facilitator` | `AZURE_FACILITATOR_PROJECT_PREFIX` | `facilitator-01` |
| `proctor` | `proctor` | `AZURE_PROCTOR_PROJECT_PREFIX` | `proctor-01` |
| `organizer` | `organizer` | `AZURE_ORGANIZER_PROJECT_PREFIX` | `organizer-01` |

Override any prefix with `azd env set <VAR> <value>` before provisioning.

## Provisioning audit

After role assignment, the hook writes a CSV audit file and prints a console summary.

File: `./.azure/attendee-provisioning-<env>-<timestamp>.csv`

| Column | Meaning |
|--------|---------|
| `upn` | Attendee UPN. |
| `object_id` | Resolved Microsoft Entra object ID. |
| `role_key` | Role key requested. |
| `role_display_name` | Foundry role display name. |
| `role_definition_id` | Azure role definition GUID. |
| `project_name` | Target project, or empty for account-scoped roles. |
| `scope` | `project` or `account`. |
| `status` | `succeeded` or `failed`. |
| `message` | Failure detail when status is `failed`. |

Review failed rows before the workshop starts. The most common cause is a UPN that does not resolve to an object ID (typo or guest account not in the tenant).

## Teardown

```bash
azd down --force --purge
```

This removes the resource group and purges soft-deleted Foundry and Key Vault resources so
the names are immediately reusable.
