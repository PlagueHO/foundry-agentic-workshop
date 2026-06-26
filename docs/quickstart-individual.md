# Individual Quickstart

Use this quickstart when you want to run the workshop labs on your own — no team, no attendee
list, and no shared provisioning. Individual mode (`AZURE_INDIVIDUAL_MODE=true`) provisions
a single Foundry project scoped to your own Azure identity, and writes your `.env`
configuration to `.env` automatically after provisioning.

See the [Individual Guide](./guide-individual.md) for detailed steps and troubleshooting.

## Prerequisites

- Azure subscription with [Foundry model quota](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/quotas-limits)
  in your target region, and **Owner or Contributor** rights to create resources and assign roles
- [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Python 3.13 or later](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (required to build
  and publish the shared MCP server images; only needed when `AZURE_CONTAINER_APPS_DEPLOY=true`,
  which is the default)

## Deploy

1. Clone this repository.

   ```bash
   git clone https://github.com/PlagueHO/foundry-agentic-workshop.git
   cd foundry-agentic-workshop
   ```

1. Sign in.

   ```bash
   az login
   azd auth login
   ```

1. Create an environment and set core variables.

   ```bash
   azd env new my-foundry-lab
   azd env set AZURE_LOCATION australiaeast
   azd env set AZURE_RESOURCE_GROUP rg-foundry-lab
   ```

1. Enable individual mode.

   ```bash
   azd env set AZURE_INDIVIDUAL_MODE true
   ```

1. Provision.

   ```bash
   azd provision
   ```

## After provisioning

1. Review `.env` — your environment configuration is ready to use.

1. Validate your setup.

   ```bash
   python scripts/health-check.py
   ```

1. Open the [Microsoft Foundry portal](https://ai.azure.com) and confirm your project appears.

1. Begin the labs. Start with
   [Lab 01 – Setup](./lab-steps/introduction-foundry-agent-service/01-setup.md).

## Tear down

Remove all provisioned resources when you are done.

```bash
azd down --force --purge
```
