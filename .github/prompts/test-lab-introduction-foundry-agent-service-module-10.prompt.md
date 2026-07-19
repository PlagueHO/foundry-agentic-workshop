---
description: "Test lab module 10 (Foundry Toolboxes) end-to-end from a local terminal and the Foundry portal, verifying every step carefully. Requires a provisioned lab environment, the repository checked out locally, a configured .env with FOUNDRY_PROJECT_ENDPOINT and RETAIL_REMEDY_OPS_MCP_SERVER_URL, and an authenticated Azure CLI session signed in as the lab attendee. Opens the ai.azure.com portal using open_browser_page."
---

## Inputs

- ${input:attendeeUpn}: (Required) The UPN of the attendee to test with (e.g. `lab.attendee.1@MngEnvMCAP199525.onmicrosoft.com`).
- ${input:envName}: (Required) The azd environment name the lab was provisioned into (e.g. `foundry-hol8`).

---

You must test the steps in the #file:labs/introduction-foundry-agent-service/10-foundry-toolboxes/README.md from a local terminal in this repository. The attendee is `${input:attendeeUpn}` in the provisioned environment `${input:envName}`.

This module bundles the **Retail Remedy Operations MCP server**, **Web Search**, and **Code Interpreter** into a single **Foundry Toolbox** managed through the portal, enables **Tool Search**, and then deploys and invokes a toolbox-wired hosted agent built with the Python **Microsoft Agent Framework**. The test creates the toolbox in the portal (with a Python SDK fallback), deploys the hosted agent from source code, invokes it, and verifies the response includes a Tool Search–driven remedy recommendation.

The lab environment must already be provisioned and the Azure CLI must already be signed in as the attendee. Use `open_browser_page` to open `https://ai.azure.com` and authenticate as the attendee to confirm the toolbox and verify the portal state.

> **Important:** Any Azure login dialogs that appear during the test must be completed by the user. Pause and prompt the user whenever a sign-in dialog is encountered. Do not attempt to enter credentials automatically.

## Pre-flight - Verify the environment is ready

Before executing any lab steps, confirm all prerequisites are satisfied. **Do not proceed if any check fails** - report the failure and ask the user to resolve it.

### Check 1 - Confirm the repository and scripts are present

1. In a terminal at the repository root, confirm the module 10 scripts exist:

   ```bash
   ls labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/setup_toolbox.py
   ls labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/deploy_hosted_agent_code.py
   ls labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/invoke_hosted_agent.py
   ```

1. Confirm all paths resolve without error.

### Check 2 - Confirm dependencies are installed

1. Confirm the shared dependencies are installed by running `uv sync` from the repo root if not already done:

   ```bash
   uv sync
   ```

1. Confirm the Azure AI Projects SDK imports cleanly:

   ```bash
   uv run python -c "from azure.ai.projects import AIProjectClient; print('azure.ai.projects OK')"
   ```

   **Check:** If the import raises `ModuleNotFoundError`, run `uv sync` from the repo root and retry.

### Check 3 - Confirm the `.env` file exists and contains required values

1. Confirm `.env` exists and the required toolbox values are populated:

   ```bash
   cat .env | grep -E 'FOUNDRY_PROJECT_ENDPOINT|RETAIL_REMEDY_OPS_MCP_SERVER_URL|TOOLBOX_NAME|AZURE_SUBSCRIPTION_ID|AZURE_RESOURCE_GROUP|FOUNDRY_RESOURCE_NAME'
   ```

1. Confirm `FOUNDRY_PROJECT_ENDPOINT` is set to a non-empty value of the form `https://<resource>.services.ai.azure.com/api/projects/<project>`.
1. Confirm `RETAIL_REMEDY_OPS_MCP_SERVER_URL` is set to a non-empty public URL ending in `/mcp` (the Module 06 MCP server endpoint).
1. Confirm `TOOLBOX_NAME` is either unset (defaults to `acl-remedy-toolbox`) or set to `acl-remedy-toolbox`.

   **Check:** If `.env` does not exist, confirm with the user that Module 01 has been completed, then copy `shared/.env.example` to `.env` and populate the values from the attendee onboarding file at `.azure/${input:envName}/<upn_local>.md` (where `<upn_local>` is the part of `${input:attendeeUpn}` before `@`), or from `azd env get-values`.

