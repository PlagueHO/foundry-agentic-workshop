---
description: "Test lab module 03 (Foundry Toolkit for VS Code) end-to-end by opening a GitHub Codespace for this repository and following each step of the lab in VS Code Insiders, verifying correctness at every stage. Login dialogs must be completed by the user."
---

## Inputs

* ${input:attendeeUpn}: (Required) The UPN of the attendee to test with (e.g. `lab.attendee.1@MngEnvMCAP199525.onmicrosoft.com`).
* ${input:envName}: (Required) The azd environment name the lab was provisioned into (e.g. `foundry-hol2`).

---

You must test the steps in the #file:labs/introduction-foundry-agent-service/03-foundry-toolkit-vscode/README.md by opening a GitHub Codespace for this repository and following each step inside VS Code Insiders. The attendee is `${input:attendeeUpn}` in the environment `${input:envName}`.

> **Important:** Any Azure or GitHub login dialogs that appear during the test must be completed by the user. Pause and prompt the user whenever a sign-in dialog is encountered. Do not attempt to enter credentials automatically.

## Step 1 — Open a GitHub Codespace for this repository

1. Open the browser and navigate to `https://github.com/PlagueHO/foundry-agentic-workshop`.
1. Click **Code** → **Codespaces** → **Create codespace on main** (or open an existing codespace if one already exists for the current branch).
1. Wait for the codespace to finish building and for VS Code Insiders to connect to it. The devcontainer will install all required extensions, including the Foundry Toolkit.
1. Confirm the codespace terminal is active and the repository is open in VS Code Insiders.

> **Note:** If a login dialog appears at any point during Codespace creation or VS Code connection, pause and ask the user to complete sign-in before continuing.

## Step 2 — Load the attendee environment

1. In the codespace terminal, run:

   ```bash
   azd env get-values --environment ${input:envName}
   ```

   Confirm the output includes `FOUNDRY_PROJECT_NAME` and `FOUNDRY_PROJECT_ENDPOINT`.

1. Locate the attendee onboarding file at:

   ```bash
   .azure/${input:envName}/<upn_local>.md
   ```

   Where `<upn_local>` is the part of `${input:attendeeUpn}` before the `@` symbol. Read the file to confirm all required environment variables are present.

1. Confirm a `.env` file exists at the repository root and is populated with the attendee's values. If it is missing, copy `shared/.env.example` to `.env` and populate it from the onboarding file's `## Your Environment Variables` section.

## Step 3 — Validate Step 1 of the lab (Verify the extension is installed)

Follow lab step **1. Verify the extension is installed**:

1. Open the **Extensions** view with <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>X</kbd> in VS Code Insiders inside the codespace.
1. Search for `Foundry Toolkit` and confirm the extension published by **Microsoft** (`ms-windows-ai-studio.windows-ai-studio`) is listed, installed, and enabled.
1. Confirm the **Foundry Toolkit icon** (the blue Foundry spark logo) is visible in the **Activity Bar** on the left side of VS Code.

   > **Check:** If the icon is absent, verify the devcontainer finished building and reload the VS Code window (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> → **Developer: Reload Window**).

## Step 4 — Validate Step 2 of the lab (Sign in to Azure)

Follow lab step **2. Sign in to Azure**:

1. Press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>A</kbd> or click the Azure icon in the Activity Bar to open the **Azure** view.
1. If the panel shows **Sign in to Azure…**, pause and ask the user to complete the browser-based sign-in with the workshop account `${input:attendeeUpn}`.
1. After sign-in, confirm the attendee's subscription appears under **RESOURCES** in the Azure view.
1. As a fallback, open a terminal in the codespace and run `az login` to confirm the identity; verify the active subscription matches `AZURE_SUBSCRIPTION_ID` from the onboarding file.

## Step 5 — Validate Step 3 of the lab (Connect to your Foundry project)

Follow lab step **3. Connect to your Foundry project**:

1. Click the **Foundry Toolkit** icon in the Activity Bar.
1. In the **My Resources** section, expand **Microsoft Foundry Resources** and click **Set Default Project**.
1. Confirm a quick-pick dropdown appears listing Foundry projects in the subscription.
1. Select the project assigned to `${input:attendeeUpn}`. Verify the project name matches `FOUNDRY_PROJECT_NAME` from the onboarding file. You can cross-check by running:

   ```bash
   azd env get-values --environment ${input:envName} | grep FOUNDRY_PROJECT_NAME
   ```

1. Confirm the toolkit now shows the project name under **My Resources** with sub-sections for **Models**, **Prompt Agents**, **Hosted Agents (Preview)**, **Tools**, **Knowledge**, and **Evaluations**.

## Step 6 — Validate Step 4 of the lab (Tour the extension interface)

Follow lab step **4. Tour the extension interface**:

