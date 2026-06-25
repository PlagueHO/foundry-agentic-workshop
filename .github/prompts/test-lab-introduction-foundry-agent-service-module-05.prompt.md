---
description: "Test lab module 05 (Agent tools and evaluations) end-to-end by operating inside an already-open GitHub Codespace and the Foundry portal (ai.azure.com), verifying every step carefully via the browser. The Codespace must already be open and authenticated to Azure, and Module 04 must have been completed (the acl-remedy-advisor agent must exist) before this prompt is run."
---

## Inputs

- ${input:attendeeUpn}: (Required) The UPN of the attendee to test with (e.g. `lab.attendee.1@MngEnvMCAP199525.onmicrosoft.com`).
- ${input:envName}: (Required) The azd environment name the lab was provisioned into (e.g. `foundry-hol2`).

---

You must test the steps in the #file:labs/introduction-foundry-agent-service/05-agent-tools-and-evaluations/README.md by operating inside an open GitHub Codespace browser session and the Foundry portal at `https://ai.azure.com`. The attendee is `${input:attendeeUpn}` in the environment `${input:envName}`.

> **Important:** Any Azure or GitHub login dialogs that appear during the test must be completed by the user. Pause and prompt the user whenever a sign-in dialog is encountered. Do not attempt to enter credentials automatically.

## Pre-flight - Verify the environment is ready

Before executing any lab steps, confirm all prerequisites are satisfied. **Do not proceed if any check fails** - report the failure and ask the user to resolve it.

### Check 1 - Confirm the Codespace browser page is open and shared

1. Use `open_browser_page` to list currently available pages.
1. Confirm a page is open with a URL matching `*.github.dev/*` or `github.dev/*`, indicating a GitHub Codespace connected to VS Code in the browser.
1. If no such page is available, pause and instruct the user to:
   - Navigate to `https://github.com/PlagueHO/foundry-agentic-workshop`.
   - Click **Code → Codespaces** and open or create a codespace on the current branch.
   - Wait for the devcontainer to finish building, then share the resulting browser tab with this session.
1. Take a screenshot of the Codespace page to confirm it is showing VS Code with the `foundry-agentic-workshop` repository open.

### Check 2 - Confirm the Foundry portal is open and authenticated

1. Use `open_browser_page` to navigate to `https://ai.azure.com`.
1. Take a screenshot and confirm the portal home page or a project page is visible.
1. Confirm the signed-in account displayed in the top-right corner matches `${input:attendeeUpn}`. If a login dialog or account-picker is shown, pause and instruct the user to sign in with `${input:attendeeUpn}` before continuing. Do not enter credentials automatically.
1. Once authenticated, confirm the portal is accessible and note the project name visible in the portal (or navigate to **All projects** to find the project assigned to `${input:attendeeUpn}`).

### Check 3 - Confirm Module 04 is complete: acl-remedy-advisor agent exists

1. In the Foundry portal, navigate to the attendee's Foundry project.
1. In the left navigation, click **Agents**.
1. Confirm `acl-remedy-advisor` appears in the agent list with at least **v1** recorded.
1. If the agent is absent, **do not proceed** - instruct the user to complete Module 04 successfully before running this test.
1. Note the current highest version of the agent (expected: **v1** if Module 04 was just completed, or higher if the attendee has already experimented).

### Check 4 - Confirm Azure authentication in the Codespace

1. Switch back to the Codespace browser page.
1. Open a terminal in the Codespace (if one is not already open).
1. Run:

   ```bash
   az account show --query '{user:user.name, subscription:id}' -o table
   ```

1. Confirm the output shows `${input:attendeeUpn}` as the signed-in user.
1. If the command fails or shows a different identity, pause and ask the user to run `az login` in the Codespace terminal and complete the browser sign-in before continuing.

### Check 5 - Confirm the Foundry Toolkit shows the project and the v1 agent

