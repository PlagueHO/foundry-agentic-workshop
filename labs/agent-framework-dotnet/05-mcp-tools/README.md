---
title: '05. MCP Tools'
description: 'Complete this lab to mcp tools.'
lastUpdated: '2026-07-13'
track: 'agent-framework-dotnet'
module: 5
slug: '05-mcp-tools'
estimatedTimeMinutes: 25
difficulty: 'intermediate'
prerequisites: ['Module 04']
audience:
  - 'attendee'
technologies:
  - 'Microsoft Agent Framework'
  - 'Microsoft Foundry'
tags:
  - 'agent-framework'
  - 'mcp'
  - 'tools'
status: 'active'
contentType: 'lab'
---
# 05. MCP Tools

**Estimated time:** 25 minutes

![Microsoft Agent Framework overview: an open-source engine for building and orchestrating AI agents, summarised in five pillars - Unified SDK (AIAgent, AgentThread, and AgentTool primitives built on Microsoft.Extensions.AI), Local-first and cloud-agnostic (run agents locally then move the same code to Foundry Agent Service or any cloud containers), Multi-agent orchestration (sequential, concurrent, handoff, group chat, magentic, and workflow patterns), Tools and extensibility (out-of-the-box integrations plus functions, APIs, and MCP servers as tools), and Enterprise-grade foundations (approval flows, content-policy hooks, OpenTelemetry observability, and long-running execution).](../../../docs/assets/diagrams/agent-framework-introduction.png)

> [!IMPORTANT]
> This module builds on [Module 04](../04-function-tools/README.md). The function-tool pattern is replaced here with a remote MCP server. You need Python 3.13 installed to start the `flight-ops` MCP server.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Start the `flight-ops` Python MCP server.
- Connect to the server with `McpClient` and `HttpClientTransport` from `ModelContextProtocol.Client`.
- Discover available tools with `ListToolsAsync()` and pass them to the agent via the `tools:` parameter.
- Watch the agent call `get_flight_status` and `get_rebooking_options` remotely.
- Use a multi-turn session to file a compensation claim for the disrupted flight.

## Concepts

### What is the Model Context Protocol?

