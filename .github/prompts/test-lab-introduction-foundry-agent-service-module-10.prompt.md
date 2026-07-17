---
description: "Test lab module 10 (Build and consume a Foundry Toolbox) end-to-end from a local terminal and the Foundry portal, verifying every step carefully. Requires a provisioned lab environment, the repository checked out locally, a configured .env with FOUNDRY_PROJECT_ENDPOINT and RETAIL_REMEDY_OPS_MCP_SERVER_URL, and an authenticated Azure CLI session signed in as the lab attendee. Opens the ai.azure.com portal using open_browser_page."
---

## Inputs

- ${input:attendeeUpn}: (Required) The UPN of the attendee to test with (e.g. `lab.attendee.1@MngEnvMCAP199525.onmicrosoft.com`).
- ${input:envName}: (Required) The azd environment name the lab was provisioned into (e.g. `foundry-hol8`).

---

You must test the steps in the #file:labs/introduction-foundry-agent-service/10-foundry-toolboxes/README.md from a local terminal in this repository. The attendee is `${input:attendeeUpn}` in the provisioned environment `${input:envName}`.

This module bundles the **Retail Remedy Operations MCP server**, **Web Search**, and **Code Interpreter** into a single **Foundry Toolbox** managed through the portal, enables **Tool Search**, and then consumes the toolbox from a Python **Microsoft Agent Framework** app. The test creates the toolbox in the portal (with a Python SDK fallback), runs the consumer script, and verifies the response includes a Tool Search–driven remedy recommendation.

The lab environment must already be provisioned and the Azure CLI must already be signed in as the attendee. Use `open_browser_page` to open `https://ai.azure.com` and authenticate as the attendee to confirm the toolbox and verify the portal state.

> **Important:** Any Azure login dialogs that appear during the test must be completed by the user. Pause and prompt the user whenever a sign-in dialog is encountered. Do not attempt to enter credentials automatically.

## Pre-flight - Verify the environment is ready

Before executing any lab steps, confirm all prerequisites are satisfied. **Do not proceed if any check fails** - report the failure and ask the user to resolve it.

### Check 1 - Confirm the repository and scripts are present

1. In a terminal at the repository root, confirm the module 10 scripts exist:

   ```bash
   ls labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/setup_toolbox.py
   ls labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/consume_toolbox.py
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
   cat .env | grep -E 'FOUNDRY_PROJECT_ENDPOINT|RETAIL_REMEDY_OPS_MCP_SERVER_URL|TOOLBOX_NAME'
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

> **Note:** The Toolboxes portal UI is in preview. If **Toolboxes** is not visible in the portal navigation, skip to the [code fallback](#code-fallback---create-the-toolbox-with-python) at the end of this part.

### Step 2 - Navigate to Toolboxes

1. In the browser opened in Check 6, navigate to the attendee's Foundry project.
1. In the left navigation, click **Build**.
1. Look for a **Toolboxes** entry under **Build** (it may also appear under **Build → Agents → Tools** or **Build → Tools**).
1. Click **Toolboxes** to open the toolbox management view.
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

   **Check:** If the **Tool search** toggle is not visible, the preview feature may not be available in this region. Record this in the results report and continue - the consumer script will attempt to use it regardless.

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

1. Confirm the endpoint URL is visible in the portal. The consumer script builds this URL automatically from `FOUNDRY_PROJECT_ENDPOINT` and `TOOLBOX_NAME`, so you do not need to paste it anywhere - but confirm it matches the pattern above.

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

## Part 3 - Consume the toolbox with the Microsoft Agent Framework

### Step 10 - Confirm the environment and sign-in are still active

1. Confirm `uv sync` has been run and dependencies are available (Check 2 above).
1. Confirm the Azure CLI session is still valid:

   ```bash
   az account show --query '{user:user.name}' -o table
   ```

   **Check:** If the session has expired, pause and ask the user to run `az login` and complete the browser sign-in before continuing.

### Step 11 - Confirm the required environment variables

1. Confirm `FOUNDRY_PROJECT_ENDPOINT` and `TOOLBOX_NAME` are set in `.env`:

   ```bash
   cat .env | grep -E 'FOUNDRY_PROJECT_ENDPOINT|TOOLBOX_NAME'
   ```

1. Confirm `FOUNDRY_PROJECT_ENDPOINT` is a non-empty value and `TOOLBOX_NAME` is `acl-remedy-toolbox` (or unset, which defaults to `acl-remedy-toolbox`).

### Step 12 - Review the consumer script

1. Open `labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/consume_toolbox.py`.
1. Confirm it wraps the toolbox MCP endpoint in an `MCPStreamableHTTPTool` backed by an `httpx.AsyncClient` that adds a fresh Microsoft Entra bearer token (scope `https://ai.azure.com/.default`) and the `Foundry-Features: Toolboxes=V1Preview` header to every request, including the connection handshake.
1. Confirm the agent instructions tell the model to call `tool_search` when a needed tool is not already visible, before responding that it cannot help.
1. Confirm the script retries the connection on failure to handle cold-start drops (`CONNECT_ATTEMPTS = 3` with a backoff).
1. Confirm the built-in query sends receipt `R-1007` (a ProBook 14 laptop battery that stopped holding charge 14 months after purchase against a 12-month standard warranty).

