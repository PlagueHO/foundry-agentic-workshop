# Learner Quickstart

Use this guide when your organizer has already provisioned shared workshop infrastructure.

## Prerequisites

1. VS Code Insiders and Foundry Toolkit for VS Code.
1. Python 3.11 or later.
1. Azure CLI installed.
1. Assigned project information from your organizer.

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

## Start labs

1. Begin with [Introduction to Foundry Agent Service](./labs/introduction-foundry-agent-service.md).
1. Continue through labs 01-08 in order.
