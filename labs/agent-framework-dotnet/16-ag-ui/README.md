# 16. AG-UI: Browser Chat with CopilotKit

**Estimated time:** 35 minutes

![Microsoft Agent Framework overview: an open-source engine for building and orchestrating AI agents, summarised in five pillars - Unified SDK (AIAgent, AgentThread, and AgentTool primitives built on Microsoft.Extensions.AI), Local-first and cloud-agnostic (run agents locally then move the same code to Foundry Agent Service or any cloud containers), Multi-agent orchestration (sequential, concurrent, handoff, group chat, magentic, and workflow patterns), Tools and extensibility (out-of-the-box integrations plus functions, APIs, and MCP servers as tools), and Enterprise-grade foundations (approval flows, content-policy hooks, OpenTelemetry observability, and long-running execution).](../../../docs/assets/diagrams/agent-framework-introduction.png)

> [!IMPORTANT]
> This module builds on [Module 04](../04-function-tools/README.md) and [Module 15](../15-agent-to-agent/README.md). You will expose your Trip Disruption Concierge as an AG-UI server and connect it to a React/CopilotKit frontend. Node.js 20 or later is required for the UI.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Expose an `AIAgent` as a streaming AG-UI server endpoint with `AddAGUI()` and `MapAGUI()`.
- Register a `GetFlightStatus` backend tool that executes server-side and streams its result to the browser.
- Configure a Next.js CopilotKit runtime proxy using `CopilotRuntime` and `HttpAgent`.
- Wrap the React application with the `<CopilotKit>` provider to enable agent connectivity.
- Display the concierge in a browser using the prebuilt `<CopilotSidebar>` component.

## Concepts

### What is AG-UI?

AG-UI (Agent User Interface protocol) is an open, event-based standard for streaming AI agent
responses to browser clients. It works over HTTP: the client sends a POST request with a list of
messages and the server replies with a stream of Server-Sent Events (SSE). Each event carries
typed data. Key event types include:

| Event type | When it fires |
|---|---|
| `RUN_STARTED` | Agent begins processing the request |
| `TEXT_MESSAGE_CONTENT` | Incremental text chunk from the model |
| `TOOL_CALL_START` | Agent is about to call a tool |
| `TOOL_CALL_RESULT` | Tool returned a result |
| `RUN_FINISHED` | Agent completed the run |

`MapAGUI` (from `Microsoft.Agents.AI.Hosting.AGUI.AspNetCore`) handles all of this for you —
you supply the agent, it handles the SSE protocol.

### Three-layer architecture

```text
Browser (React :3000)
  └─► POST /api/copilotkit  [CopilotKit runtime — Next.js API route]
                └─► POST http://localhost:8888  [your .NET MapAGUI endpoint]
                                └─► AIAgent → tools → streams SSE events
```

There are three layers, each with a single responsibility:

1. **React UI** — renders the chat using `<CopilotSidebar>`. No knowledge of AG-UI.
1. **CopilotKit runtime** (Next.js API route) — proxies requests from the browser to any
   AG-UI-compatible agent. `HttpAgent` points at your .NET server.
1. **.NET AG-UI server** — runs the agent, calls tools, streams events.

This separation means you can point the same UI at any AG-UI server without changing the React code.

### Backend tool rendering

When the model calls `get_flight_status`, the .NET server:

1. Executes your C# `GetFlightStatus` function.
1. Streams a `TOOL_CALL_RESULT` event with the result.
1. Continues generating the next text chunk.

The sidebar receives the tool result event and renders it inline, without you writing any client-side
tool-handling code. This is called _backend tool rendering_.

### AddAGUI vs other hosting patterns

| Pattern | Package | Where the loop runs |
|---|---|---|
| `MapAGUI` (this module) | `AGUI.AspNetCore` | .NET server; browser connects over SSE |
| `MapA2AHttpJson` (Module 15) | `A2A.AspNetCore` | .NET server; another agent connects |
| Foundry Hosted Agent (Module 10) | N/A | Foundry Agent Service; you call via REST |

## Steps

### Part 1 - Wire the AG-UI server

#### 1. Open the server starter file

- [ ] Open `server-src/Program.cs` in the editor.

#### 2. Register AG-UI services (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  builder.Services.AddHttpClient().AddLogging();
  builder.Services.AddAGUI();
  ```

  `AddAGUI()` registers the SSE streaming middleware that `MapAGUI` needs.

#### 3. Create the concierge agent (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
  AIAgent agent = new AIProjectClient(new Uri(endpoint), new DefaultAzureCredential())
      .AsAIAgent(
          model: model,
          name: "trip-disruption-concierge",
          instructions:
              """
              You are the Trip Disruption Concierge for Air New Zealand.
              When a passenger reports a disrupted flight:
              1. Call get_flight_status to confirm the current status of their flight.
              2. Acknowledge the disruption with empathy.
              3. Explain their options: rebooking, accommodation, compensation.
              Keep responses concise and supportive.
              """,
          tools: [AIFunctionFactory.Create(GetFlightStatus)]);
  ```

  > [!NOTE]
  > `AIFunctionFactory.Create(GetFlightStatus)` registers the local static function as a backend
  > tool. The model invokes it by name; the result streams to the browser automatically.

