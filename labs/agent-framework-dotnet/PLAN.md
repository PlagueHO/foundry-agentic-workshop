# Agent Framework (.NET) Lab - Evolving Plan

This file tracks the design, decisions, build status, and open items for the
`agent-framework-dotnet` lab. Update it after every implementation session.

---

## Scenario: Trip Disruption Concierge

A travel-focused AI assistant that helps airline passengers understand their rights
and options when flights are cancelled or delayed. The scenario is used consistently
across all modules so attendees build a single coherent system.

**Persona**: Emma Chen. Flight AU123 AKL→SYD cancelled with 3 hours notice.

### Agents

| Agent | Role |
|---|---|
| `trip-disruption-concierge` | Orchestrating concierge - routes to specialists |
| `rebooking-specialist` | Finds alternative flight options |
| `accommodation-specialist` | Sources hotel accommodation for stranded passengers |
| `compensation-specialist` | Calculates and files compensation entitlements |

---

## Module Plan (17 modules total)

### Phase 0 - Demo (completed)

| # | Slug | Title | Status |
|---|---|---|---|
| M2 | `02-first-agent` | Your First Agent | ✅ Done |
| M3 | `03-multi-turn` | Multi-turn & Threads | ✅ Done |
| M4 | `04-function-tools` | Function Tools | ✅ Done |
| M5 | `05-mcp-tools` | MCP Tools | ✅ Done |
| M9 | `09-multi-agent` | Multi-agent Orchestration | ✅ Done |
| M12 | `12-observability` | Observability & Tracing | ✅ Done |

### Phase 1 - Core (completed)

| # | Slug | Title | Status |
|---|---|---|---|
| M1 | `01-setup` | Environment Setup | ✅ Done |
| M6 | `06-knowledge-bases` | Knowledge Bases (AI Search) | ✅ Done |
| M7 | `07-memory` | Memory & Context Providers | ✅ Done |
| M8 | `08-chat-history` | Chat History Provider | ✅ Done |
| M10 | `10-hosted-agents` | Hosted Agents (Foundry) | ✅ Done |
| M11 | `11-agent-auth` | Agent Identity & Auth | ✅ Done |

### Phase 2 - Harness (completed)

| # | Slug | Title | Status |
|---|---|---|---|
| M13 | `13-concierge-claw` | ConciergeClaw - Agent Harness | ✅ Done |

### Phase 3 - Extension (in progress)

| # | Slug | Title | Status |
|---|---|---|---|
| M14 | `14-evaluation` | Evaluation & Quality | ✅ Done |
| M15 | `15-agent-to-agent` | Agent-to-Agent (A2A) | ✅ Done |
| M16 | `16-ag-ui` | Making your agent interactive through AG-UI | ❌ Todo |
| M17 | `17-capstone` | Capstone - Full System | ❌ Todo |

---

## Demo Path (Phase 0 - 30 min)

Recommended delivery order for a live 30-minute demo:

1. **M2** (~6 min) - Create the simplest possible AI agent. Show RunAsync + streaming.
1. **M3** (~5 min) - Add a session. Show how context is preserved across turns.
1. **M4** (~6 min) - Add a function tool. Show the agent calling local C# code.
1. **M5** (~5 min) - Replace the function tool with an MCP server. Show the protocol layer.
1. **M9** (~5 min) - Add specialist sub-agents. Show the orchestration loop.
1. **M12** (~3 min) - Add OTel. Open Aspire Dashboard. Show traces.

---

## Technical Stack

### Key Packages