The **[Model Context Protocol](https://modelcontextprotocol.io/)** (MCP) is an open standard for exposing tools, resources, and prompts to language models over HTTP. An MCP server publishes a list of tools - each with a name, description, and typed parameters - that any MCP client can discover and call.

Instead of writing a local C# function (as in Module 04), you point the agent at a remote server and it discovers the available tools automatically. This means the tool logic can live in Python, Node.js, or any language - and can be updated without redeploying your agent code.

### McpClient and tool discovery

The `ModelContextProtocol` package provides `McpClient` to connect to an MCP server over HTTP. `HttpClientTransport` configures the streamable-HTTP transport; `ListToolsAsync()` fetches the server's tool manifest at startup:

```csharp
await using var mcpClient = await McpClient.CreateAsync(
    new HttpClientTransport(new() { Endpoint = new Uri(mcpUrl), Name = "flight-ops" }));
IList<McpClientTool> mcpTools = await mcpClient.ListToolsAsync();
```

Each `McpClientTool` implements `AITool`, so the list can be spread directly into the agent's `tools:` parameter:

```csharp
var agent = client
    .AsAIAgent(
        model: model,
        instructions: "...",
        tools: [.. mcpTools.Cast<AITool>()]);
```

When the model decides to call a tool, the framework sends a JSON-RPC request to the MCP server, waits for the result, and injects it back into the conversation - exactly as it does for local function tools. For more on the `AIAgent` and tool integration, see the [Microsoft Agent Framework documentation](https://learn.microsoft.com/en-us/agent-framework/overview/).

### flight-ops MCP server

The `flight-ops` server is a small Python MCP server that exposes two tools:

| Tool | What it returns |
|---|---|
| `get_flight_status` | Current status, gate, and estimated departure for a flight |
| `get_rebooking_options` | Available alternative flights for a disrupted passenger |
| `file_compensation_claim` | Submits a compensation claim and returns a claim ID |

The server is located in `shared/mcp-servers/flight-ops/src/server.py` and listens on `http://localhost:3001/mcp` by default.

## Steps

### Part 1 - Start the MCP server

#### 1. Start the flight-ops server

- [ ] Open a separate terminal and run:

  ```bash
  python shared/mcp-servers/flight-ops/src/server.py
  ```

- [ ] Confirm the server outputs a startup message with no errors.

  > [!NOTE]
  > Keep this terminal open for the rest of the module. If you close it, the agent will fail with a connection error. If `FLIGHT_OPS_MCP_SERVER_URL` is already set in your `.env` to a shared remote server, you can skip this entire Part 1.

### Part 2 - Complete the starter code

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

#### 4. Connect to the MCP server (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
  await using var mcpClient = await McpClient.CreateAsync(
      new HttpClientTransport(new() { Endpoint = new Uri(mcpUrl), Name = "flight-ops" }));
  IList<McpClientTool> mcpTools = await mcpClient.ListToolsAsync();
  ```

#### 5. Create the agent with MCP tools (TODO 3)

- [ ] Locate `// ── TODO 3` and replace the commented-out block with:

  ```csharp
  var credential = new AzureCliCredential();
  var client = new AIProjectClient(new Uri(endpoint), credential);
  var agent = client
      .AsAIAgent(
          model: model,
          instructions:
              "You are the Trip Disruption Concierge. You have access to the " +
              "flight operations system. When passengers ask about flight status " +
              "or rebooking, call the appropriate MCP tool to get live data " +
              "before responding.",
          tools: [.. mcpTools.Cast<AITool>()]);

  var session = await agent.CreateSessionAsync();
  ```

#### 6. Run the first turn - check status and rebooking options (TODO 4)

- [ ] Locate `// ── TODO 4` and replace the commented-out block with:

  ```csharp
  var query =
      "My flight AU123 is disrupted. Can you check the current status and " +
      "find me the best rebooking option? My booking reference is BK98765.";

  Console.ForegroundColor = ConsoleColor.Cyan;
  Console.WriteLine($"[User] {query}");
  Console.ResetColor();
  Console.WriteLine();

  var result = await agent.RunAsync(query, session: session);

  Console.ForegroundColor = ConsoleColor.Green;
  Console.WriteLine($"[Agent] {result.Text}");
  Console.ResetColor();
  Console.WriteLine();
  ```

#### 7. Add a second turn to file a compensation claim (TODO 5)

- [ ] Locate `// ── TODO 5` and replace the commented-out block with:

  ```csharp
  var query2 =
      "Please go ahead and file a compensation claim for the cancellation.";

  Console.ForegroundColor = ConsoleColor.Cyan;
  Console.WriteLine($"[User] {query2}");
  Console.ResetColor();
  Console.WriteLine();

  var result2 = await agent.RunAsync(query2, session: session);

  Console.ForegroundColor = ConsoleColor.Green;
  Console.WriteLine($"[Agent] {result2.Text}");
  Console.ResetColor();
  Console.WriteLine();
  ```

  The session carries context from turn 1 so the agent remembers the flight and booking reference.

### Part 3 - Run and verify

#### 8. Run the starter

- [ ] In a second terminal (keep the MCP server running), run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/05-mcp-tools/src/TripConcierge.McpTools.csproj
  ```

## Validation

- The terminal shows `[Loop] MCP tools discovered: get_flight_status, get_rebooking_options, file_compensation_claim` after connecting to the server.
- The first agent response includes the current status for flight AU123 and a list of rebooking options.
- The second agent response confirms a compensation claim was filed and includes a claim ID (for example `CLM-XXXXXXXX`).

## Congratulations 🎉

You replaced the local function tool with a remote MCP server. The agent discovered the available tools at startup, called them over HTTP when the model needed live data, and used a session to carry context across two turns - all without changing your agent setup code.

> [!TIP]
> **Next up → [Module 06: Knowledge Bases](../06-knowledge-bases/README.md)**
> Ground the agent in a pre-seeded Azure AI Search index using a custom `AIContextProvider` that retrieves relevant policy documents before every model call.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Connection refused` on `localhost:3001` | Start the Python MCP server first (see Step 1) |
| MCP tools not called | Confirm the server started without errors; check its terminal window |
| `NotImplementedException` | A TODO is still incomplete |
| `AuthenticationFailedException` | Run `az login` and confirm you have the Foundry User role on the project |