1. Click the **Foundry Toolkit** icon in the Activity Bar.
1. In **MY RESOURCES**, expand **Prompt Agents** → **acl-remedy-advisor**.
1. Confirm **v1** (or the version noted in Check 3) is listed below the agent name.
1. If the project or agent is not visible, click the refresh icon next to **MY RESOURCES**, wait 10 seconds, and retry.
1. Take a screenshot of the Foundry Toolkit panel showing the agent and its version.

---

## Part 1 - Add Code Interpreter to the agent

### Step 1 - Open the agent in Agent Builder

1. In the Foundry Toolkit **MY RESOURCES** panel, confirm **Prompt Agents** → **acl-remedy-advisor** is expanded.
1. Click **v1** to open Agent Builder.
1. Confirm the Agent Builder header shows `acl-remedy-advisor | Microsoft Foundry | v1`.
1. Take a screenshot of the Agent Builder header confirming the version label.

   **Check:** If **v1** is not directly clickable, click **acl-remedy-advisor** first to expand its version list, then click **v1**. If Agent Builder opens a blank view, reload the VS Code window (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> → **Developer: Reload Window**) and retry.

### Step 2 - Open the tool picker

1. Scroll down in the left panel of Agent Builder to the **TOOL** section.
1. Confirm **Web search** is already listed (it was added in Module 04).
1. Click the **+** button next to **TOOL** to open the *Select a tool* dialog.
1. Confirm the dialog opens and the **Configured** tab is active by default.
1. Take a screenshot of the dialog showing the available tools, noting the **Added** badge on **Web search**.

   **Check:** If the **+** button is not visible, hover over the **TOOL** section header. If the dialog still does not open, reload the Codespace window and retry from Step 1.

### Step 3 - Add Code Interpreter

1. In the *Select a tool* dialog, locate **Code Interpreter** in the tool list.
1. Click **Code Interpreter** to select it. Confirm the card visually highlights.
1. Confirm **Web search** shows an **Added** badge (already configured from Module 04).
1. Click **Add Tools (1)** at the bottom-right of the dialog.
1. Confirm the dialog closes.
1. Confirm **Code Interpreter** now appears in the **TOOL** section below **Web search**.
1. Take a screenshot showing both **Web search** and **Code Interpreter** listed in the **TOOL** section.

   **Check:** If Code Interpreter does not appear after the dialog closes, close and reopen Agent Builder. If it still does not appear, click the refresh icon next to **MY RESOURCES** and reopen the agent.

---

## Part 2 - Update the instructions

### Step 4 - Add a Code Interpreter instruction

1. Scroll back up to the **Instructions** field in Agent Builder.
1. Confirm the original Module 04 instructions are still present and intact. The instructions should end with `Be concise and practical - retail staff need fast, clear answers in a busy store environment.`
1. Click at the very end of the existing instructions text to position the cursor there.
1. Press <kbd>Enter</kbd> twice to create a blank line, then type or paste the following paragraph exactly:

   ```text
   When asked to calculate refund amounts, depreciation, pro-rata warranty
   values, or compare prices, use code interpreter to perform the calculation
   precisely and show your working.
   ```

1. Confirm the new paragraph is visible at the bottom of the Instructions field.
1. Take a screenshot showing the updated Instructions field with the new paragraph visible at the bottom.

   **Check:** Confirm the original Module 04 instructions remain intact above the new paragraph. If any text was accidentally replaced, use <kbd>Ctrl</kbd>+<kbd>Z</kbd> to undo and retry.

---

## Part 3 - Save and test the updated agent

### Step 5 - Save as version 2

1. Click **Save to Foundry** in the top-right of Agent Builder.
1. Wait for the confirmation notification: *Agent 'acl-remedy-advisor' updated successfully.*
1. Confirm the Agent Builder header now shows `acl-remedy-advisor | Microsoft Foundry | v2`.
1. In the **MY RESOURCES** panel, confirm **v2** now appears under `acl-remedy-advisor` alongside **v1**.
1. Take a screenshot of the Agent Builder header showing `v2` and the sidebar showing both `v1` and `v2`.

   **Check:** If the save fails with "Cannot read properties of undefined", click **Save to Foundry** again - this is a known transient error. If it continues to fail after three attempts, confirm the Default Project is still set correctly in the Foundry Toolkit and that the Codespace can reach the Foundry endpoint (`curl -I $FOUNDRY_PROJECT_ENDPOINT` in the terminal).