| Package | Purpose |
|---|---|
| `Microsoft.Agents.AI.Foundry` | Foundry provider - `AIProjectClient.AsAIAgent()` |
| `Microsoft.Agents.AI` | Core abstractions - `AIAgent`, `AgentSession` |
| `Microsoft.Agents.AI.Mcp` | MCP tool client - `McpServer`, `.WithMcpTools()` |
| `Microsoft.Agents.AI.Harness` | Hosting harness (Phase 1+) |
| `Azure.Identity` | `DefaultAzureCredential` |
| `dotenv.net` | `.env` file loading - `Env.TraversalSearch()` |
| `OpenTelemetry.Exporter.OpenTelemetryProtocol` | OTLP exporter (Aspire Dashboard) |
| `Azure.Monitor.OpenTelemetry.Exporter` | App Insights exporter (M12) |

All versions managed centrally in `Directory.Packages.props`.

### Core API Pattern

```csharp
// 1. Create client
var client = new AIProjectClient(new Uri(endpoint), new DefaultAzureCredential());

// 2. Create agent
var agent = client.AsAIAgent(model: model, instructions: "...");

// 3a. Single turn
var result = await agent.RunAsync(query);

// 3b. Streaming
await foreach (var chunk in agent.RunStreamingAsync(query))
    if (chunk.Text is not null) Console.Write(chunk.Text);

// 4. Multi-turn with session
var session = await agent.CreateSessionAsync();
var result = await agent.RunAsync(query, session: session);
```

### Teaching Theme: "Where does the agent loop run?"

| Mode | Loop Location | How to recognise |
|---|---|---|
| `ChatClientAgent` | **Local** - your code | Your code controls the turn cycle, tools execute in-process |
| `HarnessAgent` | **Local** - harness loop | Framework manages tool calling, planning, memory, approvals; you supply instructions + tools |
| `Foundry Hosted Agent` | **Remote** - Agent Service | Service manages the loop; you just call and await |

---

## Module Design Details

### M13 - ConciergeClaw: Agent Harness

The `ConciergeClaw` wraps a `ChatClientAgent` in the AF Harness to produce a
batteries-included Trip Disruption Concierge. Attendees replace the bare agent
from earlier modules with one that has planning, memory, file access, and
concurrent sub-agent delegation - all by calling `AsHarnessAgent()`.

#### Learning objectives

- Understand the difference between a bare `ChatClientAgent` and a `HarnessAgent`
- Use `AsHarnessAgent()` with `HarnessAgentOptions` to compose harness features
- Navigate plan/execute modes with `TodoProvider` and `AgentModeProvider`
- Persist a passenger profile across sessions with `FileMemoryProvider`
- Access passenger-rights policy files with `FileAccessProvider`
- Delegate to specialist sub-agents concurrently via `BackgroundAgentsProvider`
- Wrap the harness with `LoopAgent` to drive resolution until all todos are cleared
- Use `HarnessConsole` as an interactive TUI and understand it as a customisable starting point
- Export and resume a disruption case with `SerializeSessionAsync` / `DeserializeSessionAsync`

#### Harness features used

| Feature | Provider / API | Role in the scenario |
|---|---|---|
| Planning | `TodoProvider` + `AgentModeProvider` | Structure multi-step resolution: rebook → accommodate → compensate |
| File memory | `FileMemoryProvider` | Persist passenger profile and disruption state across sessions |
| File access | `FileAccessProvider` | Read passenger-rights policy CSV from `shared/data/` |
| Background agents | `BackgroundAgentsProvider` | Delegate to rebooking/accommodation/compensation specialists concurrently |
| Web search | Built-in hosted tool | Look up live airline news and policy announcements |
| Loop | `LoopAgent` decorator | Re-invoke the harness until all todos are cleared |
| Session I/O | `SerializeSessionAsync` / `DeserializeSessionAsync` | Export and resume a disruption case |

#### Harness API pattern

```csharp
IChatClient chatClient =
    new AIProjectClient(new Uri(endpoint), new DefaultAzureCredential())
        .GetProjectOpenAIClient()
        .GetResponsesClient()
        .AsIChatClient(deploymentName);

AIAgent agent = chatClient.AsHarnessAgent(new HarnessAgentOptions
{
    ChatOptions = new ChatOptions
    {
        Instructions = ConciergeClaw.Instructions,
        Tools = [FlightTools.CreateGetFlightStatusTool()],
    },
});

await HarnessConsole.RunAgentAsync(
    agent,
    userPrompt: "Flight AU123 AKL\u2192SYD has been cancelled. How can I help you?");
```

