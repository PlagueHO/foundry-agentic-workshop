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

### What you are building

The following diagram shows the architecture you will build in this lab.

![Architecture diagram: Python Client calls the acl-remedy-advisor Agent Definition inside a Foundry Project inside a Foundry Account. The Agent Definition calls the chat Model Deployment and may invoke the Web Search Tool (which calls the Internet), the Code Interpreter Tool (sandboxed Python), or the MCP Tool — which connects over an HTTPS dev tunnel to a Retail Remedy Operations MCP Server running outside the Foundry Account on the local dev machine.](../../../docs/assets/diagrams/lab-06-mcp-tools-architecture.svg)

This lab adds a **third** tool to `acl-remedy-advisor`. Unlike Web Search and Code Interpreter — which are built-in tools that run inside the **Foundry Account** — the MCP Tool is a connection to a **Retail Remedy Operations MCP Server** that runs on your **local dev machine** (`src/server.py`). Because the agent's reasoning loop runs in the Azure cloud, it cannot reach `localhost` directly; you expose the server through a public **HTTPS dev tunnel**, and the agent calls its six tools over that tunnel. During a turn the agent may combine all three tools: MCP for purchase, policy, and stock facts; Web Search for current ACCC guidance; and Code Interpreter for the pro-rata refund calculation.

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