#### 4. Map the AG-UI endpoint (TODO 3)

- [ ] Locate `// ── TODO 3` and replace the commented-out block with:

  ```csharp
  app.MapAGUI("/", agent);

  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Server] AG-UI endpoint mapped at /");
  Console.WriteLine("[Server] Waiting for CopilotKit connections (port 8888)...");
  Console.ResetColor();
  Console.WriteLine();

  await app.RunAsync();
  ```

- [ ] Remove the `throw new NotImplementedException(...)` line.

#### 5. Start the AG-UI server

- [ ] In a terminal, run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/16-ag-ui/server-src \
    --urls http://localhost:8888
  ```

- [ ] Confirm the console prints `[Server] Waiting for CopilotKit connections (port 8888)...`.

  > [!NOTE]
  > Keep this terminal open. The React UI connects to this running server.

### Part 2 - Connect the CopilotKit React UI

#### 6. Install UI dependencies

- [ ] Open a second terminal and install the Node packages:

  ```bash
  cd labs/agent-framework-dotnet/16-ag-ui/ui
  npm install
  ```

#### 7. Configure the server URL

- [ ] Copy `.env.local.example` to `.env.local`:

  ```bash
  cp .env.local.example .env.local
  ```

- [ ] Confirm `.env.local` contains:

  ```text
  AGUI_SERVER_URL=http://localhost:8888
  ```

#### 8. Examine the CopilotKit runtime proxy

- [ ] Open `app/api/copilotkit/route.ts` and read the comments.

  This file is the **server-side** Next.js API route. The key lines are:

  ```typescript
  const runtime = new CopilotRuntime({
    agents: {
      default: new HttpAgent({ url: serverUrl }),
    },
  })
  ```

  `HttpAgent` wraps any AG-UI endpoint as a CopilotKit-compatible agent. `CopilotRuntime`
  handles discovery, session routing, and future features like threads.

#### 9. Examine the React provider

- [ ] Open `app/layout.tsx` and read the comments.

  `<CopilotKit runtimeUrl="/api/copilotkit">` connects every component in the tree to your
  runtime proxy. It is the only CopilotKit import the root layout needs.

#### 10. Examine the chat sidebar

- [ ] Open `app/page.tsx` and read the comments.

  `<CopilotSidebar>` is a prebuilt, accessible chat UI component. `defaultOpen` shows it
  immediately. The `labels` prop customises the title and welcome message.

### Part 3 - Run and chat

#### 11. Start the React development server

- [ ] In the second terminal (inside `ui/`), run:

  ```bash
  npm run dev
  ```

- [ ] Open [http://localhost:3000](http://localhost:3000) in your browser.

#### 12. Chat with the concierge

- [ ] Type the following into the sidebar and send it:

  ```text
  My flight AU123 has been cancelled. What are my options?
  ```

- [ ] Watch for:
  - A `[Tool] → get_flight_status(AU123)` line in the .NET terminal — the tool ran server-side.
  - The result and the agent's response appearing in the browser.

- [ ] Try a follow-up:

  ```text
  What compensation am I entitled to for a cancellation with less than 3 hours' notice?
  ```

## Validation

- The .NET server console prints `[Server] Waiting for CopilotKit connections (port 8888)...`.
- Navigating to `http://localhost:3000` shows the chat sidebar, open by default.
- Asking about flight `AU123` triggers the `get_flight_status` tool — visible in the .NET terminal.
- The browser sidebar shows the tool result and the agent's response in real time.
- Asking a follow-up question works — the agent maintains conversation context.

## Congratulations 🎉

You have connected your .NET Agent Framework agent to a React browser UI using the AG-UI
protocol and CopilotKit. The agent runs entirely on the .NET server; the React app is a
thin streaming client that required zero agent-specific code — just a provider, a proxy, and
a sidebar component.

> [!TIP]
> **You have completed the Agent Framework .NET lab series!**
> Module 17 (Capstone) is coming soon — wire the full multi-agent concierge into a single AG-UI endpoint.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `NotImplementedException` on server start | A TODO is still incomplete — check `server-src/Program.cs` |
| Browser shows `Failed to fetch` on send | The .NET server is not running. Start it with `dotnet run --urls http://localhost:8888` |
| Sidebar appears but responses never arrive | Check `.env.local` — `AGUI_SERVER_URL` must be `http://localhost:8888` |
| `FOUNDRY_PROJECT_ENDPOINT is not set` | Copy `shared/.env.example` to `.env` at the repository root and fill in your values |
| `AuthenticationFailedException` | Run `az login` and confirm the account matches your Foundry project assignment |
| npm install errors | Confirm Node.js 20+ is installed: `node --version` |
| Port 8888 already in use | Change the `--urls` flag on the .NET server and update `AGUI_SERVER_URL` in `.env.local` to match |
