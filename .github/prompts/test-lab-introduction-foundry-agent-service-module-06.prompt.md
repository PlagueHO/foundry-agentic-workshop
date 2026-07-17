---
description: "Test lab module 06 (Integrate MCP tools) end-to-end by operating inside an already-open GitHub Codespace for this repository in VS Code Insiders, verifying every step carefully via the browser. The Codespace must already be open and authenticated to Azure with the Foundry project set as default before this prompt is run."
---

## Inputs

- ${input:attendeeUpn}: (Required) The UPN of the attendee to test with (e.g. `lab.attendee.1@MngEnvMCAP199525.onmicrosoft.com`).
- ${input:envName}: (Required) The azd environment name the lab was provisioned into (e.g. `foundry-hol2`).

---

You must test the steps in the #file:labs/introduction-foundry-agent-service/06-mcp-tools/README.md by operating inside an open GitHub Codespace browser session. The attendee is `${input:attendeeUpn}` in the environment `${input:envName}`.

> **Important:** Any Azure or GitHub login dialogs that appear during the test must be completed by the user. Pause and prompt the user whenever a sign-in dialog is encountered. Do not attempt to enter credentials automatically.

## Pre-flight - Verify the Codespace is ready

Before executing any lab steps, confirm all prerequisites are satisfied. **Do not proceed if any check fails** - report the failure and ask the user to resolve it.

### Check 1 - Confirm the Codespace browser page is open and shared

1. Use `open_browser_page` to check which pages are currently available.
1. Confirm a page is open with a URL matching `*.github.dev/*` or `github.dev/*`, indicating a GitHub Codespace connected to VS Code Insiders in the browser.
1. If no such page is available, pause and instruct the user to:
   - Navigate to `https://github.com/PlagueHO/foundry-agentic-workshop`.
   - Click **Code → Codespaces** and open or create a codespace on the current branch.
   - Wait for the devcontainer to finish building, then share the resulting browser tab with this session.
1. Take a screenshot of the Codespace page to confirm it is showing VS Code Insiders with the `foundry-agentic-workshop` repository open.

### Check 2 - Confirm Azure authentication

1. In the Codespace terminal, run:

   ```bash
   az account show --query '{user:user.name, subscription:id}' -o table
   ```

1. Confirm the output shows `${input:attendeeUpn}` as the signed-in user and that the subscription ID matches `AZURE_SUBSCRIPTION_ID` from the environment.
1. If the command fails or shows a different identity, pause and ask the user to run `az login` in the codespace terminal and complete the browser sign-in before continuing.

### Check 3 - Confirm the Foundry project is set as default in the Foundry Toolkit

1. Click the **Foundry Toolkit** icon in the Activity Bar (the blue Foundry spark logo).
1. In **My Resources**, confirm the project name assigned to `${input:attendeeUpn}` is shown and expanded, with sub-sections including **Models**, **Prompt Agents**, **Hosted Agents (Preview)**, **Tools**, **Knowledge**, and **Evaluations** visible.
1. If the project is not set, follow the Set Default Project flow from module 03 before continuing.

### Check 4 - Confirm the `.env` file exists and contains required values

1. In the Codespace terminal, run:

   ```bash
   cat .env | grep -E 'FOUNDRY_PROJECT_ENDPOINT|AGENT_NAME|RETAIL_REMEDY_OPS_MCP_SERVER_URL'
   ```

1. Confirm `FOUNDRY_PROJECT_ENDPOINT` is populated with a non-empty value.
1. Confirm `AGENT_NAME` is set to `acl-remedy-advisor`.
1. Confirm `RETAIL_REMEDY_OPS_MCP_SERVER_URL` is populated with the shared **Azure Container Apps** MCP server URL the organizer deployed. It ends in `/mcp` and the host looks like `https://ca-mcp-<env>.<region>.azurecontainerapps.io/mcp`.
1. If `.env` does not exist, confirm with the user that module 01 has been completed, then copy `shared/.env.example` to `.env` and populate `FOUNDRY_PROJECT_ENDPOINT` and `RETAIL_REMEDY_OPS_MCP_SERVER_URL` from the attendee onboarding file at `.azure/${input:envName}/<upn_local>.md` (where `<upn_local>` is the part of `${input:attendeeUpn}` before `@`).

### Check 5 - Confirm the `acl-remedy-advisor` agent exists at the end state of module 05

