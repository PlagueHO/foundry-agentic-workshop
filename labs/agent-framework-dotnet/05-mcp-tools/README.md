# 05. MCP Tools

**Estimated time:** 20 minutes

![Microsoft Agent Framework overview: an open-source engine for building and orchestrating AI agents, summarised in five pillars — Unified SDK (AIAgent, AgentThread, and AgentTool primitives built on Microsoft.Extensions.AI), Local-first and cloud-agnostic (run agents locally then move the same code to Foundry Agent Service or any cloud containers), Multi-agent orchestration (sequential, concurrent, handoff, group chat, magentic, and workflow patterns), Tools and extensibility (out-of-the-box integrations plus functions, APIs, and MCP servers as tools), and Enterprise-grade foundations (approval flows, content-policy hooks, OpenTelemetry observability, and long-running execution).](../../../docs/assets/diagrams/agent-framework-introduction.png)

> [!IMPORTANT]
> This module builds on [Module 04](../04-function-tools/README.md). The function-tool pattern is replaced here with a remote MCP server. You need Python 3.13 installed to start the `flight-ops` MCP server.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Start the local `flight-ops` Python MCP server.
- Connect the agent to the server using `McpServer` from `Microsoft.Agents.AI.Mcp`.
- Attach the MCP toolset to the agent with `.WithMcpTools()`.
- Watch the agent call `get_flight_status` and `get_rebooking_options` remotely.

## Concepts

### What is the Model Context Protocol?

The **[Model Context Protocol](https://modelcontextprotocol.io/)** (MCP) is an open standard for exposing tools, resources, and prompts to language models over HTTP. An MCP server publishes a list of tools — each with a name, description, and typed parameters — that any MCP client can discover and call.

Instead of writing a local C# function (as in Module 04), you point the agent at a remote server and it discovers the available tools automatically. This means the tool logic can live in Python, Node.js, or any language — and can be updated without redeploying your agent code.

### McpServer and WithMcpTools

The framework provides `McpServer` to represent a connection to an MCP server and `.WithMcpTools()` to attach its tools to the agent:

```csharp
var mcpServer = new McpServer(new Uri("http://localhost:3001/mcp"));
var agent = client
    .AsAIAgent(model: model, instructions: "...")
    .WithMcpTools(mcpServer);
```

When the model decides to call a tool, the framework sends a JSON-RPC request to the MCP server, waits for the result, and injects it back into the conversation — exactly as it does for local function tools.

### flight-ops MCP server

The `flight-ops` server is a small Python MCP server that exposes two tools:

| Tool | What it returns |
|---|---|
| `get_flight_status` | Current status, gate, and estimated departure for a flight |
| `get_rebooking_options` | Available alternative flights for a disrupted passenger |

The server is located in `shared/mcp-servers/flight-ops/src/server.py` and listens on `http://localhost:3001/mcp` by default.

## Steps

### Part 1 — Start the MCP server

#### 1. Start the flight-ops server

- [ ] Open a separate terminal and run:

  ```bash
  python shared/mcp-servers/flight-ops/src/server.py
  ```

- [ ] Confirm the server outputs a startup message with no errors.

  > [!NOTE]
  > Keep this terminal open for the rest of the module. If you close it, the agent will fail with a connection error.

### Part 2 — Complete the starter code

#### 2. Open the starter file

- [ ] Open `src/Program.cs` in the editor.

#### 3. Read the MCP server URL (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  var mcpUrl = Environment.GetEnvironmentVariable("FLIGHT_OPS_MCP_SERVER_URL")
      ?? "http://localhost:3001/mcp";

  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine($"[Loop] MCP server URL: {mcpUrl}");
  Console.ResetColor();
  Console.WriteLine();
  ```

  If `FLIGHT_OPS_MCP_SERVER_URL` is not in your `.env`, the code defaults to `localhost:3001`.

#### 4. Create the McpServer (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
  var mcpServer = new McpServer(new Uri(mcpUrl));

  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Loop] Connecting to flight-ops MCP server...");
  Console.ResetColor();
  ```

#### 5. Create the agent with MCP tools (TODO 3)

- [ ] Locate `// ── TODO 3` and replace the commented-out block with:

  ```csharp
  var credential = new DefaultAzureCredential();
  var client = new AIProjectClient(new Uri(endpoint), credential);
  var agent = client
      .AsAIAgent(
          model: model,
          instructions:
              "You are the Trip Disruption Concierge. You have access to the " +
              "flight operations system. When passengers ask about flight status " +
              "or rebooking, call the appropriate MCP tool to get live data " +
              "before responding.")
      .WithMcpTools(mcpServer);

  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Loop] Agent ready — MCP tools loaded from server.");
  Console.ResetColor();
  Console.WriteLine();
  ```

#### 6. Run a prompt that exercises both tools (TODO 4)

- [ ] Locate `// ── TODO 4` and replace the commented-out block with the prompt code already commented out there.

### Part 3 — Run and verify

#### 7. Run the starter

- [ ] In a second terminal (keep the MCP server running), run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/05-mcp-tools/src/TripConcierge.McpTools.csproj
  ```

## Validation

- The terminal shows the agent calling `get_flight_status` (yellow `[MCP Tool]` line).
- The server's own output confirms the tool was invoked.
- The final response includes live flight status and rebooking options.

## Congratulations 🎉

You replaced the local function tool with a remote MCP server. The agent discovered the available tools at startup, called them over HTTP when the model needed live data, and incorporated the results into its final response — all without changing your agent setup code.

> [!TIP]
> **Next up → [Module 06: Knowledge Bases](../06-knowledge-bases/README.md)**
> Ground the agent in a pre-seeded Azure AI Search index using a custom `AIContextProvider` that retrieves relevant policy documents before every model call.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Connection refused` on `localhost:3001` | Start the Python MCP server first (see Step 1) |
| `FLIGHT_OPS_MCP_SERVER_URL is not set` | Add the variable to `.env` in the repository root |
| MCP tools not called | Confirm the server started without errors; check its terminal window |
| `NotImplementedException` | A TODO is still incomplete |
