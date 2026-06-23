# Introduction to Microsoft Agent Framework (.NET)

Build AI agents in .NET using the Microsoft Agent Framework and Azure AI Foundry.
Across these modules you will construct the **Trip Disruption Concierge** — a
multi-agent travel assistant that helps passengers understand their rights and
options when flights are cancelled or delayed.

## Learning objectives

By the end of this lab you will be able to:

- Create an `AIAgent` backed by Azure AI Foundry with a single line of code.
- Hold multi-turn conversations using `AgentSession`.
- Give agents tools — both local C# functions and remote MCP servers.
- Compose a multi-agent system where a concierge delegates to specialist agents.
- Instrument an agent with OpenTelemetry and visualise traces in the Aspire Dashboard.

## Prerequisites

- .NET 10 SDK (`dotnet --version` → `10.0.x`)
- Python 3.11+ (for the local MCP server in Module 05)
- Access to an Azure AI Foundry project — see `shared/.env.example` for required variables
- Docker Desktop (for the Aspire Dashboard in Module 12)

## Scenario

**Emma Chen** is a passenger whose flight **AU123 AKL→SYD** was cancelled with only
3 hours' notice. She contacts the Trip Disruption Concierge and works through her
options — rebooking, hotel accommodation, and compensation — across a connected
conversation.

You build this concierge progressively, adding capabilities module by module.

## Teaching theme

> **Where does the agent loop run?**

| Mode | Loop location | How to recognise |
|---|---|---|
| `ChatClientAgent` | **Local** — your process | You control the turn cycle; tools run in-process |
| Foundry Hosted Agent | **Remote** — Agent Service | The service manages the loop; you send and await |

Phase 0 focuses entirely on the local loop so you can see every iteration in your
terminal output.

## Modules

| Module | Title | Highlights |
|---|---|---|
| [01 — Environment Setup](./01-setup/README.md) | Environment Setup | Prerequisites, `.env`, health-check |
| [02 — Your First Agent](./02-first-agent/README.md) | Your First Agent | `AIProjectClient`, `RunAsync`, streaming |
| [03 — Multi-turn & Threads](./03-multi-turn/README.md) | Multi-turn & Threads | `AgentSession`, persistent context |
| [04 — Function Tools](./04-function-tools/README.md) | Function Tools | `AIFunctionFactory`, tool-call logging |
| [05 — MCP Tools](./05-mcp-tools/README.md) | MCP Tools | `McpServer`, local Python MCP server |
| [06 — Knowledge Bases](./06-knowledge-bases/README.md) | Knowledge Bases | `AIContextProvider`, Azure AI Search RAG |
| [07 — Memory & Context](./07-memory/README.md) | Memory & Context Providers | `PassengerProfileMemory`, `IChatClient` wrapping |
| [08 — Chat History](./08-chat-history/README.md) | Session Persistence | `SerializeSessionAsync`, restore across processes |
| [09 — Multi-agent Orchestration](./09-multi-agent/README.md) | Multi-agent Orchestration | Specialist agents as skills |
| [10 — Hosted Agents](./10-hosted-agents/README.md) | Hosted Agents | `AddFoundryResponses`, `MapFoundryResponses`, Container Apps |
| [11 — Agent Identity & Auth](./11-agent-auth/README.md) | Agent Identity & Auth | `DefaultAzureCredential`, `ChainedTokenCredential`, Entra Agent Identity |
| [12 — Observability & Tracing](./12-observability/README.md) | Observability & Tracing | OpenTelemetry, Aspire Dashboard |

## Project structure

Each module contains:

```text
NN-module-name/
├── README.md         ← objectives, steps, validation, troubleshooting
├── src/
│   ├── *.csproj      ← starter project (TODOs to complete)
│   └── Program.cs
└── solution/
    ├── *.csproj      ← reference implementation
    └── Program.cs
```

The starter file contains numbered TODO comments with the code you need to add
commented out directly below each one. The solution folder contains the complete
working implementation.

## Running a solution

```bash
dotnet run --project labs/agent-framework-dotnet/02-first-agent/solution/TripConcierge.FirstAgent.csproj
```

Replace `02-first-agent` and `TripConcierge.FirstAgent` with the module you want.

## Environment setup

Copy `shared/.env.example` to `.env` in the repository root and fill in your Foundry project
details. Each module loads the file automatically via `dotenv.net`.

For the Agent Framework documentation, see the [Microsoft Agent Framework documentation](https://learn.microsoft.com/en-us/agent-framework/).
