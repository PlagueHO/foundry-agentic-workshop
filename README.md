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

## Build 2026 session mapping

Use this mapping to align each lab with relevant Microsoft Build 2026 sessions.

| Module | Recommended session(s) | Why it fits |
|---|---|---|
| 01 Hosted agents | [BRK243](https://build.microsoft.com/en-US/sessions/BRK243), [BRK241](https://build.microsoft.com/en-US/sessions/BRK241) | Hosted agent architecture, runtime patterns, and production scale guidance |
| 02 Prompt-based agents | [BRK230](https://build.microsoft.com/en-US/sessions/BRK230) | Prompt-centric design in Foundry with model and cost trade-offs |
| 03 Multi-agent-as-tools | [DEM312](https://build.microsoft.com/en-US/sessions/DEM312), [BRK240](https://build.microsoft.com/en-US/sessions/BRK240) | Multi-agent orchestration and context-aware decision flows |
| 04 Agent Framework (Python) | [DEM361](https://build.microsoft.com/en-US/sessions/DEM361), [BRK250](https://build.microsoft.com/en-US/sessions/BRK250) | Agent Framework debugging, observability, and cross-framework control |
| 05 Foundry IQ | [BRK246](https://build.microsoft.com/en-US/sessions/BRK246), [LAB532](https://build.microsoft.com/en-US/sessions/LAB532) | Enterprise retrieval, grounding, and agent-ready knowledge workflows |
| 06 Foundry Toolkit for VS Code | [LTG461](https://build.microsoft.com/en-US/sessions/LTG461), [LTG424](https://build.microsoft.com/en-US/sessions/LTG424) | Practical VS Code toolkit workflows for building and hardening agents |
| 07 Foundry Toolboxes | [LIVE163](https://build.microsoft.com/en-US/sessions/LIVE163) | Tool discovery, governance, and toolbox integration patterns |
| 08 Agent ID and publishing | [DEM340](https://build.microsoft.com/en-US/sessions/DEM340), [LTG422](https://build.microsoft.com/en-US/sessions/LTG422) | Work-ready agent governance, identity, and publishing/monetization pathways |

If sessions are repeated or updated during the event, keep the same session code links and adjust your facilitation schedule based on the latest time slot in the Build portal.

## Attendee setup flow

1. Deploy shared environment from `infra/` using `azd provision`.
1. Assign each attendee their parameterized Foundry project.
1. Complete `labs/00-setup` to verify auth, tools, and project access.
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
- `labs/` numbered module content with `src/` starters and `solution/` placeholders
- `shared/` reusable Python utilities, common dependencies, sample data
- `docs/` instructor and facilitator assets
- `scripts/` helper scripts for lab operations
