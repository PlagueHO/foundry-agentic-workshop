# Architecture

The architecture of the workshop is designed to provide a scalable and efficient environment for attendees to learn and experiment with Foundry.

## Azure architecture

All workshop resources are provisioned into a single Azure resource group by [infra/main.bicep](../../infra/main.bicep). A shared Microsoft Foundry account hosts a dedicated Foundry project per attendee, the model deployments, and the agent connections, while a small set of shared platform services back the labs.

![Azure architecture for the Microsoft Foundry agentic workshop, showing a single resource group containing the Foundry account with per-attendee projects, model deployments and connections, alongside Azure AI Search, Cosmos DB, Storage, Key Vault, Container Registry, a Container Apps environment running the Module 06 MCP server, Application Insights and a Log Analytics workspace.](../assets/diagrams/workshop-azure-architecture.svg)

### Components

- **Microsoft Foundry account** — the AI Services account that owns one Foundry project per attendee (plus facilitator, proctor, and organizer projects), the model deployments (`chat`, `embedding`, `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.4-nano`), the content safety (RAI) policy, and all shared connections.
- **Azure AI Search** — search and vector store used for Foundry IQ knowledge bases and agentic retrieval. Connected to the Foundry account for every deployment.
- **Azure Container Registry** — stores the hosted agent images attendees build and push in Module 09. Uses ABAC repository permissions and is connected to the Foundry account.
- **Application Insights** — receives agent telemetry and traces over OpenTelemetry. It is workspace-based and backed by the Log Analytics workspace.
- **Azure Cosmos DB** and **Azure Storage** — optional agent capability hosts for thread storage and file storage, enabled when the corresponding capability-host flags are set.
- **Azure Container Apps environment** — runs the Module 06 Retail Remedy Operations MCP server, which Foundry agents reach over HTTPS and which pulls its image from the container registry.
- **Azure Key Vault** — RBAC-based secret storage for the workshop.
- **Log Analytics workspace** — the central diagnostics sink that every resource sends diagnostic settings to.

### Connections and data flow

- Attendees connect from GitHub Codespaces using the Python `AIProjectClient` SDK to run agents, and push their hosted agent images to the container registry.
- The Foundry account always connects to Azure AI Search, Azure Container Registry, and Application Insights, and optionally to Cosmos DB and Storage when capability hosts are enabled.
- Foundry agents call the Container Apps MCP server over HTTPS, and that server pulls its image from the container registry.
- All resources emit diagnostics to the shared Log Analytics workspace.
