# Individual Quickstart

Use this quickstart when you want to run the workshop labs on your own - no team, no attendee
list, and no shared provisioning. Individual mode (`AZURE_INDIVIDUAL_MODE=true`) provisions
a single Foundry project scoped to your own Azure identity, and writes your `.env`
configuration to `.env` automatically after provisioning.

See the [Individual Guide](./guide-individual.md) for detailed steps and troubleshooting.

## Prerequisites

- Azure subscription with [Foundry model quota](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/quotas-limits)
  in your target region, and **Owner or Contributor** rights to create resources and assign roles.
  With `AZURE_INDIVIDUAL_MODE=true` the preprovision quota check automatically selects the `default`
  profile (50 K TPM), which fits most subscriptions. Use `AZURE_MODEL_DEPLOYMENT_PROFILE=minimal`
  for lower-quota environments.
- [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Python 3.13 or later](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (required to build
  and publish the shared MCP server images; only needed when `AZURE_CONTAINER_APPS_DEPLOY=true`,
  which is the default)

## Provision the Lab Environment

1. Clone this repository.

   ```bash
   git clone https://github.com/PlagueHO/foundry-agentic-workshop.git
   cd foundry-agentic-workshop
   ```

1. Sign in.

   ```bash
   az login
   ```

1. 🆕 Run the setup wizard (recommended). It prompts for your environment name, location, and resource group,
   enables individual mode, and runs `azd provision`.

   ```bash
   uv run python scripts/configure-workshop.py
   ```

   See the [Individual Guide](./guide-individual.md) for details and a screenshot.

<details>
<summary>Manual setup (alternative to the wizard)</summary>

```bash
azd env new my-foundry-lab
azd env set AZURE_LOCATION australiaeast
azd env set AZURE_RESOURCE_GROUP rg-foundry-lab
azd env set AZURE_INDIVIDUAL_MODE true
azd provision
```

</details>

## After provisioning

1. Review `.env` - your environment configuration is ready to use.

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
