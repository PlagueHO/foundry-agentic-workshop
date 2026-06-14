---
description: "Test lab module 06 (Integrate MCP tools) end-to-end by operating inside an already-open GitHub Codespace for this repository in VS Code Insiders, verifying every step carefully via the browser. The Codespace must already be open and authenticated to Azure with the Foundry project set as default before this prompt is run."
---

## Inputs

- ${input:attendeeUpn}: (Required) The UPN of the attendee to test with (e.g. `lab.attendee.1@MngEnvMCAP199525.onmicrosoft.com`).
- ${input:envName}: (Required) The azd environment name the lab was provisioned into (e.g. `foundry-hol2`).

---

You must test the steps in the #file:labs/introduction-foundry-agent-service/06-mcp-tools/README.md by operating inside an open GitHub Codespace browser session. The attendee is `${input:attendeeUpn}` in the environment `${input:envName}`.

> **Important:** Any Azure or GitHub login dialogs that appear during the test must be completed by the user. Pause and prompt the user whenever a sign-in dialog is encountered. Do not attempt to enter credentials automatically.

## Pre-flight — Verify the Codespace is ready

Before executing any lab steps, confirm all prerequisites are satisfied. **Do not proceed if any check fails** — report the failure and ask the user to resolve it.

### Check 1 — Confirm the Codespace browser page is open and shared

1. Use `open_browser_page` to check which pages are currently available.
1. Confirm a page is open with a URL matching `*.github.dev/*` or `github.dev/*`, indicating a GitHub Codespace connected to VS Code Insiders in the browser.
1. If no such page is available, pause and instruct the user to:
   - Navigate to `https://github.com/PlagueHO/foundry-agentic-workshop`.
   - Click **Code → Codespaces** and open or create a codespace on the current branch.
   - Wait for the devcontainer to finish building, then share the resulting browser tab with this session.
1. Take a screenshot of the Codespace page to confirm it is showing VS Code Insiders with the `foundry-agentic-workshop` repository open.

### Check 2 — Confirm Azure authentication

1. In the Codespace terminal, run:

   ```bash
   az account show --query '{user:user.name, subscription:id}' -o table
   ```

1. Confirm the output shows `${input:attendeeUpn}` as the signed-in user and that the subscription ID matches `AZURE_SUBSCRIPTION_ID` from the environment.
1. If the command fails or shows a different identity, pause and ask the user to run `az login` in the codespace terminal and complete the browser sign-in before continuing.

### Check 3 — Confirm the Foundry project is set as default in the Foundry Toolkit

1. Click the **Foundry Toolkit** icon in the Activity Bar (the blue Foundry spark logo).
1. In **My Resources**, confirm the project name assigned to `${input:attendeeUpn}` is shown and expanded, with sub-sections including **Models**, **Prompt Agents**, **Hosted Agents (Preview)**, **Tools**, **Knowledge**, and **Evaluations** visible.
1. If the project is not set, follow the Set Default Project flow from module 03 before continuing.

### Check 4 — Confirm the `.env` file exists and contains required values

1. In the Codespace terminal, run:

   ```bash
   cat .env | grep -E 'FOUNDRY_PROJECT_ENDPOINT|AGENT_NAME'
   ```

1. Confirm `FOUNDRY_PROJECT_ENDPOINT` is populated with a non-empty value.
1. Confirm `AGENT_NAME` is set to `acl-remedy-advisor`.
1. If `.env` does not exist, confirm with the user that module 01 has been completed, then copy `shared/.env.example` to `.env` and populate `FOUNDRY_PROJECT_ENDPOINT` from the attendee onboarding file at `.azure/${input:envName}/<upn_local>.md` (where `<upn_local>` is the part of `${input:attendeeUpn}` before `@`).

### Check 5 — Confirm the `acl-remedy-advisor` agent exists at the end state of module 05

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
   python labs/introduction-foundry-agent-service/05-agent-tools-and-evaluations/solution/create_agent.py
   ```

   Then re-verify the agent state before proceeding.

1. Take a screenshot of the Agent Builder showing `acl-remedy-advisor v2` with both tools visible.

---

## Part 1 — Run the MCP server locally

### Step 1 — Open a dedicated terminal for the server

1. In the Codespace, open a new terminal panel (**Terminal > New Terminal**, or press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>`</kbd>).
1. Confirm the new terminal is open and ready at the repository root.

   > This terminal must remain open for the rest of the workshop. The MCP server must continue running while the agent is used in modules 06 through 10.

### Step 2 — Start the MCP server

1. In the new terminal, run:

   ```bash
   python shared/mcp-servers/retail-remedy-ops/src/server.py
   ```