### Step 13 - Run the consumer script

1. From the repository root, run:

   ```bash
   uv run python labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/consume_toolbox.py
   ```

1. Let the script run to completion. Retry messages are expected on cold start and do not indicate failure.
1. Confirm the script prints a remedy recommendation and exits cleanly with no traceback.

   **Check:** If every connection attempt fails with `MCP server failed to initialize` or `Cancelled via cancel scope`, confirm the toolbox has a default version set and the MCP server is still running and publicly accessible. Retry after confirming both.

   **Check:** If authentication fails with a 401 or 403, run `az login` and retry.

   **Check:** If the script raises `KeyError` or `ValueError` for a missing environment variable, confirm `FOUNDRY_PROJECT_ENDPOINT` and `TOOLBOX_NAME` are set in `.env`.

### Step 14 - Confirm Tool Search drove the response

1. Confirm the printed remedy recommendation:
   - References the customer's purchase and relevant store policy retrieved through the `retail_remedy_ops` tools (for example, the `R-1007` receipt and store warranty policy).
   - Applies Australian Consumer Law reasoning, distinguishing a major or minor failure and stating the appropriate remedy.
   - Includes a calculated figure (such as a pro-rata refund amount) produced by Code Interpreter, confirming Code Interpreter was invoked through the toolbox.

1. Confirm the response is grounded in tool results rather than generic - the agent must have called `tool_search` to discover the retail tools and then called them through `call_tool`.

   **Check:** If the response is generic and does not reference the purchase or Australian Consumer Law, confirm the Web Search and MCP tools have clear, specific descriptions in the toolbox definition and that Tool Search is enabled on the default version. Publish a new toolbox version with improved descriptions and set it as the default, then rerun the script.

---

## Validation - confirm all criteria

Work through each item in the lab's Validation section and confirm:

1. The `acl-remedy-toolbox` toolbox exists in the Foundry project containing **Web Search**, the `retail_remedy_ops` MCP server, and **Code Interpreter**, with **Tool Search** enabled and a default version set.
1. `python labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/consume_toolbox.py` connects to the toolbox endpoint and runs to completion without error.
1. The printed response includes a clear remedy recommendation citing store policy and Australian Consumer Law.
1. The response includes a calculated figure (such as a pro-rata refund) produced by Code Interpreter, confirming the toolbox exposed all three tools through Tool Search.

---

## Step 15 - Report results

Report the outcome of every step above. For each step state whether it **passed**, **failed**, or was **skipped** (with the reason, for example Toolboxes not visible in portal for Steps 2–9). For any failure, include:

- The exact step number and description.
- The observed behaviour.
- The expected behaviour.
- Any error messages, unexpected output, or unexpected portal state encountered.
- The screenshot filename or description for any screenshot taken.

If all non-skipped steps pass, confirm that lab module 10 end-to-end validation is complete.
