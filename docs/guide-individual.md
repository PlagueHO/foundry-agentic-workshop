# Individual Guide

Individual mode lets a solo learner provision and run the entire workshop without an attendee
list or an organizer handoff. Set `AZURE_INDIVIDUAL_MODE=true` and run `azd provision` -
your own identity becomes the sole attendee.

For the abbreviated flow, see the [Individual Quickstart](./quickstart-individual.md).

## Prerequisites

| Prerequisite | Notes |
|---|---|
| Azure subscription | **Owner or Contributor** to create resources; **Owner or User Access Administrator** to assign roles |
| Foundry model quota | Check [quota limits](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/quotas-limits) for your target region. When `AZURE_INDIVIDUAL_MODE=true`, the preprovision quota check defaults to the `default` profile (50 K TPM per model), which fits most subscriptions. Use `AZURE_MODEL_DEPLOYMENT_PROFILE=minimal` for lower-quota environments. |
| [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd) | v1.11 or later |
| [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) | v2.60 or later |
| [Python 3.13](https://www.python.org/downloads/) | Used by the provision hooks |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | Python package manager; all scripts and provision hooks run via `uv run` |
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Required for MCP server image builds (skip by setting `AZURE_CONTAINER_APPS_DEPLOY=false`) |

## Set up the environment

1. Clone the repository.

   ```bash
   git clone https://github.com/PlagueHO/foundry-agentic-workshop.git
   cd foundry-agentic-workshop
   ```

1. Install Python dependencies.

   ```bash
   uv sync
   ```

1. Sign in to Azure.

   ```bash
   az login
   azd auth login
   ```

1. Create the azd environment and configure variables.

   ```bash
   azd env new my-foundry-lab
   azd env set AZURE_LOCATION australiaeast
   azd env set AZURE_RESOURCE_GROUP rg-foundry-lab
   azd env set AZURE_INDIVIDUAL_MODE true
   ```

   Replace `australiaeast` with a region that has sufficient Foundry model quota, and choose a
   resource group name that is unique in your subscription.

## Provision

Run `azd provision`. The provision hooks run automatically.

| Hook | What happens in individual mode |
|---|---|
| Pre-provision (`prepare-attendee-roles.py`) | Reads your signed-in UPN from `az account show` and derives the Foundry project name. |
| Post-provision (`generate-attendee-onboarding.py`) | Writes your environment configuration to `.env`. |

```bash
azd provision
```

## Project naming

Your Foundry project name is derived from your signed-in UPN local part (the text before `@`),
with `.` and `_` replaced by `-`, lowercased, and truncated to 32 characters.

For example: `jane.doe@contoso.com` → `jane-doe`

If the UPN cannot be retrieved, the project name falls back to `attendee-01`.

## After provisioning

1. Review `.env`. This file is overwritten each time you re-provision.

1. Validate your setup.

   ```bash
   uv run python scripts/health-check.py
   ```

1. Open the [Microsoft Foundry portal](https://ai.azure.com) and confirm your project appears.

1. Begin the labs. Start with
   [Lab 01 – Setup](./lab-steps/introduction-foundry-agent-service/01-setup.md).

## Tear down

Remove all provisioned resources when you are done.

```bash
azd down --force --purge
```
