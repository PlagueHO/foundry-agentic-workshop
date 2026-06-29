![Microsoft Foundry Agentic Workshop - Hands-on-labs](./docs/assets/banners/microsoft-foundry-agentic-workshop.png)

# Microsoft Foundry Agentic Workshop

This repository contains **L200–L400 hands-on labs** for building agentic solutions on [Microsoft Foundry](https://learn.microsoft.com/azure/ai-foundry/what-is-foundry) using [Microsoft Foundry Agent Service](https://learn.microsoft.com/azure/ai-foundry/agents/overview), [Foundry IQ](https://learn.microsoft.com/azure/ai-foundry/foundry-iq/overview), and the [Microsoft Agent Framework](https://learn.microsoft.com/azure/ai-foundry/agents/agent-framework).

## Link to Workshop

[Foundry Agentic Workshop](https://danielscottraynsford.com/foundry-agentic-workshop/) *(Maintained by [@PlagueHO](https://github.com/PlagueHO) - not an official Microsoft resource)*

The workshop guide walks through all L200–L400 labs in this repository, providing facilitator notes, attendee instructions, and lab-by-lab objectives. Use it as your primary reference when delivering or completing the workshop.

## Who is this for

- Software engineers, architects, and technical roles building or designing AI solutions in Azure
- Comfortable with Azure basics; mostly new to Microsoft Foundry and agentic development
- Delivered as a facilitator-led session (3–4 hours) or completed independently

## Roles

| Role | Required | Responsible for |
|------|----------|-----------------|
| Organizer | Yes | Provisions the shared Azure environment, assigns project access, shares connection details, tears down after the workshop |
| Attendee | Yes | Completes the labs using the shared environment the organizer provisions |
| Facilitator | No | Delivers the session, owns pacing and the time-box per lab, coordinates with proctors |
| Proctor | No | Provides 1:1 floor support during delivery so the facilitator can keep teaching |

## Quickstarts

Start with the path that matches your role.

| Role | Start with | Then read |
|------|------------|-----------|
| Organizer | [Organizer Quickstart](./docs/quickstart-organizer.md) | [Organizer Guide](./docs/guide-organizer.md) |
| Individual learner | [Individual Quickstart](./docs/quickstart-individual.md) | [Individual Guide](./docs/guide-individual.md) |
| Attendee | [Attendee Quickstart](./docs/quickstart-attendee.md) | [Attendee Guide](./docs/guide-attendee.md) |
| Facilitator | [Facilitator Quickstart](./docs/quickstart-facilitator.md) | [Facilitator Guide](./docs/guide-facilitator.md) |
| Proctor | [Proctor Guide](./docs/guide-proctor.md) | - |

## Organizer: provision the lab environment

The organizer deploys a shared Foundry account in their Azure subscription and creates one dedicated project per attendee. Attendees receive their project name and shared connection values; no Azure work is required on their side.

### Prerequisites

- Azure subscription with [Foundry model quota](https://learn.microsoft.com/azure/foundry/foundry-models/quotas-limits) in your target region
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (required to build and publish the shared MCP server image during provisioning)
- Python 3.13

### Clone this repo

The first step is to clone this repository and navigate into it:

```bash
git clone https://github.com/PlagueHO/foundry-agentic-workshop.git
cd foundry-agentic-workshop
```

### Prepare

Using Azure Developer CLI and Azure CLI, create a new environment and set the required variables. `AZURE_ATTENDEE_LIST` can be set now or later; it's only read during provisioning.

```bash
az login
azd auth login
azd env new my-workshop
azd env set AZURE_LOCATION australiaeast
azd env set AZURE_RESOURCE_GROUP rg-my-workshop
```

### Assign attendees by UPN

To assign attendees to the lab, set `AZURE_ATTENDEE_LIST` before provisioning. Each entry gets a dedicated Foundry project and the specified role. Configure the JSON array as a list of the attendees you want to grant access to, using their user principal names (UPNs). These must all be users in the Entra ID tenant associated with the subscription you're deploying to.

```bash
azd env set AZURE_ATTENDEE_LIST '[{"upn":"alice@contoso.com"},{"upn":"bob@contoso.com"},{"upn":"facilitator@contoso.com","role":"facilitator"}]'
```

> [!NOTE]
> During the provisioning process, the script `scripts/prepare-attendee-roles.py` reads `AZURE_ATTENDEE_LIST`, looks up each user in Entra ID, and assigns them the specified role to the assigned project and Azure AI Search. The default role is `foundry-user`, which allows them to build agents and use pre-deployed models but not manage resources or access other attendees' projects.

### Provision

```bash
azd provision
```

For more details, see the [Organizer Guide](./docs/guide-organizer.md) for role options, team projects, and the full attendee list schema.

### Share with attendees

After provisioning, give each attendee:

- Their `FOUNDRY_PROJECT_NAME` (for example `attendee-01`)
- The shared values: `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `FOUNDRY_RESOURCE_NAME`, `AZURE_SEARCH_SERVICE_NAME`, `RETAIL_REMEDY_OPS_MCP_SERVER_URL`

> [!TIP]
> The `scripts/generate-attendee-onboarding.py` postprovision hook creates a per-attendee `.env` file with all required values pre-filled. Share the generated file instead of copying values manually.

### Cost

Plan for approximately **AUD 50/day** for a sandbox environment, depending on region, SKU, and usage.

### Teardown

```bash
azd down --force --purge
```

Removes the resource group and purges soft-deleted Foundry and Key Vault resources so names are immediately reusable.

## Attendee: set up your environment

Your organizer provisions the Foundry environment before the workshop. You only need a local development environment and the connection values they share with you.

### Option 1: Dev container (recommended)

This repository includes a [dev container](https://containers.dev/) that installs all required tools and VS Code extensions automatically.

1. Open the repository in [VS Code](https://code.visualstudio.com/insiders/) or [GitHub Codespaces](https://github.com/features/codespaces).
1. When prompted, select **Reopen in Container** (VS Code) or wait for the Codespaces environment to build.
1. The container installs Azure CLI, Azure Developer CLI, Python 3.13, Node.js, and all required VS Code extensions including the [Foundry Toolkit](https://marketplace.visualstudio.com/items?itemName=ms-windows-ai-studio.windows-ai-studio).

### Option 2: GitHub Codespaces

1. Click **Code → Codespaces → Create codespace on main** in the GitHub UI.
1. The codespace builds from the dev container configuration - no local install required.
1. Continue from step 3 of the [Attendee Quickstart](./docs/quickstart-attendee.md).

### Option 3: Local machine

Install the following tools manually:

- [VS Code Insiders](https://code.visualstudio.com/insiders/) with the [Foundry Toolkit for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-windows-ai-studio.windows-ai-studio)
- [Python 3.13 or later](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)

Then install the shared Python dependencies:

```bash
uv sync
```

### Configure and validate

1. Copy `shared/.env.example` to `.env` and populate the values your organizer shared.
1. Sign in:

   ```bash
   az login
   az account set --subscription <your-subscription-id>
   ```

1. Validate:

   ```bash
   uv run python scripts/health-check.py
   ```

See the [Attendee Quickstart](./docs/quickstart-attendee.md) for the full flow.

## Available labs

| Lab series | Description |
|------------|-------------|
| [Introduction to Foundry Agent Service](./docs/labs/introduction-foundry-agent-service.md) | Build agents from first principles using Foundry Agent Service, MCP tools, Foundry IQ, the Python Agent Framework, and hosted agents |
| [Introduction to Microsoft Agent Framework (.NET)](./docs/labs/agent-framework-dotnet.md) | Build agentic .NET applications end-to-end using the Microsoft Agent Framework, from a single-turn agent through to a fully hosted, observable multi-agent system |

### Introduction to Foundry Agent Service - modules

| Module | Description | Time |
|--------|-------------|------|
| [01 - Setup](./labs/introduction-foundry-agent-service/01-setup/README.md) | Configure your local environment, sign in to Azure, and verify access to your assigned Foundry project. | 15 min |
| [02 - Foundry portal walkthrough](./labs/introduction-foundry-agent-service/02-foundry-portal-walkthrough/README.md) | Tour the Foundry portal and understand its core capabilities: models, Agent Service, IQ, and tools. | 10 min |
| [03 - Foundry Toolkit for VS Code](./labs/introduction-foundry-agent-service/03-foundry-toolkit-vscode/README.md) | Install and connect the Foundry Toolkit VS Code extension, tour the model catalog, and generate starter code. | 15 min |
| [04 - Prompt-based agents](./labs/introduction-foundry-agent-service/04-prompt-based-agents/README.md) | Create your first Prompt Agent using the Agent Builder and chat with it from Python using `AIProjectClient`. | 20 min |
| [05 - Agent tools and evaluations](./labs/introduction-foundry-agent-service/05-agent-tools-and-evaluations/README.md) | Add Web Search and Code Interpreter built-in tools, then run quality and safety evaluations against the agent. | 30 min |
| [06 - MCP tools](./labs/introduction-foundry-agent-service/06-mcp-tools/README.md) | Integrate a custom MCP server as an agent tool, giving the agent access to a retail operations API. | 30 min |
| [07 - Foundry IQ](./labs/introduction-foundry-agent-service/07-foundry-iq/README.md) | Ground the agent in enterprise content by connecting an Azure AI Search–backed Foundry IQ knowledge base. | 25 min |
| [08 - Agent Framework for Python](./labs/introduction-foundry-agent-service/08-agent-framework-python/README.md) | Run and orchestrate agents using the Microsoft Agent Framework Python SDK against the agents you built. | 25 min |
| [09 - Hosted agents](./labs/introduction-foundry-agent-service/09-hosted-agents/README.md) | Package a code-first Agent Framework agent and deploy it as a fully managed hosted agent on Foundry. | 35 min |
| [10 - Foundry Toolboxes](./labs/introduction-foundry-agent-service/10-foundry-toolboxes/README.md) | Discover and consume curated tool sets via Foundry Toolboxes (preview) through a hosted agent. | 30 min |
| [11 - Agent ops and Agent ID](./labs/introduction-foundry-agent-service/11-agent-ops-and-agent-id/README.md) | Inspect traces, monitor agent operations, and explore Entra Agent Identities and continuous evaluation. | TBD |
| [12 - Publishing agents](./labs/introduction-foundry-agent-service/12-publishing-agents/README.md) | Publish an agent and understand how published agents are consumed. Requires `foundry-project-manager` role. *(Optional)* | 15 min |

### Introduction to Microsoft Agent Framework (.NET) - modules

| Module | Description | Time |
|--------|-------------|------|
| [01 - Setup](./labs/agent-framework-dotnet/01-setup/README.md) | Configure .NET SDK, Python, and dotenv with verified Foundry access. | 15 min |
| [02 - Your First Agent](./labs/agent-framework-dotnet/02-first-agent/README.md) | Create a single-turn `AIAgent` running against your Foundry project with streaming output. | 15 min |
| [03 - Multi-turn & Threads](./labs/agent-framework-dotnet/03-multi-turn/README.md) | Hold multi-turn conversations using `AgentSession`. | 20 min |
| [04 - Function Tools](./labs/agent-framework-dotnet/04-function-tools/README.md) | Extend the agent with flight-lookup and booking C# function tools. | 20 min |
| [05 - MCP Tools](./labs/agent-framework-dotnet/05-mcp-tools/README.md) | Wire a local Python MCP server into the agent via `McpServer`. | 25 min |
| [06 - Knowledge Bases](./labs/agent-framework-dotnet/06-knowledge-bases/README.md) | Ground the agent in passenger-rights documents via `AIContextProvider` and Azure AI Search. | 25 min |
| [07 - Memory & Context](./labs/agent-framework-dotnet/07-memory/README.md) | Surface passenger context automatically in every turn with a custom memory provider. | 20 min |
| [08 - Chat History](./labs/agent-framework-dotnet/08-chat-history/README.md) | Serialise session state to disk and restore it correctly across process restarts. | 20 min |
| [09 - Multi-agent Orchestration](./labs/agent-framework-dotnet/09-multi-agent/README.md) | Compose a concierge agent that orchestrates specialist sub-agents for rebooking, accommodation, and compensation. | 25 min |
| [10 - Hosted Agents](./labs/agent-framework-dotnet/10-hosted-agents/README.md) | Deploy the concierge as a hosted agent on Azure Container Apps. | 30 min |
| [11 - Agent Identity & Auth](./labs/agent-framework-dotnet/11-agent-auth/README.md) | Apply `DefaultAzureCredential` and Entra Agent Identity end-to-end. | 20 min |
| [12 - Observability & Tracing](./labs/agent-framework-dotnet/12-observability/README.md) | Instrument with OpenTelemetry and visualise traces in the Aspire Dashboard. | 25 min |
| [13 - ConciergeClaw - Agent Harness](./labs/agent-framework-dotnet/13-concierge-claw/README.md) | Wrap the concierge with `AsHarnessAgent()`, adding planning, file memory, loop evaluation, and session serialisation in one call. | 35 min |

## Infrastructure

The lab infrastructure is defined in [Bicep](https://learn.microsoft.com/azure/azure-resource-manager/bicep/overview) using [Azure Verified Modules](https://aka.ms/avm) for Foundry account, Azure AI Search, Azure Container Registry, Azure Container Apps, Storage, and supporting services. Deployments are driven by the [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/) (`azd`).

## Repository layout

| Path | Purpose |
|------|---------|
| `.devcontainer/` | Dev container configuration for VS Code and GitHub Codespaces |
| `.github/` | Copilot guidance, workflows, and issue/PR templates |
| `docs/` | Role-based guides, quickstarts, and lab documentation |
| `infra/` | Bicep IaC using Azure Verified Modules |
| `labs/` | Lab series, each with numbered modules containing `src/` starters and `solution/` |
| `scripts/` | Helper scripts for health checks, role assignment, and index seeding |
| `shared/` | Reusable Python utilities, common dependencies, sample data, and shared MCP server source (`shared/mcp-servers/`) |
