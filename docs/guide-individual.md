# Individual Guide

Individual mode lets a solo learner provision and run the entire workshop without an attendee
list or an organizer handoff. Set `AZURE_INDIVIDUAL_MODE=true` and run `azd provision` —
your own identity becomes the sole attendee.

The Attendee Onboarding Portal is deployed and the onboarding index is uploaded to blob
storage, the same as in workshop mode. As a solo learner you do not need to use the portal;
your environment configuration is written directly to `shared/.env`.

For the abbreviated flow, see the [Individual Quickstart](./quickstart-individual.md).

## Prerequisites

| Prerequisite | Notes |
|---|---|
| Azure subscription | **Owner or Contributor** to create resources; **Owner or User Access Administrator** to assign roles |
| Foundry model quota | Check [quota limits](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/quotas-limits) for your target region |
| [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd) | v1.11 or later |
| [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) | v2.60 or later |
| [Python 3.13](https://www.python.org/downloads/) | Used by the provision hooks |
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Required for MCP server image builds (skip by setting `AZURE_CONTAINER_APPS_DEPLOY=false`) |

## Set up the environment

1. Clone the repository.

   ```bash
   git clone https://github.com/PlagueHO/foundry-agentic-workshop.git
   cd foundry-agentic-workshop
   ```

1. Install Python dependencies.

   ```bash
   pip install -r shared/requirements.txt
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
| Pre-provision (`prepare-attendee-roles.py`) | Reads your signed-in UPN from `az account show`, derives the project name, and writes `AZURE_ATTENDEE_LIST_RESOLVED`. |
| Post-provision (`generate-attendee-onboarding.py`) | Generates the onboarding index, uploads it to Azure Blob Storage, and writes `shared/.env`. |
| Post-provision (`deploy-attendee-portal.py`) | Runs normally: builds and pushes the portal image, configures EasyAuth. |

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
   python scripts/health-check.py
   ```

1. Open the [Microsoft Foundry portal](https://ai.azure.com) and confirm your project appears.

1. Begin the labs. Start with
   [Lab 01 – Setup](./lab-steps/introduction-foundry-agent-service/01-setup.md).

## What is not available in individual mode

Individual mode is designed for solo learning. The following features are not available.

| Feature | Reason |
|---|---|
| Multiple projects | One project is provisioned for your own identity |

The Attendee Onboarding Portal and Azure Blob Storage upload run the same as in workshop mode.
You do not need to use the portal — `shared/.env` is your primary configuration artefact.

To switch to multi-attendee mode, clear `AZURE_INDIVIDUAL_MODE` and provide an
`AZURE_ATTENDEE_LIST`:

```bash
azd env set AZURE_INDIVIDUAL_MODE false
```

## Tear down

Remove all provisioned resources when you are done.

```bash
azd down --force --purge
```