1. Expand **My Resources** and confirm the project name is visible. Expand it and verify the sub-sections **Models**, **Prompt Agents**, **Hosted Agents**, **Connections**, and **Knowledge Stores** are present.
1. Expand **Developer Tools** and confirm the **Discover** and **Build** groups are listed.
1. Expand **Help and Feedback** and confirm documentation links are present.
1. Press <kbd>F1</kbd>, type `Foundry Toolkit`, and verify that commands such as **Open Model Catalog** and **Open Playground** appear in the command palette.

## Step 7 — Validate Step 5 of the lab (Explore My Resources — deployed models)

Follow lab step **5. Explore My Resources — deployed models**:

1. Under **My Resources**, expand the project, then expand **Models**.
1. Confirm both the `chat` model (GPT-4o) and the `embedding` model are listed.
1. Click the `chat` model entry and confirm the model card opens showing:
   * **Deployment info**: name, provisioning state, deployment type, and rate limit.
   * **Endpoint info**: target URI and authentication type.
   * **Useful links**: code sample and tutorial links.

## Step 8 — Validate Step 6 of the lab (Explore Developer Tools — Model Catalog)

Follow lab step **6. Explore Developer Tools — Model Catalog**:

1. Under **Developer Tools**, expand **Discover** and double-click **Model Catalog**.
1. Confirm the Model Catalog page opens in the editor area.
1. Verify the filter dropdowns are functional: **Hosted by**, **Publisher**, **Feature**, and **Model type**.
1. Use the search bar to search for a model by name and confirm results appear.
1. Click any model card and confirm its full description, context window, and supported inference tasks are displayed.

## Step 9 — Validate Step 7 of the lab (Explore Developer Tools — Tool Catalog)

Follow lab step **7. Explore Developer Tools — Tool Catalog**:

1. Under **Developer Tools**, expand **Discover** and double-click **Tool Catalog**.
1. Confirm the Tool Catalog page opens and lists available tools and MCP servers.

## Step 10 — Validate Step 8 of the lab (Open the Model Playground)

Follow lab step **8. Open the Model Playground**:

1. Under **Developer Tools**, double-click **Model Playground**.
1. Confirm the Model Playground opens in the editor area.
1. In the **BASIC INFORMATION** panel, confirm **chat (via Microsoft Foundry)** is selected in the model dropdown.
1. Click the **System prompt** field and enter exactly:

   ```text
   You are a helpful retail assistant for Contoso Outdoors, a company that sells
   outdoor sporting goods and equipment. You help customers with product inquiries,
   order status, return policies, and general shopping assistance. Always be
   friendly, concise, and direct customers to relevant products where appropriate.
   If you don't know something, say so honestly.
   ```

1. In the chat area, type the following question and press <kbd>Ctrl</kbd>+<kbd>Enter</kbd> to send:

   ```text
   What's your return policy for hiking boots, and do you have any waterproof options available?
   ```

1. Confirm the model returns a response that:
   * Is in the role of a Contoso Outdoors retail assistant.
   * Addresses the return policy question.
   * Mentions or acknowledges waterproof boot options.
1. Click **View Code** (top right of the playground) and confirm a code snippet is displayed that reproduces the playground call.

## Step 11 — Validate Step 9 of the lab (Generate starter code for a model)

Follow lab step **9. Generate starter code for a model**:

1. In **My Resources > Models**, right-click the `chat` model and select **Open code file**.
1. Confirm a dialog or quick-pick appears prompting for:
   * **SDK**: Azure AI Foundry SDK (or Azure OpenAI SDK) — select **Azure AI Foundry SDK**.
   * **Language**: Python — select **Python**.
   * **Authentication**: DefaultAzureCredential — select **DefaultAzureCredential**.
1. Confirm a new file opens in the editor containing a working Python code sample.
1. Verify the generated code:
   * Pulls the project endpoint from an environment variable (not a hard-coded value).
   * Uses `DefaultAzureCredential` for authentication.
   * Contains an import for `azure-ai-projects` or equivalent SDK.

## Step 12 — Validate the Validation criteria

Confirm each item listed in the **Validation** section of the lab README is satisfied:

1. The **Foundry Toolkit** icon appears in the Activity Bar.
1. The toolkit **My Resources** section shows the assigned project name with **Models**, **Prompt Agents**, **Hosted Agents**, **Tools**, **Knowledge**, and **Evaluations** visible.
1. The **Models** sub-section lists at least the `chat` and `embedding` deployments.
1. The **Model Playground** accepts a system prompt, sends a user message, and returns a response in the role of the retail assistant.
1. The **View Code** button in the playground generates a Python code snippet.

## Step 13 — Report results

Report the outcome of every step above clearly. For each step state whether it **passed** or **failed**. For any failure, include:

* The exact step number and description.
* The observed behaviour.
* The expected behaviour.
* Any error messages or unexpected UI state encountered.

If all steps pass, confirm the lab module 03 end-to-end validation is complete.
