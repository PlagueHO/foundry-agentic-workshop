# Azure AI Foundry Agentic Workshop (HOL)

This repository scaffolds a **3–4 hour, L200–L300 instructor-led workshop** for building agentic solutions on **Azure AI Foundry**.

## Audience

- Software engineers and technical data scientists
- Comfortable with Azure basics
- Mostly new to Azure AI Foundry

## Prerequisites

- Azure subscription with quota to deploy lab resources
- VS Code Insiders
- Foundry Toolkit for VS Code
- Python 3.11+
- Azure CLI (`az`)
- Terraform 1.9+
- Azure Developer CLI (`azd`)
- An AI coding agent (GitHub Copilot or Claude Code)

## Agenda (3–4 hours)

| Module | Topic | Duration (min) |
|---|---|---:|
| 00 | Setup and access validation | 20 |
| 01 | Hosted agents (framework-orchestrated ReAct + tools) | 30 |
| 02 | Prompt-based agents (prompt-orchestrated ReAct + tools) | 30 |
| 03 | Multi-agent-as-tools patterns | 30 |
| 04 | Microsoft Agent Framework (Python) | 25 |
| 05 | Foundry IQ retrieval across enterprise sources | 30 |
| 06 | Foundry Toolkit for VS Code tasks | 20 |
| 07 | Foundry Toolboxes (optional) | 15 |
| 08 | Agent ID and publishing | 20 |

## Attendee setup flow

1. Deploy shared environment from `infra/` using `azd provision`.
1. Assign each attendee their parameterized Foundry project.
1. Complete `labs/agent-service-introduction/00-setup` to verify auth, tools, and project access.
1. Progress through labs in numerical order.

## Cost note

Plan for approximately **AUD 50/day** for a sandbox environment, depending on region, SKU, and usage.

## Reset between runs

Use `infra/teardown.sh` or `infra/teardown.ps1` to remove workshop resources between instructor deliveries, then redeploy with updated attendee count.

## Infrastructure deployment (Terraform + azd)

The infrastructure is defined in Terraform using:

- **Azure Verified Modules (AVM)** for Foundry account, Azure AI Search, and Storage
- **AzAPI** for Azure AI Foundry project child resources and Foundry-to-Search connection

### Quick start

```bash
az login
azd auth login
./infra/deploy.sh hol australiaeast rg-foundry-hol 20
```

### Optional custom naming

Set Terraform variables in the active azd environment before provisioning:

```bash
azd env set TF_VAR_foundry_name foundryhol001
azd env set TF_VAR_search_name foundryholsearch001
azd env set TF_VAR_storage_account_name foundryholstorage01
azd provision
```

### Teardown

```bash
./infra/teardown.sh hol
```

## Repository layout

- `.github/` Copilot guidance and issue/PR templates
- `infra/` Terraform IaC (AVM + AzAPI), azd-friendly deploy wrappers
- `labs/agent-service-introduction/` numbered module content with `src/` starters and `solution/` placeholders
- `shared/` reusable Python utilities, common dependencies, sample data
- `docs/` instructor and facilitator assets
- `scripts/` helper scripts for lab operations