### Step 6 - Test in the playground

1. Click the **Playground** tab at the top of Agent Builder.
1. Send the following message to test the agent with both a legal guidance need (Web search) and a calculation need (Code Interpreter):

   ```text
   A customer bought a $899 laptop 14 months ago. The battery now only holds 20% of its original capacity after normal use. The manufacturer's warranty was 12 months. What are the customer's rights under Australian Consumer Law, and what would a reasonable refund amount be if they've had 14 months of use from a product expected to last at least 3 years?
   ```

1. Wait for the full response and take a screenshot.
1. Verify the response meets **all** of these criteria:
   - Classifies the failure as **major** or **minor** under ACL (or both, with an explanation of the distinction).
   - Explains the remedy options available to the customer under each classification.
   - Cites at least one URL from `accc.gov.au` or a state consumer affairs site (Web search fired).

1. Note whether **Code Interpreter** activity is visible in the response (e.g. a code block output, a calculation shown step-by-step, or a `[code interpreter]` indicator). Record this observation without treating absence as a failure - the model exercises judgement about when to invoke Code Interpreter.

   > If you want to verify Code Interpreter fires reliably, send a second, calculation-focused message:
   >
   > ```text
   > Calculate the pro-rata refund for a $899 laptop used for 14 out of an expected 36 months. Show your working.
   > ```
   >
   > Confirm a code block or calculation output is visible in the response.

1. Take a screenshot of the playground response.

   **Check:** If the response contains no ACL classification at all, scroll up in the Instructions field to confirm the Module 04 instructions are still present. If the response errors with a connectivity message, run `curl -I $FOUNDRY_PROJECT_ENDPOINT` in the terminal to verify the endpoint is reachable.

---

## Part 4 - Scaffold evaluation code

### Step 7 - Open the Evaluation tab in Agent Builder

1. In Agent Builder, look for the **Evaluation** tab in the header area alongside **Playground** and **Conversations**.
1. Click **Evaluation**.
1. Confirm the **Evaluation Setup** screen appears with two options:
   - **Scaffold Evaluation Code**
   - A link or button labelled **Go to Foundry**
1. Take a screenshot of the Evaluation Setup screen.

   **Check:** If the **Evaluation** tab is not visible, scroll the Agent Builder header to reveal hidden tabs, or resize the panel. If it still does not appear, reload the window and reopen the agent.

### Step 8 - Choose evaluators

1. Click **Scaffold Evaluation Code**.
1. Confirm the **Select Evaluator(s)** dialog opens, listing evaluators grouped by category.
1. In the **Agents** category, check **Tool Call Accuracy**.
1. In the **Agents** category, also check **Task Adherence**.
1. Confirm the dialog header shows **2 Selected**.
1. Take a screenshot of the dialog with both evaluators checked.
1. Click **OK**.

   **Check:** If the dialog does not open at all, confirm the Foundry Toolkit has an active project connection. Check the VS Code **Output** panel (select **Foundry Toolkit** in the dropdown) for errors before retrying.

### Step 9 - Select the save folder and confirm files are generated

1. When the folder picker dialog appears with the prompt *Select a folder to save the evaluation code*, navigate to:

   ```text
   labs/introduction-foundry-agent-service/05-agent-tools-and-evaluations/src
   ```

1. Click **Select Folder**.
1. In the Codespace file explorer (sidebar), expand `labs/introduction-foundry-agent-service/05-agent-tools-and-evaluations/src/`.
1. Confirm the following six files were generated (alongside the existing `starter.py`):
   - `test_acl_remedy_advisor.py`
   - `data.jsonl`
   - `evaluators.py`
   - `requirements.txt`
   - `pytest.ini`
   - `README.md`