1. Confirm the server prints the following startup line (take a screenshot):

   ```text
   Starting Retail Remedy Operations MCP server on http://0.0.0.0:8080/mcp
   ```

   **Check:** If the command fails with `ModuleNotFoundError`, confirm the Python dependencies are installed:

   ```bash
   pip install -r shared/requirements.txt
   ```

   Then retry starting the server.

   **Check:** If port 8080 is already in use, identify and stop the conflicting process before restarting.

---

## Part 2 — Expose the server with a public tunnel

The agent runs in the Azure cloud and cannot reach `localhost`. Port 8080 must be exposed with a public HTTPS URL.

### Step 3 — Forward port 8080

1. In the VS Code bottom panel, click the **PORTS** tab.
1. Click **Forward a Port** (or the `+` icon) and type `8080`, then press **Enter**.
1. Confirm port `8080` appears in the ports table.
1. Take a screenshot of the PORTS tab showing port 8080 forwarded.

### Step 4 — Set visibility to Public

1. Right-click the `8080` row in the PORTS panel.
1. Select **Port Visibility** → **Public**.

   > [!IMPORTANT]
   > If a browser dialog appears asking you to authenticate or confirm the action, pause and ask the user to complete it. Do not attempt to enter credentials automatically.

1. Confirm the **Visibility** column now shows **Public**.

   **Check:** If **Public** is not available (the option is greyed out or missing), the Codespace may not support public port forwarding. Report this as a failure — the lab cannot proceed without a public URL.

1. Take a screenshot of the PORTS panel confirming visibility is set to Public.

### Step 5 — Copy the tunnel URL

1. In the **Forwarded Address** column of the PORTS panel, hover over the `8080` row and copy the tunnel URL.
1. Confirm the URL matches one of these patterns depending on the environment:
   - **GitHub Codespaces**: `https://<codespace-name>-8080.app.github.dev`
   - **VS Code Dev Tunnels**: `https://abc123-8080.devtunnels.ms`
1. Append `/mcp` to the copied URL. For example:

   ```text
   https://<codespace-name>-8080.app.github.dev/mcp
   ```

1. Verify the URL is reachable by running in a second terminal (do not use the server terminal):

   ```bash
   curl -s -o /dev/null -w "%{http_code}" <tunnel-url>
   ```

   Confirm the HTTP status code is `200` or `405` (Method Not Allowed is acceptable — it confirms the endpoint is reachable).

   **Check:** If the status code is `403`, the port visibility is not set to Public. Return to Step 4 and re-confirm.

   **Check:** If the command times out or returns a connection error, the tunnel is not active. Re-forward the port and retry.

1. Record the full tunnel URL (ending in `/mcp`) — it will be used in Steps 7 and the `.env` file.
1. Optionally, set `MCP_SERVER_URL` in the `.env` file to this URL now:

   ```bash
   echo "MCP_SERVER_URL=<tunnel-url>" >> .env
   ```

---

## Part 3 — Connect the MCP server to the agent

### Step 6 — Open the agent in Agent Builder

1. In the Foundry Toolkit panel (**MY RESOURCES → Prompt Agents**), expand `acl-remedy-advisor` and click **v2** to open Agent Builder.
1. Confirm the Agent Builder header shows `acl-remedy-advisor | Microsoft Foundry | v2`.

### Step 7 — Add the MCP tool

1. Scroll to the **TOOL** section and click the **+** button.
1. In the tool picker, look for an option labelled **MCP**, **Custom MCP**, or **Model Context Protocol**.
1. Fill in the connection details:

   | Field | Value |
   |---|---|
   | Label / Name | `retail_remedy_ops` |
   | Server URL | The tunnel URL from Step 5, ending in `/mcp` |
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
   python labs/introduction-foundry-agent-service/06-mcp-tools/solution/create_agent_with_mcp.py
   ```

   Confirm `MCP_SERVER_URL` is set in `.env` before running. After the script completes, re-open `acl-remedy-advisor` in Agent Builder and verify the six tools are listed.

   **Check:** If only some tools appear (fewer than six), the server may have started with an error. Check the server terminal for error output and restart if needed.

1. Take a screenshot of the Agent Builder TOOL section showing all six MCP tool names.

---

## Part 4 — Update the agent instructions

### Step 8 — Add the MCP tool-boundary instruction

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
   warranty, policy, or stock details — call the MCP tools instead.
   ```

1. Take a screenshot of the instructions field showing the new paragraph at the bottom.

   **Check:** If the instructions field shows only the base text without the Code Interpreter paragraph from module 05, the wrong agent version is open. Confirm the header shows `v2` and re-add the missing Code Interpreter paragraph before adding the MCP paragraph.

