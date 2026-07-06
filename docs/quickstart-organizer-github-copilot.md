## Overview

This quickstart shows how to use the `provision-foundry-workshop` skill with GitHub Copilot to stand up and validate a shared Foundry workshop environment in a single conversational step. The skill handles configuration, attendee validation, provisioning, and post-provision verification automatically.

For the manual equivalent, see the [Organizer Quickstart](./quickstart-organizer.md) and the [Organizer Guide](./guide-organizer.md).

## Who does what

| Role | Responsibility |
|------|----------------|
| Organizer | Runs this quickstart to provision infrastructure and assign attendee access. |
| Facilitator | Delivers the labs and distributes onboarding files. See the [Facilitator Quickstart](./quickstart-facilitator.md). |
| Proctor | Floor support during delivery. See the [Proctor Guide](./guide-proctor.md). |
| Attendee | Runs the labs. See the [Attendee Quickstart](./quickstart-attendee.md). |

## Prerequisites

1. Clone this repository.

   ```bash
   git clone https://github.com/PlagueHO/foundry-agentic-workshop.git
   cd foundry-agentic-workshop
   ```

1. Install [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
   and [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).

1. Sign in to both CLIs against the subscription where you hold Owner or
   User Access Administrator rights.

   ```bash
   az login
   azd auth login
   ```

1. Install one of the following:
   * [VS Code Insiders](https://code.visualstudio.com/insiders/) with the GitHub Copilot extension and **Agent Mode** enabled.
   * [GitHub Copilot CLI](https://githubnext.com/projects/copilot-cli) (`gh copilot`).

1. Collect the Microsoft Entra UPNs (email addresses) for all attendees,
   facilitators, proctors, and organizers you want to provision access for.

## Prepare your parameters

Before invoking the skill, gather the values below. The skill will ask for any that you do not supply.

| Parameter | Description | Example |
|-----------|-------------|---------|
| `env` | azd environment name | `my-workshop` |
| `location` | Azure region slug | `australiaeast` |
| `rg` | Resource group name | `rg-my-workshop` |
| `default-role` | Default role for attendees (optional, defaults to `foundry-user`) | `foundry-user` |
| `attendees` | JSON array of attendee objects - see [Attendee list format](#attendee-list-format) | See below |

### Attendee list format

Build a JSON array with one object per person. Standard attendees need only their UPN; staff members require an explicit `role`:

```json
[
  {"upn": "alice@contoso.com"},
  {"upn": "bob@contoso.com"},
  {"upn": "carol@contoso.com"},
  {"upn": "facilitator@contoso.com", "role": "facilitator"},
  {"upn": "proctor@contoso.com",     "role": "proctor"},
  {"upn": "organizer@contoso.com",   "role": "organizer"}
]
```

**Role keys**

| Key | Foundry role | Scope | Typical use |
|-----|-------------|-------|-------------|
| `foundry-user` | Foundry User | Project | Standard attendees (default, least privilege) |
| `foundry-project-manager` | Foundry Project Manager | Account | Attendees who need to publish agents |
| `foundry-account-owner` | Foundry Account Owner | Account | Attendees who need to deploy models |
| `foundry-owner` | Foundry Owner | Account | Full access |
| `facilitator` | Foundry Owner | Account | Workshop facilitators |
| `proctor` | Foundry Owner | Account | Floor proctors |
| `organizer` | Foundry Owner | Account | Organizers and admins |

The skill validates that every `upn` is a correctly formed email address and that every `role` is one of the keys above before starting any Azure operations.

## Run the skill

### VS Code Insiders (Agent Mode)

Open the repository folder in VS Code Insiders, open the Copilot chat panel, and switch to **Agent Mode**. Then send a message in either style below.

**With all parameters supplied:**

```text
Provision the Foundry workshop

env: my-workshop
location: australiaeast
rg: rg-my-workshop
default-role: foundry-user
attendees:
[
  {"upn": "alice@contoso.com"},
  {"upn": "bob@contoso.com"},
  {"upn": "facilitator@contoso.com", "role": "facilitator"}
]
```

**Letting the skill ask interactively:**

```text
Provision the Foundry workshop
```

The skill will ask for each missing parameter - including a guided prompt for the attendee list - before starting any Azure operations.

### GitHub Copilot CLI

```bash
gh copilot suggest "Provision the Foundry workshop with env=my-workshop location=australiaeast rg=rg-my-workshop"
```

## What the skill does

The skill executes these steps automatically:

1. **Collects** any missing parameters via interactive prompts.
1. **Validates** the attendee list - JSON structure, UPN format, valid role keys, no duplicates.
1. **Confirms** the validated roster with you before making any changes.
1. **Configures** the azd environment with all required variables.
1. **Provisions** with `azd provision`, which:
   * Runs the **model-quota preflight** — validates model availability and quota for the selected
     profile (`AZURE_MODEL_DEPLOYMENT_PROFILE`, default `default`) and blocks with copy-paste
     remediation on shortfall. Skip with `AZURE_MODEL_QUOTA_CHECK=false` if needed.
   * Resolves each UPN to a Microsoft Entra object ID.
   * Deploys the Foundry account, per-attendee projects, and RBAC role assignments.
   * Seeds the Azure AI Search indexes with lab data.
1. **Verifies**:
   * UPN resolution audit CSV at `.azure/<env>/attendee-resolution-<env>-<timestamp>.csv`
   * RBAC provisioning summary CSV at `.azure/<env>/attendee-provisioning-<env>-<timestamp>.csv`
   * Per-attendee onboarding files at `.azure/<env>/<upn_local>.md`
   * AI Search index population via `scripts/health-check.py`
1. **Reports** a summary showing counts of successes and any failures.

## After provisioning

Hand the per-attendee onboarding files to the facilitator for distribution. Each attendee's file is at `.azure/<env>/<upn_local>.md` and contains their `FOUNDRY_PROJECT_NAME`, connection values, and setup commands.

```bash
azd env get-value AZURE_ATTENDEE_PROJECT_NAMES
```

It is the **facilitator's responsibility** to deliver each attendee's file before the workshop starts. Refer attendees to the [Attendee Quickstart](./quickstart-attendee.md).

## Teardown

```bash
azd down --force --purge
```