#### Project slug

`TripConcierge.ConciergeClaw` in `13-concierge-claw/`

---

### M14 - Evaluation & Quality

The concierge from Module 04 (compensation tool attached) is scored with both an
offline `LocalEvaluator` and a cloud-based `FoundryEvals` pipeline, teaching the
built-in evaluation framework on top of `Microsoft.Extensions.AI.Evaluation`.

#### Learning objectives

- Build a `LocalEvaluator` from `EvalChecks.KeywordCheck`, `EvalChecks.ToolCalledCheck`, and `FunctionEvaluator.Create`
- Run `agent.EvaluateAsync(queries, evaluator)` and read `AgentEvaluationResults`
- Build a `FoundryEvals` instance for cloud LLM-as-judge scoring (relevance, coherence, task adherence)
- Read pass/fail summaries, per-item metrics, and the Foundry portal report link

#### Project slug

`TripConcierge.Evaluation` in `14-evaluation/`

---

### M15 - Agent-to-Agent (A2A)

The Compensation Specialist from Module 09 is moved out of process into its own
ASP.NET Core host, exposed over the Agent-to-Agent (A2A) protocol, and consumed
remotely by the concierge - the same `WithAgentSkill` composition, now spanning
a network boundary.

#### Learning objectives

- Host an `AIAgent` as an A2A server with `AddA2AServer` + `MapA2AHttpJson`
- Publish an agent card with `MapWellKnownAgentCard`
- Discover a remote A2A agent from a client with `A2ACardResolver.GetAIAgentAsync()`
- Expose a remote `AIAgent` as a callable tool on the concierge with `AsAIFunction()`

#### Project layout

Unlike the single `src`/`solution` pair used elsewhere, M15 has four projects -
mirroring Module 10's `deploy-src`/`deploy-solution` split:

| Folder | Project | Role |
|---|---|---|
| `server-src/` / `server-solution/` | `TripConcierge.CompensationService` | ASP.NET Core A2A host for the Compensation Specialist |
| `src/` / `solution/` | `TripConcierge.AgentToAgent` | Console concierge client consuming the remote specialist |

---

## Infrastructure Decisions