- [ ] Make sure **VS Code Insiders** is open with the **Foundry Toolkit** extension loaded. Click the **Foundry Toolkit** icon in the Activity Bar to show the **MY RESOURCES** panel.
- [ ] In the **MY RESOURCES** panel, expand **Prompt Agents** → `acl-remedy-advisor` and open the latest version.
- [ ] Confirm the Agent Builder header shows `acl-remedy-advisor`.

  > You can also view your agents in the [Microsoft Foundry portal](https://ai.azure.com) under **Build → Agents**.

  <details>
  <summary>📸 Screenshot: Foundry portal — Agents list</summary>

  ![Foundry portal Agents list showing acl-remedy-advisor](../../../docs/assets/screenshots/introduction-foundry-agent-service/lab-06/01-agents-list.png)

  </details>

#### 7. Add the MCP tool

- [ ] Scroll to the **TOOL** section and click the **+** button.
- [ ] In the tool picker, look for an option labelled **MCP**, **Custom MCP**, or **Model Context Protocol**.
- [ ] Fill in the connection details:

  | Field | Value |
  |---|---|
  | Label / Name | `retail-remedy-ops` |
  | Server URL | The tunnel URL you copied, ending in `/mcp` |
  | Authentication | None / Anonymous |

  > [!NOTE]
  > **Naming difference between the portal and the solution script.** The portal connection name only allows letters, numbers, **dashes**, and dots — so you enter `retail-remedy-ops` (with dashes). The Python solution script (`solution/create_agent_with_mcp.py`) uses the Azure AI Agents SDK, whose `server_label` only allows letters, numbers, and **underscores** — so it uses `retail_remedy_ops` (with underscores). The two values intentionally differ because each platform enforces a different naming rule; both refer to the same MCP server.

- [ ] Confirm and save. Agent Builder discovers the tools from the server's `/mcp` endpoint.
- [ ] Verify that all six tool names appear in the tool list (`lookup_purchase`, `get_product_profile`, `search_store_policy`, `find_replacement_options`, `draft_remedy_summary`, `create_remedy_case`).

  After saving, the Foundry portal Playground view shows all three tool groups — Code Interpreter, Web Search, and the MCP server — connected to the agent:

  <details>
  <summary>📸 Screenshot: Agent playground with all tool groups connected</summary>

  ![Agent playground showing Code Interpreter, Web Search, and the retail remedy operations MCP tool connected to acl-remedy-advisor](../../../docs/assets/screenshots/introduction-foundry-agent-service/lab-06/02-agent-playground.png)

  </details>

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

#### 9. Save the new version

- [ ] Click **Save to Foundry** in Agent Builder.
- [ ] Confirm Agent Builder saves a **new version** of the agent. Saving any change — including adding the MCP tool — creates a new version. The exact number depends on how many times the agent has been saved before; for example, an agent created by the Module 05 solution script starts at **Version 1**, so this save produces **Version 2**.

### Part 5 — Test with a realistic scenario

#### 10. Run the battery-failure test prompt

- [ ] Open the playground for `acl-remedy-advisor`.
- [ ] Paste the following prompt and send it:

  ```text
  Receipt R-1007 is for a laptop bought by customer C-1042. The battery now only
  holds 20% charge after 14 months of normal use. Check our records and store
  policy, then advise the retail staff member what remedy to offer under Australian
  Consumer Law. Include any replacement options and calculate a reasonable
  pro-rata refund.
  ```

  <details>
  <summary>📸 Screenshot: Portal playground with battery-failure prompt</summary>

  ![Portal playground with the battery-failure prompt ready to send](../../../docs/assets/screenshots/introduction-foundry-agent-service/lab-06/05-playground-prompt.png)

  </details>

- [ ] Watch the run trace. Confirm the agent calls the MCP tools in sequence before producing its answer.

  > [!NOTE]
  > If the portal playground returns a `missing_required_parameter: tools[1].container` error, this means the Code Interpreter tool needs to be re-added through the Agent Builder UI (the code fallback script does not configure the container automatically). Use `starter.py` from the terminal to test instead, or remove and re-add Code Interpreter through Agent Builder.

#### 11. Approve the MCP tool calls

The first time the agent calls an MCP tool, the playground pauses and shows an **Approve / Deny** prompt. This is the MCP human-in-the-loop approval gate — the agent will not call the tool until you approve it.

- [ ] When the **Approve / Deny** prompt appears, click the dropdown arrow on the **Approve** button.
- [ ] Select **Always approve all tools** so the remaining tool calls in this run proceed without prompting you for each one.

  > [!NOTE]
  > The Approve menu also offers **Approve once** (approve this single call) and **Always approve this tool** (auto-approve future calls to this one tool). Until you save the agent with the approval preference applied, the playground may still prompt once per new tool the agent calls.

  <details>
  <summary>📸 Screenshot: MCP tool approval prompt</summary>

  ![Playground showing the Approve / Deny prompt for the lookup_purchase MCP tool call](../../../docs/assets/screenshots/introduction-foundry-agent-service/lab-06/10-mcp-approval-request.png)

  </details>

#### 12. Inspect the run trace

- [ ] Open the **Run** trace in the playground or the Runs panel.
- [ ] Confirm MCP tool calls appear in the trace (e.g., `lookup_purchase`, `get_product_profile`, `search_store_policy`).
- [ ] Confirm Code Interpreter is called to calculate the pro-rata refund.
- [ ] Confirm the final response includes a clear remedy recommendation citing store policy and ACL.

  <details>
  <summary>📸 Screenshot: Completed run with MCP tool calls</summary>

  ![Completed agent answer with the pro-rata refund calculation and the retail remedy operations MCP tool plus Code Interpreter trace chips](../../../docs/assets/screenshots/introduction-foundry-agent-service/lab-06/11-mcp-final-answer.png)

  </details>

### Part 7 (extra credit) — Browse the run trace in the Foundry portal

The **Traces** tab in the Foundry portal shows each agent conversation as a structured trace when Application Insights is connected to your Foundry project. This lets you inspect the exact sequence of MCP tool calls, model reasoning steps, and Code Interpreter invocations.

#### 14. Open the agent in the Foundry portal

- [ ] In a browser, navigate to [Microsoft Foundry](https://ai.azure.com) and sign in.
- [ ] In the left navigation, click **Build** → **Agents**.
- [ ] Click **acl-remedy-advisor** to open the agent.

  <details>
  <summary>📸 Screenshot: Foundry portal — Agents list</summary>

  ![Foundry portal Agents list showing acl-remedy-advisor](../../../docs/assets/screenshots/introduction-foundry-agent-service/lab-06/01-agents-list.png)

  </details>

#### 15. Open the Traces tab

- [ ] In the agent view, click the **Traces** tab.

  <details>
  <summary>📸 Screenshot: Traces tab for acl-remedy-advisor</summary>

  ![Traces tab for acl-remedy-advisor — shows Conversations and Responses sub-tabs](../../../docs/assets/screenshots/introduction-foundry-agent-service/lab-06/04-traces-tab.png)

  </details>

  > [!NOTE]
  > Trace data requires **Application Insights** to be connected to your Foundry project. If the Traces tab shows a "Connect" banner, click it to link an Application Insights resource. Once connected, future conversations will appear as traces automatically.

#### 16. Inspect the MCP tool call flow

- [ ] Under the **Conversations** sub-tab, click any conversation row to expand it.
- [ ] In the trace timeline, locate the MCP tool call steps — they appear as `mcp_call` entries labelled with the tool name (e.g., `lookup_purchase`, `get_product_profile`).
- [ ] Confirm the calls appear in the expected sequence: purchase lookup → product profile → store policy → replacement options → reasoning → Code Interpreter (pro-rata) → summary.
- [ ] Click any individual tool call to view the exact input payload and returned JSON.

---

### Part 6 (optional) — Verify from code

#### 13. Chat from the terminal

- [ ] In a new terminal (keep the server terminal running), start the chat client:

  ```bash
  python labs/introduction-foundry-agent-service/06-mcp-tools/src/starter.py
  ```

- [ ] Send the same battery-failure prompt.
- [ ] Confirm `[tool: ...]` indicators appear before the final response, showing the agent called tools during the turn.

---

> [!IMPORTANT]
> **Keep the MCP server and tunnel running.** Leave the server terminal open and the port 8080 tunnel set to Public. The `acl-remedy-advisor` agent uses these tools in Module 09 (Hosted Agents) and Module 10 (Foundry Toolboxes). If you need to recreate the tunnel, update `MCP_SERVER_URL` in your `.env` file and reconnect the MCP tool in Agent Builder.

---

## Validation

- The `acl-remedy-advisor` agent lists six MCP tools in its tool configuration.
- The battery-failure test prompt triggers at least three MCP tool calls visible in the run trace.
- The run trace also shows Code Interpreter used for the pro-rata calculation.
- The final response includes a remedy recommendation, a refund or replacement option, and a policy citation.
- The MCP server terminal shows incoming request logs during the agent run.

## Congratulations 🎉

You connected your agent to live, custom operations. You stood up the `retail_remedy_ops` MCP server, exposed it publicly, and wired its tools into `acl-remedy-advisor` — then watched the agent orchestrate MCP calls, Code Interpreter, and reasoning together to resolve a real battery-failure scenario end to end. Your agent can now act on domain-specific data, not just answer from general knowledge.

> [!TIP]
> **Next up → [Module 07: Ground the agent with Foundry IQ knowledge bases](../07-foundry-iq/README.md)**
> Ground your agent in trusted knowledge so its answers cite your own indexed sources. No need to scroll — jump straight in!

## Troubleshooting

- **Tools not discovered:** Confirm the MCP server is running (`http://localhost:8080/mcp` should respond) and the tunnel URL ends in `/mcp`. Restart the server if it stopped.
- **Port not reachable (403 or connection refused):** Confirm the port visibility is set to **Public** in the PORTS panel. Private ports return 403 to the Azure-hosted agent.
- **Tools are never called:** Strengthen the agent instructions — add the MCP tool-boundary paragraph from Part 4 and re-save as a new version. Use a prompt that explicitly includes a receipt ID.
- **Tool call times out:** The Agent Service times out MCP calls at 100 seconds. If the server is unresponsive, restart it and verify the tunnel is still active.
- **Tunnel URL changed:** If you recreated the tunnel, the URL changes. Update `MCP_SERVER_URL` in `.env`, edit the MCP tool connection in Agent Builder with the new URL, and re-save the agent.
- **`MCPTool` import fails in the code fallback:** Confirm `azure-ai-projects>=2.0.0` is installed (`pip install -r shared/requirements.txt`).
- **Portal playground returns `missing_required_parameter: tools[1].container`:** The code fallback script (`create_agent_with_mcp.py`) creates Code Interpreter without the container reference the portal requires. To fix: in Agent Builder, click the `⋮` menu next to Code Interpreter, remove it, then click **Add** → **Code Interpreter** to re-add it through the UI. Alternatively, test using `starter.py` from the terminal, which does not require the container reference.