This module requires the `acl-remedy-advisor` agent to already exist with both **Web search** and **Code Interpreter** tools attached and saved as **v2**, as created during module 05.

1. In the Foundry Toolkit panel, expand **MY RESOURCES → Prompt Agents**.
1. Confirm `acl-remedy-advisor` is listed.
1. Expand `acl-remedy-advisor` and confirm **v2** is listed (v1 from module 04 and v2 from module 05 should both appear).
1. Click **v2** to open Agent Builder and confirm:
   - The Agent Builder header shows `acl-remedy-advisor | Microsoft Foundry | v2`.
   - The **TOOL** section lists both **Web search** and **Code Interpreter**.
   - The instructions include the Code Interpreter paragraph added in module 05:
     *"When asked to calculate refund amounts, depreciation, pro-rata warranty values, or compare prices, use code interpreter to perform the calculation precisely and show your working."*

   **Check:** If the agent does not exist or is not at v2 with both tools, run the module 05 solution script before continuing:

   ```bash
   uv run python labs/introduction-foundry-agent-service/05-agent-tools-and-evaluations/solution/create_agent.py
   ```

   Then re-verify the agent state before proceeding.

1. Take a screenshot of the Agent Builder showing `acl-remedy-advisor v2` with both tools visible.

---

## Part 1 - Confirm the deployed MCP server

By default the organizer deploys the shared **Retail Remedy Operations** MCP server to **Azure Container Apps**, and its public HTTPS URL is already in the attendee's `.env` file as `RETAIL_REMEDY_OPS_MCP_SERVER_URL`. Nothing needs to run locally - the agent calls the deployed server directly, and this URL must always be present in `.env`.

### Step 1 - Confirm the deployed MCP server URL

1. In the Codespace terminal, print the configured URL:

   ```bash
   grep '^RETAIL_REMEDY_OPS_MCP_SERVER_URL=' .env
   ```

1. Confirm `RETAIL_REMEDY_OPS_MCP_SERVER_URL` is set to the shared Azure Container Apps URL. It ends in `/mcp` and the host looks like:

   ```text
   https://ca-mcp-<env>.<region>.azurecontainerapps.io/mcp
   ```

   **Check:** If `RETAIL_REMEDY_OPS_MCP_SERVER_URL` is empty, populate it from the attendee onboarding file at `.azure/${input:envName}/<upn_local>.md` (where `<upn_local>` is the part of `${input:attendeeUpn}` before `@`), or from `azd env get-values`. The `.env` file must always contain this value before continuing.

### Step 2 - Verify the deployed server is reachable

1. Confirm the deployed endpoint responds by running:

   ```bash
   curl -s -o /dev/null -w "%{http_code}" "$(grep '^RETAIL_REMEDY_OPS_MCP_SERVER_URL=' .env | cut -d= -f2-)"
   ```

1. Confirm the HTTP status code is `200`, `405`, or `406` (a non-connection response confirms the endpoint is reachable).
1. Take a screenshot of the terminal showing the status code.

   **Check:** If the command times out or returns a connection error, the deployed Azure Container Apps server is unavailable. Pause and ask the user to confirm with the organizer that the shared MCP server is running before continuing.

<details>
<summary>Optional - run your own MCP server locally and expose it with a public tunnel</summary>

If the shared Azure Container Apps server is unavailable, or you want to run and modify the server yourself, host it locally and expose it with a public HTTPS tunnel. The Azure-hosted agent runs in the cloud and cannot reach `localhost`, so the forwarded port must be **Public**.

1. In a dedicated terminal that stays open for the rest of the workshop, start the server:

   ```bash
   uv run python shared/mcp-servers/retail-remedy-ops/src/server.py
   ```

   Confirm it prints `Starting Retail Remedy Operations MCP server on http://0.0.0.0:8080/mcp`.

1. In the VS Code **PORTS** panel, forward port `8080`, then right-click the row and set **Port Visibility** → **Public**. A private port returns `403` to the Azure-hosted agent.
1. Copy the forwarded address, append `/mcp`, and set `RETAIL_REMEDY_OPS_MCP_SERVER_URL` in `.env` to the full tunnel URL:

   ```bash
   echo "RETAIL_REMEDY_OPS_MCP_SERVER_URL=<tunnel-url>" >> .env
   ```

1. Verify reachability with the same `curl` command from Step 2.

</details>

---

## Part 2 - Connect the MCP server to the agent

