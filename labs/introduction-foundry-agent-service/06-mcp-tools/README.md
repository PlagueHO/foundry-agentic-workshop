# 06. Integrate MCP tools

**Estimated time:** 30 minutes

> [!IMPORTANT]
> This module builds on [Module 04 — Create and chat with a Prompt Agent](../04-prompt-based-agents/README.md) and
> [Module 05 — Agent tools and evaluations](../05-agent-tools-and-evaluations/README.md). Complete both modules before
> starting here. The `acl-remedy-advisor` agent must exist in your Foundry project with Web search and Code Interpreter
> tools already attached.

<!-- markdownlint-disable-next-line MD028 -->
> [!NOTE]
> If you could not complete Module 05, run the solution script to create the required agent before continuing:
>
> ```bash
> python labs/introduction-foundry-agent-service/05-agent-tools-and-evaluations/solution/create_agent.py
> ```

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Run a mocked **Retail Remedy Operations** MCP server locally.
- Expose the server publicly using a dev tunnel so the Azure-hosted agent can reach it.
- Connect the MCP server to the `acl-remedy-advisor` agent in Agent Builder.
- Update the agent instructions to guide when to call the MCP tools.
- Test the agent end-to-end with a realistic retail scenario.

## Concepts

### What is MCP?

**Model Context Protocol (MCP)** is an open standard that lets AI agents call external tools over HTTP. Each MCP server exposes a set of typed functions. When the agent's reasoning loop decides it needs information, it calls the appropriate MCP tool, receives a structured response, and incorporates that response into its answer.

### Why does the agent need a public URL?

The `acl-remedy-advisor` agent runs its reasoning loop in the **Azure cloud**. It cannot reach `localhost` or a port on your laptop. To connect the agent to a locally running MCP server you must expose the server's port through a **public HTTPS tunnel** — VS Code Dev Tunnels or Codespaces port forwarding both work.

### The Retail Remedy Operations tools

This module uses a mocked server (`src/server.py`) that returns deterministic data from a local JSON file. The six tools are:

| Tool | What it returns |
|---|---|
| `lookup_purchase` | Purchase record for a receipt ID |
| `get_product_profile` | Category, expected lifespan, warranty period, repairability |
| `search_store_policy` | Policy excerpts matching a topic keyword |
| `find_replacement_options` | In-stock comparable products with price deltas |
| `draft_remedy_summary` | Structured staff-facing remedy summary (no persistence) |
| `create_remedy_case` | Simulated case creation returning a deterministic case ID |

The tools return **facts, not verdicts**. The agent combines MCP facts with Web search (ACCC guidance) and Code Interpreter (pro-rata calculations) to produce its final guidance.

## Steps

### Part 1 — Run the MCP server locally

#### 1. Open a dedicated terminal for the server