1. Take a screenshot of the file explorer showing all six generated files.

   **Check:** If no files appear, confirm the `src/` directory exists and VS Code has write permission. In the Codespace terminal, verify with `ls labs/introduction-foundry-agent-service/05-agent-tools-and-evaluations/src/`. If the directory is missing or write-protected, resolve that and retry from Step 8. If files still are not generated, check the VS Code **Output → Foundry Toolkit** panel for error details.

### Step 10 - Inspect the generated files

1. Open `test_acl_remedy_advisor.py` in the editor.
1. Confirm the file contains `from pytest_agent_evals import` with at least `EvaluatorResults`, `evals`, `AzureOpenAIModelConfig`, `FoundryAgentConfig`, and `BuiltInEvaluatorConfig` in the import block.
1. Open `data.jsonl` and confirm it contains at least one JSON line with a `query` field containing an ACL-related question.
1. Open `evaluators.py` and confirm it references environment variables for the judge model (look for `AZURE_OPENAI_ENDPOINT` or `AZURE_OPENAI_DEPLOYMENT_NAME`).
1. Take a screenshot of `test_acl_remedy_advisor.py` open in the editor showing the import block.

---

## Part 5 - Run an automatic evaluation in the Foundry portal

### Step 11 - Navigate to the agent in the Foundry portal

1. Switch to the Foundry portal browser tab (`https://ai.azure.com`).
1. Confirm you are in the attendee's project. If not, navigate to it from **All projects**.
1. In the left navigation, click **Agents**.
1. Click **acl-remedy-advisor** in the agent list to open the agent detail view.
1. Click the **Evaluation** tab at the top of the agent detail page.
1. Confirm the **Automatic Evaluation** sub-tab is selected.
1. Take a screenshot of the Evaluation tab (note whether previous evaluations are listed or whether it shows *No evaluations found*).
1. Click **Create** in the top-right corner of the evaluations list.

   **Check:** If **acl-remedy-advisor** is not in the Agents list in the portal, the agent save in Step 5 may not have propagated. Reload the portal page and wait 30 seconds before retrying. If the agent is still absent, verify the Codespace is connected to the correct project endpoint.

### Step 12 - Wizard Step 1: Select evaluation target

1. Confirm the **Create new evaluation** wizard opens at **Step 1: Target**.
1. Confirm **Agent** is selected as the target type.
1. Confirm `acl-remedy-advisor v2` (or the latest version saved in Step 5) is pre-checked in the agent list on the right.
1. Take a screenshot of Step 1.
1. Click **Next**.

   **Check:** If only **v1** is listed or if the expected version is not pre-checked, verify that the save in Step 5 completed with the correct version confirmation. Reload the portal page if needed to refresh the agent version list.

### Step 13 - Wizard Step 2: Select evaluation scope

1. Confirm **Step 2: Scope** shows options including **Individual turns** and **Full conversations (preview)**.
1. Confirm **Individual turns** is selected.
1. Take a screenshot of Step 2.
1. Click **Next**.

### Step 14 - Wizard Step 3: Configure synthetic data