### Step 3 - Open the agent in Agent Builder

1. In the Foundry Toolkit panel (**MY RESOURCES → Prompt Agents**), expand `acl-remedy-advisor` and click **v2** to open Agent Builder.
1. Confirm the Agent Builder header shows `acl-remedy-advisor | Microsoft Foundry | v2`.

### Step 4 - Add the MCP tool

1. Scroll to the **TOOL** section and click the **+** button.
1. In the tool picker, look for an option labelled **MCP**, **Custom MCP**, or **Model Context Protocol**.
1. Fill in the connection details:

   | Field | Value |
   |---|---|
   | Label / Name | `retail_remedy_ops` |
   | Server URL | Your `RETAIL_REMEDY_OPS_MCP_SERVER_URL` from `.env`, ending in `/mcp` |
   | Authentication | None / Anonymous |

1. Confirm and save the MCP tool connection. Agent Builder discovers the tools from the server's `/mcp` endpoint.
1. Verify that all six tool names appear in the tool list:
   - `lookup_purchase`
   - `get_product_profile`
   - `search_store_policy`
   - `find_replacement_options`
   - `draft_remedy_summary`
   - `create_remedy_case`

   **Check:** If the tool picker does not show an MCP or Custom MCP option, the Foundry Toolkit version may not support MCP tools via the UI. Use the code fallback:

   ```bash
   uv run python labs/introduction-foundry-agent-service/06-mcp-tools/solution/create_agent_with_mcp.py
   ```

   Confirm `RETAIL_REMEDY_OPS_MCP_SERVER_URL` is set in `.env` before running. After the script completes, re-open `acl-remedy-advisor` in Agent Builder and verify the six tools are listed.

   **Check:** If only some tools appear (fewer than six), the deployed server may be unhealthy. Re-run the `curl` reachability check from Step 2, and if it fails ask the user to confirm the shared MCP server status with the organizer.

1. Take a screenshot of the Agent Builder TOOL section showing all six MCP tool names.

---

## Part 3 - Update the agent instructions

### Step 5 - Add the MCP tool-boundary instruction

1. Scroll to the **Instructions** field in Agent Builder.
1. Confirm the existing instructions include both the base ACL advisor text (from module 04) and the Code Interpreter paragraph (from module 05).
1. Position the cursor at the very end of the existing instructions and press **Enter** twice to create a blank line.
1. Add the following paragraph exactly:

   ```text
   Use the retail operations MCP tools when a question includes a receipt ID,
   customer ID, or product ID, or when staff ask about store policy, warranty
   details, or replacement availability. Call lookup_purchase first to retrieve
   the purchase record, then get_product_profile for lifespan and warranty data,
   search_store_policy for relevant policy excerpts, and find_replacement_options
   if the customer may want a replacement. Use draft_remedy_summary to produce a
   structured summary for the staff member. Use create_remedy_case to log the
   outcome if the staff member confirms the remedy. Do not invent purchase,
   warranty, policy, or stock details - call the MCP tools instead.
   ```

1. Take a screenshot of the instructions field showing the new paragraph at the bottom.

   **Check:** If the instructions field shows only the base text without the Code Interpreter paragraph from module 05, the wrong agent version is open. Confirm the header shows `v2` and re-add the missing Code Interpreter paragraph before adding the MCP paragraph.

### Step 6 - Save as v3

1. Click **Save to Foundry** in Agent Builder.
1. Wait for the confirmation notification: *Agent 'acl-remedy-advisor' updated successfully.*
1. Confirm the Agent Builder header now shows `acl-remedy-advisor | Microsoft Foundry | v3`.
1. Check the **MY RESOURCES** panel - **v3** should appear below `acl-remedy-advisor` alongside **v1** and **v2**.
1. Take a screenshot of the MY RESOURCES panel showing all three versions.

---

## Part 4 - Test with a realistic scenario

### Step 7 - Run the battery-failure test prompt

1. Click the **Playground** tab in Agent Builder (ensure it is targeting `acl-remedy-advisor v3`).
1. Paste the following prompt and send it:

   ```text
   Receipt R-1007 is for a laptop bought by customer C-1042. The battery now only
   holds 20% charge after 14 months of normal use. Check our records and store
   policy, then advise the retail staff member what remedy to offer under Australian
   Consumer Law. Include any replacement options and calculate a reasonable
   pro-rata refund.
   ```

