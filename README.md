![Microsoft Foundry Agentic Workshop - Hands-on-labs](./docs/assets/banners/microsoft-foundry-agentic-workshop.png)

# Microsoft Foundry Agentic Workshop

[![Continuous Integration][ci-badge]][ci-url]
[![Continuous Delivery][cd-badge]][cd-url]
[![CodeQL][codeql-badge]][codeql-url]
[![Deploy Docs][docs-badge]][docs-url]
[![Workshop Guide][guide-badge]][guide-url]
[![License: MIT][license-badge]][license-url]
[![PRs Welcome][prs-badge]][prs-url]

This repository contains **L200–L400 hands-on labs** for building agentic solutions on [Microsoft Foundry](https://learn.microsoft.com/azure/ai-foundry/what-is-foundry) using [Microsoft Foundry Agent Service](https://learn.microsoft.com/azure/ai-foundry/agents/overview), [Foundry IQ](https://learn.microsoft.com/azure/ai-foundry/foundry-iq/overview), and the [Microsoft Agent Framework](https://learn.microsoft.com/azure/ai-foundry/agents/agent-framework).

This README is the starting point. It explains **who the workshop is for**, **the two ways to run it**, and **where to go next**. All detailed steps live in the [workshop guide](https://danielscottraynsford.com/foundry-agentic-workshop/) and the [`docs/`](./docs) folder, which is the single source of truth for quickstarts and role guides.

## Link to the workshop guide

[Foundry Agentic Workshop](https://danielscottraynsford.com/foundry-agentic-workshop/) *(Maintained by [@PlagueHO](https://github.com/PlagueHO) - not an official Microsoft resource)*

The guide walks through every lab with facilitator notes, attendee instructions, and lab-by-lab objectives. Use it as your primary reference when delivering or completing the workshop.

## Who is this for

- Software engineers, architects, and technical roles building or designing AI solutions in Azure.
- Comfortable with Azure basics; mostly new to Microsoft Foundry and agentic development.
- Delivered as a facilitator-led group lab, or completed solo in self-learning mode.

## How the workshop is used

The workshop runs in one of two modes. Pick the one that matches your situation, then follow its flow.

### Individual mode (learning solo)

You provision your own Foundry environment scoped to your identity and work through the labs at your own pace. Individual mode (`AZURE_INDIVIDUAL_MODE=true`) creates a single project and writes your `.env` automatically.

**Flow:** provision your environment → validate → work through the labs → tear down.

➡️ Start with the [Individual Quickstart](./docs/quickstart-individual.md), then read the [Individual Guide](./docs/guide-individual.md).

### Group lab mode (facilitator-led)

One **organizer** provisions a single shared Foundry environment with a dedicated project per attendee. **Attendees** then use the connection details they receive - no Azure provisioning on their side. A **facilitator** and optional **proctors** run the live session.

**Flow:** organizer provisions the shared environment and assigns attendees → attendees receive their project and connection values → facilitator delivers the labs → organizer tears down afterwards.

➡️ Organizers start with the [Organizer Quickstart](./docs/quickstart-organizer.md); attendees start with the [Attendee Quickstart](./docs/quickstart-attendee.md).

## Roles and where to start

![Workshop roles jump-in guide — animated carousel cycling through Individual Learner, Organizer, Attendee, Facilitator, and Proctor roles](./docs/assets/carousels/jump-in.svg)

Every delivery involves up to four roles. Only the organizer and attendee are required. Pick your role and follow its quickstart and guide - all steps live in [`docs/`](./docs).

| Role | Mode | Required | Responsible for | Start here | Then read |
|------|------|----------|-----------------|------------|-----------|
| Individual learner | Individual | - | Provisions and completes the labs solo | [Individual Quickstart](./docs/quickstart-individual.md) | [Individual Guide](./docs/guide-individual.md) |
| Organizer | Group | Yes | Provisions the shared environment, assigns access, shares details, tears down | [Organizer Quickstart](./docs/quickstart-organizer.md) | [Organizer Guide](./docs/guide-organizer.md) |
| Attendee | Group | Yes | Completes the labs using the shared environment | [Attendee Quickstart](./docs/quickstart-attendee.md) | [Attendee Guide](./docs/guide-attendee.md) |
| Facilitator | Group | No | Delivers the session, owns pacing and time-boxes, coordinates proctors | [Facilitator Quickstart](./docs/quickstart-facilitator.md) | [Facilitator Guide](./docs/guide-facilitator.md) |
| Proctor | Group | No | Provides 1:1 floor support during delivery | [Proctor Guide](./docs/guide-proctor.md) | - |

> [!TIP]
> Not sure which role you have? If you set up the environment for others, you are the **organizer**. If someone sent you connection details, you are an **attendee**. If you are working alone, use **individual mode**.

## Available labs

| Lab series | Description |
|------------|-------------|
| [Introduction to Foundry Agent Service](./docs/labs/introduction-foundry-agent-service.md) | Build agents from first principles using Foundry Agent Service, MCP tools, Foundry IQ, the Python Agent Framework, and hosted agents |
| [Introduction to Microsoft Agent Framework (.NET)](./docs/labs/agent-framework-dotnet.md) | Build agentic .NET applications end-to-end using the Microsoft Agent Framework, from a single-turn agent through to a fully hosted, observable multi-agent system |

The full module list, timings, and objectives for each series live in the linked docs pages above. Every module is independently runnable, so you can resume at any point.

## Cost

Plan for approximately **AUD 50/day** for a sandbox environment, depending on region, SKU, and usage. Tear down with `azd down --force --purge` when finished; see the relevant quickstart for teardown details.

## Infrastructure

The lab infrastructure is defined in [Bicep](https://learn.microsoft.com/azure/azure-resource-manager/bicep/overview) using [Azure Verified Modules](https://aka.ms/avm) for the Foundry account, Azure AI Search, Azure Container Registry, Azure Container Apps, Storage, and supporting services. Deployments are driven by the [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/) (`azd`). See the [infrastructure design](./docs/design/infrastructure.md) and [architecture](./docs/design/architecture.md) docs for details.

## Repository layout

| Path | Purpose |
|------|---------|
| `.devcontainer/` | Dev container configuration for VS Code and GitHub Codespaces |
| `.github/` | Copilot guidance, workflows, and issue/PR templates |
| `docs/` | Role-based guides, quickstarts, and lab documentation (the source of truth) |
| `infra/` | Bicep IaC using Azure Verified Modules |
| `labs/` | Lab series, each with numbered modules containing `src/` starters and `solution/` |
| `scripts/` | Helper scripts for health checks, role assignment, and index seeding |
| `shared/` | Reusable Python utilities, common dependencies, sample data, and shared MCP server source (`shared/mcp-servers/`) |

## Contributing

Contributions are welcome. Please open an issue before submitting a pull request for anything beyond trivial fixes, so maintainers can confirm the change is in scope. See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on bug reports, content improvements, new lab modules, and the pull request process.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

<!-- Badge reference links -->
[ci-badge]: https://github.com/PlagueHO/foundry-agentic-workshop/actions/workflows/continuous-integration.yml/badge.svg
[ci-url]: https://github.com/PlagueHO/foundry-agentic-workshop/actions/workflows/continuous-integration.yml
[cd-badge]: https://github.com/PlagueHO/foundry-agentic-workshop/actions/workflows/continuous-delivery.yml/badge.svg
[cd-url]: https://github.com/PlagueHO/foundry-agentic-workshop/actions/workflows/continuous-delivery.yml
[codeql-badge]: https://github.com/PlagueHO/foundry-agentic-workshop/actions/workflows/codeql.yml/badge.svg
[codeql-url]: https://github.com/PlagueHO/foundry-agentic-workshop/actions/workflows/codeql.yml
[docs-badge]: https://github.com/PlagueHO/foundry-agentic-workshop/actions/workflows/deploy-docs.yml/badge.svg
[docs-url]: https://github.com/PlagueHO/foundry-agentic-workshop/actions/workflows/deploy-docs.yml
[guide-badge]: https://img.shields.io/badge/Workshop%20Guide-online-blue?logo=readthedocs&logoColor=white
[guide-url]: https://danielscottraynsford.com/foundry-agentic-workshop/
[license-badge]: https://img.shields.io/badge/License-MIT-yellow.svg
[license-url]: ./LICENSE
[prs-badge]: https://img.shields.io/badge/PRs-welcome-brightgreen.svg
[prs-url]: ./CONTRIBUTING.md