1. Confirm **Step 3: Data** is shown.
1. Confirm **Synthetic generation** is selected (it should be the default).
1. Click **Generate** to open the dataset configuration dialog.
1. In the **Generate synthetic dataset** dialog:
   - Confirm **Model** is set to `chat` (or the project's chat deployment).
   - Change **Number of rows** to **5**.
   - In the **Prompt** field, enter:

     ```text
     Generate questions a retail staff member might ask about Australian
     Consumer Law remedies for common product faults: faulty electronics,
     broken appliances, defective clothing, and expired warranties. Include
     at least one question requiring a refund calculation.
     ```

1. Take a screenshot of the dialog showing the row count and prompt text.
1. Click **Confirm**.
1. Confirm a dataset card appears under Synthetic generation showing a name and *Version 1.0*.
1. Take a screenshot of the data step with the dataset card visible.
1. Click **Next**.

   **Check:** If the **Generate** button is absent or the dialog fails to open, confirm the project has an active chat model deployment. If the generation request errors, try reducing rows to **3** and retry. If the project shows no model deployments, report this as a failure - the environment provisioning may be incomplete.

### Step 15 - Wizard Step 4: Review pre-selected criteria

1. Confirm **Step 4: Criteria** is shown with evaluators pre-selected across multiple categories.
1. Confirm evaluators are present in at least the **Agents**, **Quality**, and **Safety** groupings.
1. Note the total evaluator count (expected: approximately 19 evaluators for an Agent scoped to Individual turns).
1. Leave all pre-selected evaluators active.
1. Take a screenshot of the Criteria step showing the evaluator groups and their items.
1. Click **Next**.

### Step 16 - Wizard Step 5: Name and submit

1. Confirm **Step 5: Review** is shown with a summary panel on the right listing Target, Scope, Dataset, and Evaluators.
1. In the evaluation name field, enter:

   ```text
   acl-remedy-advisor-tools-eval
   ```

1. Confirm the summary shows the correct target (`acl-remedy-advisor v2`), scope (Individual turns), and the synthetic dataset.
1. Take a screenshot of the Review step showing the name and summary.
1. Click **Submit**.
1. Confirm the portal navigates to the `acl-remedy-advisor-tools-eval` evaluation detail page.

   **Check:** If the name field is read-only or the Submit button is disabled, confirm all prior wizard steps completed without errors. If submission fails with an error, note the full error message and include it in the report.

### Step 17 - Monitor the evaluation run

1. On the `acl-remedy-advisor-tools-eval` detail page, locate the run row in **Evaluation runs**.
1. Confirm the run shows a **Queued** or **In progress** status immediately after submission.
1. Take a screenshot confirming the run was submitted successfully.
1. Wait for the **Status** to change to **Completed**. With 5 rows and approximately 19 evaluators, expect 3–10 minutes. If the run has not completed within 15 minutes, note this as a warning and include the current status in the report - do not block the test run indefinitely.
1. Once **Completed**, click the run name to open the detailed results view.
1. Take a screenshot of the results view showing per-evaluator scores across the test rows.
1. Verify:
   - **ToolCallAccuracy** score column is visible in the results.
   - **TaskAdherence** score column is visible in the results.
   - Safety evaluator columns (**Violence**, **SelfHarm**, **IndirectAttack**) do not show elevated risk scores (scores near 0 or *Very low* are expected for a retail law scenario).

   **Check:** If the evaluation stays **In progress** beyond 15 minutes, check the Azure portal for quota alerts on the chat deployment. Note this in the report and advise the user to reduce rows or check quota before retrying.

---

## Validation - Confirm all lab criteria

Work through each item in the lab's Validation section and confirm the outcome:

1. The Agent Builder header shows `acl-remedy-advisor | Microsoft Foundry | v2` after saving.
1. **Code Interpreter** appears in the **TOOL** section of Agent Builder alongside **Web search**.
1. **v2** appears under `acl-remedy-advisor` in the **MY RESOURCES** panel alongside **v1**.
1. The playground response for the laptop battery prompt classifies the failure under ACL and provides remedy options with at least one ACCC citation.
1. All six expected files exist in `labs/introduction-foundry-agent-service/05-agent-tools-and-evaluations/src/`: `test_acl_remedy_advisor.py`, `data.jsonl`, `evaluators.py`, `requirements.txt`, `pytest.ini`, `README.md`.
1. The Foundry portal shows an `acl-remedy-advisor-tools-eval` evaluation with a **Completed** status (or **In progress** if still running at report time) and per-evaluator score columns are visible once complete.

---

## Step 18 - Report results

Report the outcome of every step above. For each step state whether it **passed**, **failed**, or was **skipped**. For any failure, include:

- The exact step number and description.
- The observed behaviour.
- The expected behaviour.
- Any error messages, unexpected output, or unexpected UI state encountered.
- The screenshot filename or description if a screenshot was taken.

If all steps pass, confirm that lab module 05 end-to-end validation is complete.
