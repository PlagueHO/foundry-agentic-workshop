# Attendee Quickstart

Use this quickstart when your organizer has already provisioned shared workshop
infrastructure. It is the high-level flow; see the [Attendee Guide](./guide-attendee.md) for
detailed setup and troubleshooting.

## Prerequisites

1. [VS Code Insiders](https://code.visualstudio.com/insiders/) with the [Foundry Toolkit for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-windows-ai-studio.windows-ai-studio).
1. [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).
1. [Python 3.13 or later](https://www.python.org/downloads/).
1. Your assigned project information from your organizer.

## Clone the repository

```bash
git clone https://github.com/PlagueHO/foundry-agentic-workshop.git
cd foundry-agentic-workshop
```

## Configure your environment file

1. Copy `shared/.env.example` to `.env`.
1. Populate these values from your assignment:
   - `AZURE_SUBSCRIPTION_ID`
   - `AZURE_RESOURCE_GROUP`
   - `FOUNDRY_RESOURCE_NAME`
   - `FOUNDRY_PROJECT_NAME`
   - `AZURE_SEARCH_SERVICE_NAME`

## Sign in

```bash
az login
az account set --subscription <your-subscription-id>
```

## Validate setup

```bash
python scripts/health-check.py
```

## Start the labs

Open the [available labs](./labs/introduction-foundry-agent-service) in the docs and begin with the first lab in your assigned series. Each lab is independently runnable, so you can resume at any point.