### Check 4 - Confirm the Module 06 MCP server is running and publicly exposed

The toolbox wraps the **Retail Remedy Operations MCP server** from Module 06. It must be running and reachable on its public URL for toolbox creation and the consumer script to succeed.

1. Confirm `RETAIL_REMEDY_OPS_MCP_SERVER_URL` points to a **public** URL (ending in `/mcp`), not a `localhost` address - the toolbox endpoint runs in Foundry's managed infrastructure and cannot reach `localhost`.
1. Confirm the public endpoint responds:

   ```bash
   curl -i -X POST "$RETAIL_REMEDY_OPS_MCP_SERVER_URL" -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
   ```

   **Check:** Expect an HTTP `200` with a JSON-RPC response listing the `retail_remedy_ops` tools: `lookup_purchase`, `get_product_profile`, `search_store_policy`, `find_replacement_options`, `draft_remedy_summary`, `create_remedy_case`. If the request fails or times out, restart the Module 06 server, re-expose the dev tunnel publicly, and update `RETAIL_REMEDY_OPS_MCP_SERVER_URL` before continuing.

### Check 5 - Confirm Azure authentication

1. Confirm the Azure CLI is signed in as the attendee:

   ```bash
   az account show --query '{user:user.name, subscription:id}' -o table
   ```

1. Confirm the output shows `${input:attendeeUpn}` as the signed-in user.
1. If the command fails or shows a different identity, pause and ask the user to run `az login` and complete the browser sign-in before continuing. Do not enter credentials automatically.

### Check 6 - Open the Foundry portal

1. Use `open_browser_page` to navigate to `https://ai.azure.com`.
1. If a login dialog appears, pause and ask the user to sign in as `${input:attendeeUpn}`. Do not enter credentials automatically.
1. Navigate to the attendee's Foundry project and confirm the portal loads.
1. Note whether `acl-remedy-toolbox` already exists in the Toolboxes area (from a prior run) so you can distinguish a fresh creation later.

---

## Part 1 - Confirm the MCP server URL

### Step 1 - Verify RETAIL_REMEDY_OPS_MCP_SERVER_URL in .env

1. Open the `.env` file and confirm `RETAIL_REMEDY_OPS_MCP_SERVER_URL` is set to the shared server URL ending in `/mcp`. For example:

   ```text
   https://ca-mcp-<env>.<region>.azurecontainerapps.io/mcp
   ```

1. Save this URL - it is pasted into the toolbox configuration in Part 2.

   > **Note:** If you are running your own MCP server instead of the shared one, confirm it is still running with port 8080 set to **Public** and use its tunnel URL as your `RETAIL_REMEDY_OPS_MCP_SERVER_URL`. See Module 06, Part 1.

---

## Part 2 - Create the toolbox in the Foundry portal

