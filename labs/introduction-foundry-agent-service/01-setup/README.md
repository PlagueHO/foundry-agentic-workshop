# 01. Workshop setup and access verification

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

- `FOUNDRY_PROJECT_NAME` - for example, `attendee-01`.
- Shared values: `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `FOUNDRY_RESOURCE_NAME`, `FOUNDRY_PROJECT_ENDPOINT`, `AZURE_OPENAI_ENDPOINT`, and `AZURE_SEARCH_SERVICE_NAME`.

With the default `foundry-user` role you can build agents and use the models your organizer pre-deployed. You do not deploy models yourself.

> [!TIP]
> For the condensed setup flow, follow the [Attendee Quickstart](../../../docs/quickstart-attendee.md). For full details, troubleshooting, and Codespaces or dev container options, see the [Attendee Guide](../../../docs/guide-attendee.md).

## Prerequisites

Install the following before continuing:

1. [VS Code Insiders](https://code.visualstudio.com/insiders/) with the [Foundry Toolkit for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-windows-ai-studio.windows-ai-studio) extension.
1. [Python 3.13 or later](https://www.python.org/downloads/).
1. [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).

> [!NOTE]
> GitHub Codespaces and local dev containers are fully supported and install all prerequisites automatically. See the [Attendee Guide](../../../docs/guide-attendee.md) for setup steps.

## Steps

- [ ] Clone the repository and open it in VS Code Insiders:

   ```bash
   git clone https://github.com/PlagueHO/foundry-agentic-workshop.git
   cd foundry-agentic-workshop
   code-insiders .
   ```

- [ ] Create a Python virtual environment in the repository root and activate it:

  ```bash
  python -m venv .venv
  ```

  - **Windows:** `.venv\Scripts\activate`
  - **macOS / Linux:** `source .venv/bin/activate`

- [ ] Install the shared Python dependencies:

   ```bash
   python -m pip install -r shared/requirements.txt
   ```

- [ ] Copy `shared/.env.example` to `.env` in the repository root and populate the values your organizer provided:

  - `AZURE_SUBSCRIPTION_ID`
  - `AZURE_RESOURCE_GROUP`
  - `FOUNDRY_RESOURCE_NAME`
  - `FOUNDRY_PROJECT_NAME`
  - `FOUNDRY_PROJECT_ENDPOINT`
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_SEARCH_SERVICE_NAME`

- [ ] Sign in to Azure and select your subscription:

   ```bash
   az login
   az account set --subscription <your-subscription-id>
   ```

- [ ] Run the health check to validate your environment:

   ```bash
   python scripts/health-check.py
   ```

- [ ] Sign in to the [Foundry portal](https://ai.azure.com).

   > [!IMPORTANT]
   > All labs use the **New Foundry** experience. Enable the **New Foundry** toggle in the top navigation bar before starting.

- [ ] Enable the **New Foundry** toggle in the top navigation bar if it is not already on.

   ![New Foundry toggle in the top navigation bar](../../../docs/assets/screenshots/foundry-new-foundry-toggle.png)

- [ ] When prompted, select the project named in your `FOUNDRY_PROJECT_NAME` from the dropdown and select **Let's go**.

   You should see the New Foundry project home page:

   ![New Foundry project home page](../../../docs/assets/screenshots/new-foundry-project-home.png)

## Validation

- `az login` succeeds and the active subscription matches the workshop subscription.
- All required `.env` values are populated.
- `python scripts/health-check.py` reports a healthy environment.
- Your assigned project is visible in the [Foundry portal](https://ai.azure.com).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `pip install` fails with `externally-managed-environment` | Python 3.13 on Linux/macOS enforces PEP 668. | Create and activate the `.venv` virtual environment first (see step 2). |
| `health-check.py` reports authentication failure | Not signed in or wrong subscription. | Re-run `az login` and `az account set --subscription <id>`. |
| Project not visible in the portal | Role not yet assigned, or wrong project name. | Confirm your `FOUNDRY_PROJECT_NAME` with your organizer or proctor. |
| Cannot deploy a model | Expected with the `foundry-user` role. | Use the models your organizer pre-deployed or request your organizer provides you with the necessary permissions. |
| Missing `.env` value | Assignment not yet received. | Confirm the values with your organizer. |