- [ ] In VS Code, open a new terminal panel (**Terminal > New Terminal**, or press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>`</kbd>).

  > Keep this terminal open for the rest of the workshop. The MCP server must continue running while you use the agent in Modules 06 through 10.

#### 2. Start the server

- [ ] Run the following command from the repository root:

  ```bash
  python labs/introduction-foundry-agent-service/06-mcp-tools/src/server.py
  ```

  Alternatively, run the **lab06: run mcp server** task: open the Command Palette (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>), type **Run Task**, select **lab06: run mcp server**.

- [ ] Confirm the server prints:

  ```text
  Starting Retail Remedy Operations MCP server on http://0.0.0.0:8080/mcp
  ```

### Part 2 — Expose the server with a public tunnel

The agent runs in the cloud and cannot reach `localhost`. You must expose port 8080 with a **public** URL.

#### 3. Forward port 8080

- [ ] In the VS Code bottom panel, click the **PORTS** tab.
- [ ] Click **Forward a Port** (or the `+` icon) and type `8080`, then press **Enter**.
- [ ] Confirm port `8080` appears in the ports table.

#### 4. Set visibility to Public

- [ ] Right-click the `8080` row in the PORTS panel.
- [ ] Select **Port Visibility** → **Public**.
- [ ] Confirm the **Visibility** column now shows **Public**.

  > [!IMPORTANT]
  > The port **must** be set to **Public**. A private port returns a 403 when the Azure-hosted agent tries to call it.

#### 5. Copy the tunnel URL

- [ ] In the **Forwarded Address** column, click the copy icon or hover over the URL to copy it.
- [ ] The URL looks like one of these depending on your environment:
  - **VS Code Dev Tunnels** (local VS Code): `https://abc123-8080.devtunnels.ms`
  - **GitHub Codespaces**: `https://<codespace-name>-8080.app.github.dev`
- [ ] Append `/mcp` to the copied URL. For example:

  ```text
  https://abc123-8080.devtunnels.ms/mcp
  ```

- [ ] Save this full URL — you will paste it into Agent Builder in the next part.
- [ ] Optionally, set `MCP_SERVER_URL` in your `.env` file to this URL.

### Part 3 — Connect the MCP server to the agent

#### 6. Open the agent in Agent Builder

- [ ] In the Foundry Toolkit panel (**MY RESOURCES** → **Prompt Agents**), expand `acl-remedy-advisor` and open the latest version.
- [ ] Confirm the Agent Builder header shows `acl-remedy-advisor`.

#### 7. Add the MCP tool

- [ ] Scroll to the **TOOL** section and click the **+** button.
- [ ] In the tool picker, look for an option labelled **MCP**, **Custom MCP**, or **Model Context Protocol**.
- [ ] Fill in the connection details:

  | Field | Value |
  |---|---|
  | Label / Name | `retail_remedy_ops` |
  | Server URL | The tunnel URL you copied, ending in `/mcp` |
  | Authentication | None / Anonymous |

- [ ] Confirm and save. Agent Builder discovers the tools from the server's `/mcp` endpoint.
- [ ] Verify that all six tool names appear in the tool list (`lookup_purchase`, `get_product_profile`, `search_store_policy`, `find_replacement_options`, `draft_remedy_summary`, `create_remedy_case`).

> [!TIP]
> **Code fallback:** If the Agent Builder UI cannot add the MCP tool, run the code fallback script which creates a new agent version directly via the API:
>
> ```bash
> python labs/introduction-foundry-agent-service/06-mcp-tools/solution/create_agent_with_mcp.py
> ```
>
> Ensure `MCP_SERVER_URL` is set in your `.env` file before running the script.

### Part 4 — Update the agent instructions

The agent needs guidance on when to call the MCP tools. Without it the model may answer from general knowledge instead of calling the tools.

#### 8. Add the MCP tool-boundary instruction

- [ ] Scroll to the **Instructions** field in Agent Builder.
- [ ] Position your cursor at the very end of the existing instructions.
- [ ] Press **Enter** twice to create a blank line, then add the following paragraph:

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

#### 9. Save as v3

- [ ] Click **Save to Foundry** in Agent Builder.
- [ ] Confirm the version increments to **v3** (v1: Web search only; v2: + Code Interpreter; v3: + MCP tools).

### Part 5 — Test with a realistic scenario

#### 10. Run the battery-failure test prompt

- [ ] Open the playground for `acl-remedy-advisor v3`.
- [ ] Paste the following prompt and send it:

  ```text
  Receipt R-1007 is for a laptop bought by customer C-1042. The battery now only
  holds 20% charge after 14 months of normal use. Check our records and store
  policy, then advise the retail staff member what remedy to offer under Australian
  Consumer Law. Include any replacement options and calculate a reasonable
  pro-rata refund.
  ```

- [ ] Watch the run trace. Confirm the agent calls the MCP tools in sequence before producing its answer.

#### 11. Inspect the run trace

- [ ] Open the **Run** trace in the playground or the Runs panel.
- [ ] Confirm MCP tool calls appear in the trace (e.g., `lookup_purchase`, `get_product_profile`, `search_store_policy`).
- [ ] Confirm Code Interpreter is called to calculate the pro-rata refund.
- [ ] Confirm the final response includes a clear remedy recommendation citing store policy and ACL.

### Part 6 (optional) — Verify from code

#### 12. Chat from the terminal

- [ ] In a new terminal (keep the server terminal running), start the chat client:

  ```bash
  python labs/introduction-foundry-agent-service/06-mcp-tools/src/starter.py
  ```

- [ ] Send the same battery-failure prompt.
- [ ] Confirm `[tool: ...]` indicators appear before the final response, showing the agent called tools during the turn.

---

> [!IMPORTANT]
> **Keep the MCP server and tunnel running.** Leave the server terminal open and the port 8080 tunnel set to Public. The `acl-remedy-advisor` agent uses these tools in Module 07 (Foundry Toolboxes) and Module 10 (Hosted Agents). If you need to recreate the tunnel, update `MCP_SERVER_URL` in your `.env` file and reconnect the MCP tool in Agent Builder.

---

## Validation

- The `acl-remedy-advisor` agent lists six MCP tools in its tool configuration.
- The battery-failure test prompt triggers at least three MCP tool calls visible in the run trace.
- The run trace also shows Code Interpreter used for the pro-rata calculation.
- The final response includes a remedy recommendation, a refund or replacement option, and a policy citation.
- The MCP server terminal shows incoming request logs during the agent run.

## Troubleshooting

- **Tools not discovered:** Confirm the MCP server is running (`http://localhost:8080/mcp` should respond) and the tunnel URL ends in `/mcp`. Restart the server if it stopped.
- **Port not reachable (403 or connection refused):** Confirm the port visibility is set to **Public** in the PORTS panel. Private ports return 403 to the Azure-hosted agent.
- **Tools are never called:** Strengthen the agent instructions — add the MCP tool-boundary paragraph from Part 4 and re-save as a new version. Use a prompt that explicitly includes a receipt ID.
- **Tool call times out:** The Agent Service times out MCP calls at 100 seconds. If the server is unresponsive, restart it and verify the tunnel is still active.
- **Tunnel URL changed:** If you recreated the tunnel, the URL changes. Update `MCP_SERVER_URL` in `.env`, edit the MCP tool connection in Agent Builder with the new URL, and re-save the agent.
- **`MCPTool` import fails in the code fallback:** Confirm `azure-ai-projects>=2.0.0` is installed (`pip install -r shared/requirements.txt`).