1. Wait for the response and take a screenshot of the playground.
1. Confirm the agent's final response includes:
   - A remedy recommendation citing store policy and Australian Consumer Law.
   - A refund or replacement option.
   - At least one policy citation.

   **Check:** If the agent answers from general knowledge without calling any MCP tools, the instructions may not have been saved or the MCP connection may be broken. Re-run the `curl` reachability check from Step 2 to confirm the deployed server responds, then retry.

### Step 8 - Inspect the run trace

1. Open the **Run** trace in the playground or the **Runs** panel in Agent Builder.
1. Confirm MCP tool calls appear in the trace. Look for at least these three calls:
   - `lookup_purchase`
   - `get_product_profile`
   - `search_store_policy`
1. Confirm Code Interpreter is also called at least once for the pro-rata refund calculation.
1. Confirm the final response includes a clear remedy recommendation.
1. Take a screenshot of the run trace showing the MCP tool calls and Code Interpreter call.

   **Check:** If MCP tool calls do not appear in the trace, confirm the MCP tool instructions were saved (Step 6) and the MCP tool shows in the TOOL section of Agent Builder. Also confirm `RETAIL_REMEDY_OPS_MCP_SERVER_URL` still points at the deployed server and that the `curl` reachability check from Step 2 succeeds.

   **Check:** If Code Interpreter does not appear in the trace, the calculation may have been answered from general knowledge. Try adding the phrase *"Show your working using code."* to the prompt to force Code Interpreter.

---

## Part 5 (optional) - Verify from code

### Step 9 - Chat from the terminal

1. Open a terminal in the Codespace.
1. Run the chat client:

   ```bash
   uv run python labs/introduction-foundry-agent-service/06-mcp-tools/src/starter.py
   ```

1. Confirm the output begins with `Conversation started:` followed by a UUID-format conversation ID.
1. At the `You:` prompt, send the battery-failure prompt from Step 7.
1. Confirm `[tool: ...]` indicators appear before the final response, showing the agent called tools during the turn. Look for entries such as:
   - `[tool: mcp_call]` or similar MCP tool indicators
   - Indicators for Code Interpreter
1. Confirm the final `Advisor:` response includes a remedy recommendation with store policy and ACL guidance.
1. Type `exit` and press <kbd>Enter</kbd>. Confirm `Goodbye.` is printed and the script exits cleanly.
1. Take a screenshot of the terminal showing the conversation with tool indicators and the `Goodbye.` message.

   **Check:** If the script raises `KeyError: 'FOUNDRY_PROJECT_ENDPOINT'`, confirm `.env` is saved and that `FOUNDRY_PROJECT_ENDPOINT` is not blank.

   **Check:** If the script raises an authentication error, run `az login` in the terminal.

   **Check:** If no tool indicators appear, the agent may be using a cached version without MCP tools. Confirm `AGENT_NAME=acl-remedy-advisor` in `.env` and that v3 was saved successfully in Step 6.

---

## Validation - confirm all criteria

Work through each item in the lab's Validation section and confirm:

1. `RETAIL_REMEDY_OPS_MCP_SERVER_URL` in `.env` is set to the shared Azure Container Apps URL ending in `/mcp`.
1. The deployed MCP server responds to the `curl` reachability check (status `200`, `405`, or `406`).
1. `acl-remedy-advisor` in Agent Builder shows all six MCP tool names (`lookup_purchase`, `get_product_profile`, `search_store_policy`, `find_replacement_options`, `draft_remedy_summary`, `create_remedy_case`) in its tool list.
1. The Agent Builder header shows `acl-remedy-advisor | Microsoft Foundry | v3` after saving.
1. The battery-failure test prompt triggers at least three MCP tool calls visible in the run trace.
1. The run trace also shows Code Interpreter used for the pro-rata calculation.
1. The final response includes a remedy recommendation, a refund or replacement option, and a policy citation.
1. The MCP tool calls in the run trace return purchase, product, and policy facts, confirming the agent reached the deployed server.

---

## Step 10 - Report results

Report the outcome of every step above. For each step state whether it **passed** or **failed**. For any failure, include:

- The exact step number and description.
- The observed behaviour.
- The expected behaviour.
- Any error messages, unexpected output, or unexpected UI state encountered.
- The screenshot filename or description if a screenshot was taken.

If all steps pass, confirm that lab module 06 end-to-end validation is complete.
