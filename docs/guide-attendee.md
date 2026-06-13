# Attendee Guide

This guide walks through preparing your machine and validating access before you run the
labs. For the condensed flow, see the [Attendee Quickstart](./quickstart-attendee.md).

> [!NOTE]
> Running the labs on your local machine is recommended for the best performance and direct Azure credential access. GitHub Codespaces and local dev containers are also fully supported; see [Run in GitHub Codespaces](#run-in-github-codespaces) and [Run in a dev container (local)](#run-in-a-dev-container-local) below for guidance on each.

## What your organizer provides

Your organizer provisions the shared Foundry environment and assigns you a project. Before
you start, you should have:

- Your `FOUNDRY_PROJECT_NAME` (for example, `attendee-01`).
- The shared values: `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `FOUNDRY_RESOURCE_NAME`, `FOUNDRY_PROJECT_ENDPOINT`, `AZURE_OPENAI_ENDPOINT`, and `AZURE_SEARCH_SERVICE_NAME`.

With the default `foundry-user` role you can build agents and use the models your organizer
pre-deployed. You do not deploy models yourself.

## Clone the repository

```bash
git clone https://github.com/PlagueHO/foundry-agentic-workshop.git
cd foundry-agentic-workshop
```

## Install prerequisites

1. Install [VS Code Insiders](https://code.visualstudio.com/insiders/).
1. Install the [Foundry Toolkit for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-windows-ai-studio.windows-ai-studio) from the Extensions view.
1. Install [Python 3.13 or later](https://www.python.org/downloads/).
1. Install the [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).
1. Install the [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd).
1. Create a Python virtual environment in the repository root:

   ```bash
   python -m venv .venv
   ```

   A virtual environment isolates the workshop's Python packages from your system Python and from other projects on your machine. This prevents version conflicts with packages you may already have installed and keeps your global Python installation clean.

   Activate the virtual environment before installing packages or running any lab scripts:

   - **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
   - **Windows (cmd):** `.venv\Scripts\activate.bat`
   - **macOS / Linux:** `source .venv/bin/activate`

   When activated, your terminal prompt shows `(.venv)` as a prefix, confirming the environment is active.

   > [!IMPORTANT]
   > You must activate the virtual environment in every new terminal session before running lab scripts or installing packages. If you open a new terminal and the `(.venv)` prefix is absent, run the activate command again before continuing.

1. Install the workshop Python dependencies:

   ```bash
   python -m pip install -r shared/requirements.txt
   ```

> [!NOTE]
> *Foundry Toolkit for VS Code on the Visual Studio Marketplace.*

## Configure your environment file

1. Copy `shared/.env.example` to `.env` in the repository root.
1. Populate the values your organizer gave you:
   - `AZURE_SUBSCRIPTION_ID`
   - `AZURE_RESOURCE_GROUP`
   - `FOUNDRY_RESOURCE_NAME`
   - `FOUNDRY_PROJECT_NAME` — typically the local part of your UPN (for example `alice-smith` from `alice.smith@contoso.com`), unless your organizer configured sequential names. Confirm with your organizer if unsure.
   - `FOUNDRY_PROJECT_ENDPOINT` — derived as `https://<FOUNDRY_RESOURCE_NAME>.services.ai.azure.com/api/projects/<FOUNDRY_PROJECT_NAME>`. Your organizer's onboarding file contains the exact value.
   - `AZURE_OPENAI_ENDPOINT` — derived as `https://<FOUNDRY_RESOURCE_NAME>.openai.azure.com/openai/v1`. Your organizer's onboarding file contains the exact value.
   - `AZURE_SEARCH_SERVICE_NAME`
1. Leave the attendee RBAC and `AZURE_SEARCH_ADMIN_KEY` values blank; those are for
   organizers.

## Sign in

```bash
az login
az account set --subscription <your-subscription-id>
```

The labs authenticate with `DefaultAzureCredential`, so signing in with the Azure CLI is
enough — no keys required.

## Validate setup

```bash
python scripts/health-check.py
```

Resolve any reported issues before starting. If the check reports a missing value, confirm
it against the assignment your organizer shared.

> [!NOTE]
> Screenshot placeholder — *a successful `health-check.py` run in the terminal.* Alt text: "Terminal showing the health check passing for the configured Foundry project."

## Open your project

> [!IMPORTANT]
> All labs use the **New Foundry** experience. You must enable it before starting. If the portal opens in the legacy view, enable the **New Foundry** toggle in the top navigation bar, then select your project from the dialog that appears.
>
> ![Microsoft Foundry portal header showing the New Foundry toggle switched on, with the project name lab-attendee-1 and navigation links Home, Discover, Build, Operate, Docs.](./assets/screenshots/foundry-new-foundry-toggle.png)
> *The New Foundry toggle (top navigation bar) must be switched on.*

1. Sign in to the [Foundry portal](https://ai.azure.com).
1. Enable the **New Foundry** toggle in the top navigation bar if it is not already on.
1. When prompted, select the project named in your `FOUNDRY_PROJECT_NAME` from the dropdown and select **Let's go**.
1. Confirm the project home page loads showing your project endpoint.

   > [!NOTE]
   > ![New Microsoft Foundry project home page showing "Welcome, Azure Lab Attendee 1" with project endpoint and Azure OpenAI endpoint fields, and cards for Create agents, Explore playgrounds, and Find models.](./assets/screenshots/foundry-new-foundry-project-home.png)
   > *The New Foundry project home page showing your project endpoint and available actions.*

## Start the labs

Open the [available labs](./labs/introduction-foundry-agent-service) in the docs and begin with the first lab in the series. Each lab is independently runnable, so you can resume at any point if you fall behind.

## Run in GitHub Codespaces

GitHub Codespaces creates a fully configured cloud development environment directly from the
repository. The `.devcontainer` configuration installs all prerequisites automatically.

1. Navigate to the [repository on GitHub](https://github.com/PlagueHO/foundry-agentic-workshop).
1. Select **Code**, then select the **Codespaces** tab.
1. Select the **+** icon or **Create codespace on main**.

   > [!NOTE]
   > ![GitHub repository page showing the Code dropdown with the Codespaces tab selected, displaying a Create codespace on main button and an active codespace named silver lamp on the main branch.](./assets/screenshots/github-codespaces-panel-full.png)
   > *The Code dropdown on the GitHub repository page with the Codespaces tab selected.*

1. Wait for the container to build and the post-create setup script to complete. This takes a few minutes on the first launch.
1. Once VS Code loads in the browser (or in the desktop client), continue from
   [Configure your environment file](#configure-your-environment-file) and [Sign in](#sign-in) below.

> [!NOTE]
> During `az login` inside a Codespace, the Azure CLI opens a browser tab for device-code authentication. Ensure your browser allows pop-ups from `github.dev` or `*.github.dev`.
>
> Some Foundry Toolkit visual features work best on a local machine. All scripted lab steps run normally in a Codespace.

## Run in a dev container (local)

If you have Docker and the Dev Containers VS Code extension, you can run the same pre-configured
environment locally without installing Python, the Azure CLI, or other dependencies by hand.

### Additional prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or a compatible container
  runtime with the `docker` CLI (such as Podman Desktop in compatibility mode)
- [VS Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
  (`ms-vscode-remote.remote-containers`)

### Steps

1. Clone the repository and open it in VS Code:

   ```bash
   git clone https://github.com/PlagueHO/foundry-agentic-workshop.git
   code foundry-agentic-workshop
   ```

1. When VS Code prompts **Reopen in Container**, select it. If the notification does not appear,
   open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) and run
   **Dev Containers: Reopen in Container**.
1. Wait for the container to build and the post-create setup script to finish. Progress is visible
   in the terminal that opens automatically.
1. Once the container is ready, continue from [Configure your environment file](#configure-your-environment-file)
   and [Sign in](#sign-in) below.

> [!NOTE]
> The dev container requires at least 8 GB of memory allocated to Docker. Increase this in
> **Docker Desktop > Settings > Resources** if the build fails or VS Code reports low memory.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `pip install` fails with `externally-managed-environment` | Python 3.13 on Linux/macOS enforces PEP 668. | Create and activate the `.venv` virtual environment first (see prerequisites). |
| `health-check.py` reports authentication failure | Not signed in or wrong subscription. | Re-run `az login` and `az account set --subscription <id>`. |
| Project not visible in the portal | Role not yet assigned, or wrong project name. | Confirm your `FOUNDRY_PROJECT_NAME` with your organizer or proctor. |
| Cannot deploy a model | Expected with the `foundry-user` role. | Use the models your organizer pre-deployed. |
| Cannot perform an action in a lab | The lab may require an elevated Foundry role. | Ask your organizer to check and adjust your role assignment. |
| Codespace build fails | Container build error or Docker timeout. | Retry by selecting **Rebuild Container** from the Command Palette. |
| Dev container shows low-memory warning | Docker Desktop memory limit too low. | Increase Docker memory to at least 8 GB in Docker Desktop settings. |