### Step 9 — Save as v3

1. Click **Save to Foundry** in Agent Builder.
1. Wait for the confirmation notification: *Agent 'acl-remedy-advisor' updated successfully.*
1. Confirm the Agent Builder header now shows `acl-remedy-advisor | Microsoft Foundry | v3`.
1. Check the **MY RESOURCES** panel — **v3** should appear below `acl-remedy-advisor` alongside **v1** and **v2**.
1. Take a screenshot of the MY RESOURCES panel showing all three versions.

---

## Part 5 — Test with a realistic scenario

### Step 10 — Run the battery-failure test prompt

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

   **Check:** If the agent answers from general knowledge without calling any MCP tools, the instructions may not have been saved or the MCP connection may be broken. Verify the tunnel is still active and retry.

### Step 11 — Inspect the run trace

1. Open the **Run** trace in the playground or the **Runs** panel in Agent Builder.
1. Confirm MCP tool calls appear in the trace. Look for at least these three calls:
   - `lookup_purchase`
   - `get_product_profile`
   - `search_store_policy`
1. Confirm Code Interpreter is also called at least once for the pro-rata refund calculation.
1. Confirm the final response includes a clear remedy recommendation.
1. Take a screenshot of the run trace showing the MCP tool calls and Code Interpreter call.

   **Check:** If MCP tool calls do not appear in the trace, confirm the MCP tool instructions were saved (Step 9) and the MCP tool shows in the TOOL section of Agent Builder. Also confirm the server terminal shows incoming request logs during the agent run.

   **Check:** If Code Interpreter does not appear in the trace, the calculation may have been answered from general knowledge. Try adding the phrase *"Show your working using code."* to the prompt to force Code Interpreter.

---

## Part 6 (optional) — Verify from code

### Step 12 — Chat from the terminal

1. Open a second terminal in the Codespace (the server terminal from Step 2 must remain running).
1. Run the chat client:

   ```bash
   python labs/introduction-foundry-agent-service/06-mcp-tools/src/starter.py
   ```

1. Confirm the output begins with `Conversation started:` followed by a UUID-format conversation ID.
1. At the `You:` prompt, send the battery-failure prompt from Step 10.
1. Confirm `[tool: ...]` indicators appear before the final response, showing the agent called tools during the turn. Look for entries such as:
   - `[tool: mcp_call]` or similar MCP tool indicators
   - Indicators for Code Interpreter
1. Confirm the final `Advisor:` response includes a remedy recommendation with store policy and ACL guidance.
1. Type `exit` and press <kbd>Enter</kbd>. Confirm `Goodbye.` is printed and the script exits cleanly.
1. Take a screenshot of the terminal showing the conversation with tool indicators and the `Goodbye.` message.

   **Check:** If the script raises `KeyError: 'FOUNDRY_PROJECT_ENDPOINT'`, confirm `.env` is saved and that `FOUNDRY_PROJECT_ENDPOINT` is not blank.

   **Check:** If the script raises an authentication error, run `az login` in the terminal.

   **Check:** If no tool indicators appear, the agent may be using a cached version without MCP tools. Confirm `AGENT_NAME=acl-remedy-advisor` in `.env` and that v3 was saved successfully in Step 9.

---

## Validation — confirm all criteria

Work through each item in the lab's Validation section and confirm:

1. The MCP server terminal shows the startup line `Starting Retail Remedy Operations MCP server on http://0.0.0.0:8080/mcp`.
1. Port 8080 is forwarded and visible as **Public** in the PORTS panel.
1. `acl-remedy-advisor` in Agent Builder shows all six MCP tool names (`lookup_purchase`, `get_product_profile`, `search_store_policy`, `find_replacement_options`, `draft_remedy_summary`, `create_remedy_case`) in its tool list.
1. The Agent Builder header shows `acl-remedy-advisor | Microsoft Foundry | v3` after saving.
1. The battery-failure test prompt triggers at least three MCP tool calls visible in the run trace.
1. The run trace also shows Code Interpreter used for the pro-rata calculation.
1. The final response includes a remedy recommendation, a refund or replacement option, and a policy citation.
1. The MCP server terminal shows incoming request logs during the agent run.

---

## Step 13 — Report results

Report the outcome of every step above. For each step state whether it **passed** or **failed**. For any failure, include:

- The exact step number and description.
- The observed behaviour.
- The expected behaviour.
- Any error messages, unexpected output, or unexpected UI state encountered.
- The screenshot filename or description if a screenshot was taken.

If all steps pass, confirm that lab module 06 end-to-end validation is complete.
