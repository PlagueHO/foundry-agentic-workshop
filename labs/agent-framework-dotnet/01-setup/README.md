# 01. Environment Setup

**Estimated time:** 15 minutes

> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Understand what Azure services you have been provisioned with for this lab.
- Install prerequisites and configure your local environment.
- Sign in to Azure and confirm access to your assigned Foundry project.
- Verify the pre-provisioned environment so you can focus on building agents.

## What your organizer provides

Your organizer provisions the shared Foundry environment and assigns you a project. Before you start, you should have received:

- **Attendee Portal URL** — sign in with your lab Microsoft account to get your personal `.env` values.
- `FOUNDRY_PROJECT_NAME` — for example, `attendee-01`.
- Shared values: `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `FOUNDRY_RESOURCE_NAME`, `FOUNDRY_PROJECT_ENDPOINT`, `AZURE_OPENAI_ENDPOINT`, and `AZURE_SEARCH_SERVICE_NAME`.

With the default `foundry-user` role you can build agents and use the models your organizer pre-deployed. You do not deploy models yourself.

> [!TIP]
> For the condensed setup flow, follow the [Attendee Quickstart](../../../docs/quickstart-attendee.md). For full details, troubleshooting, and Codespaces or dev container options, see the [Attendee Guide](../../../docs/guide-attendee.md).

## Prerequisites

Install the following before continuing:

1. [.NET 10 SDK](https://dot.net/download).
1. [Python 3.13 or later](https://www.python.org/downloads/).
1. [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).
1. [Docker](https://www.docker.com/products/docker-desktop/) (optional) — required only for [Module 12](../12-observability/README.md), which runs the Aspire Dashboard as a local container.

> [!NOTE]
> Docker is only needed for the Aspire Dashboard container in Module 12. You can complete the rest of the lab without it. GitHub Codespaces and local dev containers are fully supported, include Docker, and install all other prerequisites automatically. See the [Attendee Guide](../../../docs/guide-attendee.md) for setup steps.

## Steps

### Part 1 — Clone and install dependencies

#### 1. Clone the repository

- [ ] Clone the repository and open it in your editor:

  ```bash
  git clone https://github.com/PlagueHO/foundry-agentic-workshop.git
  cd foundry-agentic-workshop
  ```

#### 2. Create a Python virtual environment

- [ ] Create and activate a Python virtual environment in the repository root:

  ```bash
  python -m venv .venv
  ```

  - **Windows:** `.venv\Scripts\activate`
  - **macOS / Linux:** `source .venv/bin/activate`

#### 3. Install Python dependencies

- [ ] Install the shared Python dependencies:

  ```bash
  python -m pip install -r shared/requirements.txt
  ```

#### 4. Restore .NET packages

- [ ] Restore the NuGet packages for all lab projects:

  ```bash
  dotnet restore labs/agent-framework-dotnet
  ```

### Part 2 — Configure your environment

#### 5. Populate your .env file

- [ ] Get your environment variables from the **Attendee Portal URL** your organizer shared. Sign in with your lab Microsoft account, then copy the values or click **Download .env** to save the file directly.

  If the portal is unavailable, copy the values from the onboarding file your organizer sent.

  In either case, copy `shared/.env.example` to `.env` in the repository root and populate:

  - `AZURE_SUBSCRIPTION_ID`
  - `AZURE_RESOURCE_GROUP`
  - `FOUNDRY_RESOURCE_NAME`
  - `FOUNDRY_PROJECT_NAME`
  - `FOUNDRY_PROJECT_ENDPOINT`
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_SEARCH_SERVICE_NAME`

### Part 3 — Sign in and verify

#### 6. Sign in to Azure

- [ ] Sign in to Azure and select your subscription:

  ```bash
  az login
  az account set --subscription <your-subscription-id>
  ```

#### 7. Run the health check

- [ ] Confirm all environment variables and Azure connectivity are working:

  ```bash
  python labs/agent-framework-dotnet/shared/health-check.py
  ```

## Validation

- `az login` succeeds and the active subscription matches the workshop subscription.
- All required `.env` values are populated.
- `dotnet --version` outputs `10.x.x`.
- `python labs/agent-framework-dotnet/shared/health-check.py` reports a healthy environment.

## Congratulations 🎉

You built a solid foundation for the rest of the lab. You created and activated a Python virtual environment, installed the shared dependencies, restored the .NET packages, populated your `.env` file, and signed in to Azure — with the health check passing. Everything is in place to start building agents.

> [!TIP]
> **Next up → [Module 02: Your First Agent](../02-first-agent/README.md)**
> Create the simplest possible AI agent backed by Azure AI Foundry and run your first conversation.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `pip install` fails with `externally-managed-environment` | Python 3.13 on Linux/macOS enforces PEP 668. | Create and activate the `.venv` virtual environment first (see step 2). |
| `health-check.py` reports authentication failure | Not signed in or wrong subscription. | Re-run `az login` and `az account set --subscription <id>`. |
| `FOUNDRY_PROJECT_ENDPOINT is not set` | `.env` file missing or endpoint not populated. | Confirm `.env` exists in the repository root with your endpoint value. |
| `dotnet: command not found` | .NET 10 SDK not installed. | Install the [.NET 10 SDK](https://dot.net/download). |
| `dotnet restore` fails | NuGet feed unavailable or package not yet released. | Check your network connection and the NuGet package feed configuration. |