> **Note:** If **Toolboxes** is not visible in the portal navigation below, skip to the [code fallback](#code-fallback---create-the-toolbox-with-python) at the end of this part.

### Step 2 - Navigate to Toolboxes

1. In the browser opened in Check 6, navigate to the attendee's Foundry project.
1. In the left navigation, click **Build**.
1. Under **Build**, click **Tools**.
1. Select the **Toolboxes** tab.
1. Take a screenshot of the Toolboxes page.

   **Check:** If **Toolboxes** is not visible in the navigation, record this step as **skipped (Toolboxes not in portal)** and proceed to the code fallback.

### Step 3 - Create the toolbox

1. Click **+ Create** or **+ New toolbox**.
1. Enter the following details:

   | Field | Value |
   |---|---|
   | Name | `acl-remedy-toolbox` |
   | Description | `Retail Remedy operations tools, web search, and code interpreter for ACCC and ACL guidance` |

1. Take a screenshot of the filled-in creation form.

### Step 4 - Add the Web Search tool

1. In the tool configuration area, click **+ Add tool**.
1. Select **Web Search** from the tool picker.
1. In the tool **Description** field, enter:

   ```text
   Search the web for ACCC rulings, Australian Consumer Law guidance, and current retail policy information.
   ```

1. Confirm the Web Search tool appears in the toolbox configuration.

### Step 5 - Add the MCP tool

1. Click **+ Add tool** again.
1. Select **MCP** (or **Model Context Protocol** / **Custom MCP**) from the tool picker.
1. Fill in the connection details:

   | Field | Value |
   |---|---|
   | Label / Server name | `retail_remedy_ops` |
   | Server URL | Your `RETAIL_REMEDY_OPS_MCP_SERVER_URL` (ending in `/mcp`) |
   | Authentication | None / Anonymous |
   | Description | `Retail Remedy Operations tools for looking up purchases, product profiles, store policies, replacement options, and creating remedy cases.` |

1. Confirm the six MCP tools are discovered from the server: `lookup_purchase`, `get_product_profile`, `search_store_policy`, `find_replacement_options`, `draft_remedy_summary`, `create_remedy_case`.
1. Take a screenshot showing the MCP tool added with its discovered tools listed.

   **Check:** If the MCP tools are not discovered, confirm the MCP server is still running and `RETAIL_REMEDY_OPS_MCP_SERVER_URL` is publicly accessible. Restart the server and re-expose the tunnel if needed, then retry tool discovery.

### Step 6 - Add the Code Interpreter tool

1. Click **+ Add tool** again.
1. Select **Code Interpreter** from the tool picker.
1. Confirm the toolbox now lists all three tools: **Web Search**, the `retail_remedy_ops` MCP server, and **Code Interpreter**.
1. Take a screenshot showing all three tools configured.

### Step 7 - Enable Tool Search

1. Locate the **Tool search** toggle or checkbox in the toolbox configuration.
1. Enable it.
1. Confirm the toggle is enabled.

   **Check:** If the **Tool search** toggle is not visible, the preview feature may not be available in this region. Record this in the results report and continue - the hosted agent will attempt to use it regardless.

### Step 8 - Publish the toolbox and set it as the default version

1. Click **Publish** (or **Save** / **Create**).
1. Confirm a toolbox named `acl-remedy-toolbox` is created.
1. Confirm the published version is set as the **default** version. The consumer endpoint resolves `?api-version=v1` to the default version, so this must be set for the app in Part 3 to connect.
1. Take a screenshot of the toolbox list showing `acl-remedy-toolbox` published with a default version set.

   **Check:** If the published version is not automatically set as the default, locate the version in the toolbox and set it as the default manually before continuing.

### Step 9 - Confirm the toolbox MCP endpoint

1. After publishing, locate the **Consumer endpoint** URL for `acl-remedy-toolbox`. It has the form:

   ```text
   https://<account>.services.ai.azure.com/api/projects/<project>/toolboxes/acl-remedy-toolbox/mcp?api-version=v1
   ```

1. Confirm the endpoint URL is visible in the portal. The hosted agent builds this URL automatically from `FOUNDRY_PROJECT_ENDPOINT` and `TOOLBOX_NAME` at runtime, so you do not need to paste it anywhere - but confirm it matches the pattern above.

#### Code fallback - Create the toolbox with Python

> If the portal does not expose Toolboxes in your region, or you skipped the portal steps above, run the fallback script to create the toolbox through the Python SDK. `RETAIL_REMEDY_OPS_MCP_SERVER_URL` must be set in your `.env` file.
>
> ```bash
> uv run python labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/setup_toolbox.py
> ```
>
> The script creates the `acl-remedy-toolbox` toolbox with Web Search, the `retail_remedy_ops` MCP server, Code Interpreter, and Tool Search enabled, then prints the consumer endpoint URL.

1. Run the fallback script and confirm it exits cleanly with a printed consumer endpoint URL.
1. Navigate to the Toolboxes area in the portal (if available) and confirm `acl-remedy-toolbox` appears with a default version set. If the portal does not show it, set the new version as the default using the portal before continuing with Part 3.

---

## Part 3 - Deploy and invoke the toolbox-wired hosted agent

### Step 10 - Review the agent bundle

1. Open `labs/introduction-foundry-agent-service/10-foundry-toolboxes/src/agent/main.py` and confirm:
   - The toolbox MCP endpoint is built as `{FOUNDRY_PROJECT_ENDPOINT}/toolboxes/{TOOLBOX_NAME}/mcp?api-version=v1`.
   - The endpoint is wrapped in an `MCPStreamableHTTPTool` backed by an `httpx.AsyncClient` with a `_ToolboxAuth` handler that fetches a fresh Entra bearer token (scope `https://ai.azure.com/.default`) on every request.
   - The `httpx.AsyncClient` does **not** contain a `Foundry-Features` header (toolboxes are GA — only the bearer token is required).
   - The agent instructions tell the model to call `tool_search` when a needed tool is not already visible.
   - `load_prompts=False` is passed to `MCPStreamableHTTPTool` (the toolbox endpoint does not implement `prompts/list`).

1. Open `labs/introduction-foundry-agent-service/10-foundry-toolboxes/src/agent/agent.yaml` and confirm it declares `acl-remedy-advisor-hosted` with the Responses protocol and the environment variables `AZURE_AI_MODEL_DEPLOYMENT_NAME` and `TOOLBOX_NAME`.

   **Check:** If `Foundry-Features` still appears in `main.py`, report this as a failure — it was removed when toolboxes reached GA.

### Step 11 - Confirm the required environment variables

1. Confirm the `.env` file sets all variables required by the deploy script:

   ```bash
   cat .env | grep -E 'FOUNDRY_PROJECT_ENDPOINT|AZURE_SUBSCRIPTION_ID|AZURE_RESOURCE_GROUP|FOUNDRY_RESOURCE_NAME|TOOLBOX_NAME'
   ```

1. Confirm `FOUNDRY_PROJECT_ENDPOINT` is a non-empty value of the form `https://<resource>.services.ai.azure.com/api/projects/<project>`.
1. Confirm `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, and `FOUNDRY_RESOURCE_NAME` are all non-empty (the deploy script uses them to grant the **Foundry User** role to the agent's per-deploy identity).
1. Confirm `TOOLBOX_NAME` is `acl-remedy-toolbox` or unset (defaults to the same).

   **Check:** If any required variable is missing or empty, report it and stop.

### Step 12 - Deploy the agent from source code

1. From the repository root, run the deploy script:

   ```bash
   uv run python labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/deploy_hosted_agent_code.py
   ```

1. Let the script run to completion. The remote build takes several minutes. The script zips `src/agent/`, uploads it, and polls until the version reports **active**. It then grants the agent's per-deploy Entra identity the **Foundry User** role so it can call the model and the toolbox.
1. Confirm the script prints `Agent version is now active.` and exits cleanly with no traceback.

   **Check:** If the script errors with a missing environment variable, confirm `.env` is populated (Step 11).

   **Check:** If the build never becomes active, open the Foundry portal, navigate to **Agents → acl-remedy-advisor-hosted-code**, open the version, and check the build logs. A failed remote build usually means a broken dependency in `requirements.txt`. Report the full error message.

   **Check:** If authentication fails with a `401` or `403`, run `az login` and retry.

### Step 13 - View the agent in the portal

1. In the browser, navigate to the attendee's Foundry project and click **Agents** in the left navigation.
1. Confirm `acl-remedy-advisor-hosted-code` appears in the Agents list.
1. Open the agent and confirm:
   - **Kind** shows **hosted**.
   - The new version is listed as **active**.
1. Take a screenshot of the Agents list and a screenshot of the agent detail page with the new version active.

   **Check:** If `acl-remedy-advisor-hosted-code` is not visible, confirm Step 12 completed successfully and reload the portal.

### Step 14 - Invoke the agent from code

1. From the repository root, run the invoke script:

   ```bash
   uv run python labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/invoke_hosted_agent.py
   ```

1. Let the script run to completion. The script selects the latest active version, opens an agent session, routes 100% of traffic to the new version, and runs a two-turn Australian Consumer Law conversation for receipt `R-1007` (a laptop battery that failed about 14 months after a 12-month warranty).
1. Confirm the script exits cleanly with no traceback.
1. Confirm the first-turn response:
   - References receipt `R-1007` and store policy retrieved through the `retail_remedy_ops` tools.
   - Applies Australian Consumer Law reasoning (distinguishes a major or minor failure and states the appropriate remedy).
   - Recommends a concrete next step for the customer.
1. Confirm the second turn builds on context from the first (the customer still has the original box and charger).

   **Check:** If the connection drops with `MCP server failed to initialize` or `Cancelled via cancel scope`, the toolbox endpoint had a cold start. Re-run the script.

   **Check:** If authentication fails with a `401` or `403`, run `az login` and retry.

   **Check:** If the response does not reference receipt `R-1007` or `retail_remedy_ops` data, confirm Tool Search is enabled on the default toolbox version and tool descriptions are specific. Publish a new version with improved descriptions, set it as the default, and rerun.

### Step 15 - Review the run traces and metrics

1. In the browser, open `acl-remedy-advisor-hosted-code` in the Foundry portal and select the **Traces** tab.
1. Open the most recent run and expand the trajectory.
1. Confirm the trace shows a `tool_search` span followed by one or more `call_tool` spans dispatching `retail_remedy_ops` lookups. This confirms Tool Search discovered the tools and invoked them through the toolbox.
1. Take a screenshot of the trace view showing the `tool_search` → `call_tool` flow.
1. Select the **Monitor** tab and confirm the run appears in the operational charts (agent runs, token usage, tool calls).
1. Take a screenshot of the Monitor dashboard.

   **Check:** If no traces appear, wait 1–2 minutes and refresh — traces may be delayed. If they still do not appear, confirm the invoke script exited cleanly in Step 14.

---

## Validation - confirm all criteria

Work through each item in the lab's Validation section and confirm:

1. The `acl-remedy-toolbox` toolbox exists in the Foundry project containing **Web Search**, the `retail_remedy_ops` MCP server, and **Code Interpreter**, with **Tool Search** enabled and a default version set.
1. `python labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/deploy_hosted_agent_code.py` publishes a new version of `acl-remedy-advisor-hosted-code` that reports **active**.
1. The new version appears in the portal **Agents** view for `acl-remedy-advisor-hosted-code` with kind **hosted**.
1. `python labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/invoke_hosted_agent.py` runs to completion and prints a clear remedy recommendation citing store policy and Australian Consumer Law, and recommending the appropriate remedy.
1. The portal **Traces** view for `acl-remedy-advisor-hosted-code` shows a `tool_search` span followed by `call_tool` spans confirming Tool Search drove tool discovery through the toolbox.

---

## Step 16 - Report results

Report the outcome of every step above. For each step state whether it **passed**, **failed**, or was **skipped** (with the reason, for example Toolboxes not visible in portal for Steps 2–9). For any failure, include:

- The exact step number and description.
- The observed behaviour.
- The expected behaviour.
- Any error messages, unexpected output, or unexpected portal state encountered.
- The screenshot filename or description for any screenshot taken.

If all non-skipped steps pass, confirm that lab module 10 end-to-end validation is complete.