- **Target framework**: `net10.0`
- **Language version**: `preview` (C# 14 features available)
- **Nullable**: enabled
- **Implicit usings**: enabled
- **SDK pin**: `global.json` with `rollForward: latestMinor`
- **Package management**: Central Package Management via `Directory.Packages.props`
- **Project naming**: `TripConcierge.<ModuleName>` (e.g., `TripConcierge.FirstAgent`)

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | Azure AI Foundry project endpoint | `https://...` |
| `AGENT_MODEL` | Model deployment name | `chat` |
| `FLIGHT_OPS_MCP_SERVER_URL` | URL for flight-ops MCP server | `http://localhost:3001/mcp` |
| `FLIGHT_OPS_MCP_SERVER_LABEL` | Label for flight-ops MCP server | `flight_ops` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP endpoint for Aspire Dashboard | `http://localhost:4317` |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | App Insights (optional in M12) | `InstrumentationKey=...` |
| `A2A_SERVER_URL` | Compensation Specialist A2A server endpoint (M15) | `http://localhost:5000` |

## MCP Servers

| Server | Location | Transport | Phase |
|---|---|---|---|
| `retail-remedy-ops` | `shared/mcp-servers/retail-remedy-ops/` | HTTP | Existing |
| `flight-ops` | `shared/mcp-servers/flight-ops/` | HTTP | Phase 0 ✅ |

---

## Open Items

- [x] Phase 1: Add `01-setup` README with pre-requisite checklist
- [x] Phase 1: Add `06-knowledge-bases` connecting to `passenger-rights` Azure AI Search index
- [x] Phase 1: Create `scripts/seed-passenger-rights-index.py`
- [x] Phase 1: Create `scripts/deploy-flight-ops-mcp-server.py`
- [x] Phase 1: Update `shared/.env.example` with all Phase 1 env vars
- [x] Phase 1: Add `azure.yaml` postprovision hooks for new scripts
- [x] Phase 2 (M13): Scaffold `13-concierge-claw/` project - starter + solution
- [x] Phase 2 (M13): Write README with `ConciergeClaw` steps (plan → execute → loop)
- [x] Phase 2 (M13): Add `HarnessConsole` shared console reference project to `shared/` (deferred - console TUI is sample-only; no NuGet package available)
- [x] Phase 2 (M13): Verify `AsHarnessAgent` / `HarnessAgentOptions` API signatures against published release
- [x] Phase 3 (M14): Scaffold `14-evaluation/` project - starter + solution, `LocalEvaluator` + `FoundryEvals`
- [x] Phase 3 (M15): Scaffold `15-agent-to-agent/` - client (`src`/`solution`) + A2A server (`server-src`/`server-solution`) for the Compensation Specialist
- [ ] Phase 3 (M16): Scaffold `16-ag-ui/` - console AG-UI client + `MapAGUI` server
- [ ] Phase 3 (M17): Add capstone lab wiring all modules together (guided integration)
- [ ] Phase 2: Evaluate A2A protocol support in AF .NET (superseded - implemented in M15)
- [ ] All: Verify exact AF API method signatures against published release (APIs are prerelease)

---

## Official References

- Overview: <https://learn.microsoft.com/en-us/agent-framework/overview/>
- Get started: <https://learn.microsoft.com/en-us/agent-framework/get-started/>
- Your first agent: <https://learn.microsoft.com/en-us/agent-framework/get-started/your-first-agent>
- Add tools: <https://learn.microsoft.com/en-us/agent-framework/get-started/add-tools>
- Multi-turn: <https://learn.microsoft.com/en-us/agent-framework/get-started/multi-turn>
- Memory: <https://learn.microsoft.com/en-us/agent-framework/get-started/memory>
- Hosting: <https://learn.microsoft.com/en-us/agent-framework/get-started/hosting>
- MCP tools: <https://learn.microsoft.com/en-us/agent-framework/agents/tools/local-mcp-tools>
- Foundry provider: <https://learn.microsoft.com/en-us/agent-framework/agents/providers/microsoft-foundry>
- Aspire Dashboard standalone: <https://learn.microsoft.com/dotnet/aspire/fundamentals/dashboard/standalone>
- Harness overview (blog): <https://devblogs.microsoft.com/agent-framework/build-your-own-claw-and-agent-harness-with-microsoft-agent-framework/>
- Harness Part 1 - Meet your claw (blog): <https://devblogs.microsoft.com/agent-framework/meet-your-agent-harness-and-claw/>
- Harness samples: <https://github.com/microsoft/agent-framework/tree/main/dotnet/samples/02-agents/Harness>
- AF GitHub repo: <https://github.com/microsoft/agent-framework>
- .NET samples: <https://github.com/microsoft/agent-framework/tree/main/dotnet/samples>
- Getting started samples: <https://github.com/microsoft/agent-framework/tree/main/dotnet/samples/01-get-started>
- MCP samples: <https://github.com/microsoft/agent-framework/tree/main/dotnet/samples/02-agents/ModelContextProtocol>
- OTel samples: <https://github.com/microsoft/agent-framework/tree/main/dotnet/samples/02-agents/AgentOpenTelemetry>
- Hosting samples: <https://github.com/microsoft/agent-framework/tree/main/dotnet/samples/04-hosting>
