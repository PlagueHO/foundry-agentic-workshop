# Microsoft Foundry Agentic Workshop (HOL)

This repository scaffolds a **3–4 hour, L200–L300 instructor-led workshop** for building agentic solutions on **Microsoft Foundry**.

## Audience

- Software engineers and technical data scientists
- Comfortable with Azure basics
- Mostly new to Microsoft Foundry

## Prerequisites

- Azure subscription with quota to deploy lab resources
- VS Code Insiders
- Foundry Toolkit for VS Code
- Python 3.11+
- Azure CLI (`az`)
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

## Quick start for lab organizers

Use this path when one organizer deploys a shared environment for multiple learners.

1. Sign in to Azure and azd.

```bash
az login
azd auth login
```

1. Select or create an azd environment name.

```bash
azd env new hol-shared
azd env select hol-shared
```

1. Set core deployment variables.

```bash
azd env set AZURE_LOCATION australiaeast
azd env set AZURE_RESOURCE_GROUP rg-foundry-hol-shared
azd env set AZURE_ATTENDEE_COUNT 20
azd env set AZURE_ATTENDEE_PROJECT_PREFIX attendee
```

1. Optional: set RBAC profile and attendee identities.

```bash
azd env set AZURE_ATTENDEE_ACCESS_PROFILE project-user
azd env set AZURE_ATTENDEE_USER_PRINCIPAL_NAMES '["learner1@contoso.com","learner2@contoso.com"]'
```

Use `project-user` for least-privilege labs (00-07). For publishing scenarios in lab 08, switch to `project-publisher`.

1. Provision infrastructure.

```bash
azd provision
```

1. View project assignments and share each learner's `FOUNDRY_PROJECT_NAME` value.

```bash
azd env get-value AZURE_ATTENDEE_PROJECT_NAMES
```

1. Tear down when the workshop is finished.

```bash
azd down --force --purge
```

## Quick start for learners

Use this path when an organizer has already deployed shared infrastructure.

1. Copy `shared/.env.example` to a local `.env` file and fill in assigned values:
   - `AZURE_SUBSCRIPTION_ID`
   - `AZURE_RESOURCE_GROUP`
   - `FOUNDRY_RESOURCE_NAME`
   - `FOUNDRY_PROJECT_NAME`
   - `AZURE_SEARCH_SERVICE_NAME`

1. Sign in and confirm the correct subscription is active.

```bash
az login
az account set --subscription <your-subscription-id>
```

1. Run the environment check.

```bash
python scripts/health-check.py
```

1. Complete `labs/introduction-foundry-agent-service/00-setup` first, then progress through labs 01-08 in order.

## Multi-environment model

- Shared environment model: one organizer deploys a shared Foundry account with multiple attendee projects.
- Per-learner environment model: each learner runs `azd env new <name>` with `AZURE_ATTENDEE_COUNT=1`.
- Environments are isolated by azd environment name and resource group naming.

## Cost note

Plan for approximately **AUD 50/day** for a sandbox environment, depending on region, SKU, and usage.

## Reset between runs

Use `azd down --force --purge` to remove workshop resources between deliveries, then redeploy with updated attendee count.

## Why Bicep

We chose Bicep because it is purpose-built for Azure, concise, readable, and first-class with Azure tooling. It gives us safer infrastructure changes with clear module composition, strong resource typing, and predictable deployment behavior in CI/CD.

This workshop also leans on Azure Verified Modules to keep infrastructure patterns consistent, maintainable, and production-aligned.

## Infrastructure deployment (Bicep + azd)

The infrastructure is defined in Bicep using Azure Verified Modules for Foundry account, Azure AI Search, Storage, and supporting services.

### Quick start

```bash
az login
azd auth login
azd env new hol
azd env set AZURE_LOCATION australiaeast
azd env set AZURE_RESOURCE_GROUP rg-foundry-hol
azd env set AZURE_ATTENDEE_COUNT 20
azd provision
```

### Optional attendee configuration

Set attendee-specific variables in the active azd environment before provisioning:

```bash
azd env set AZURE_ATTENDEE_PROJECT_PREFIX attendee
azd env set AZURE_ATTENDEE_ACCESS_PROFILE project-user
azd env set AZURE_ATTENDEE_USER_PRINCIPAL_NAMES '["learner1@contoso.com","learner2@contoso.com"]'
azd provision
```

### Teardown

```bash
azd down --force --purge
```

## Repository layout

- `.github/` Copilot guidance and issue/PR templates
- `infra/` Bicep IaC (AVM modules) and parameter templates
- `labs/introduction-foundry-agent-service/` numbered module content with `src/` starters and `solution/` placeholders
- `shared/` reusable Python utilities, common dependencies, sample data
- `docs/` instructor and facilitator assets
- `scripts/` helper scripts for lab operations
