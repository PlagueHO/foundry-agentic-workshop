# Introduction to Microsoft Agent Framework (.NET)

This lab covers the full end-to-end journey for building agentic applications in .NET using the Microsoft Agent Framework and Azure AI Foundry.

In this lab, you will learn how to:

1. Set up your environment and verify access to your Foundry project.
1. Create an `AIAgent` backed by Azure AI Foundry with a single line of code.
1. Hold multi-turn conversations using `AgentSession`.
1. Give agents tools - both local C# functions and remote MCP servers.
1. Ground agents in documents with `AIContextProvider` and Azure AI Search.
1. Persist and restore chat history across process restarts.
1. Compose a multi-agent system where a concierge delegates to specialist agents.
1. Deploy, authenticate, and instrument a hosted agent end-to-end.
1. Wrap a chat client in the Agent Harness with `AsHarnessAgent()` to add planning, memory, tools, and loop evaluation in a single call.
1. Evaluate agent quality with local checks and Azure AI Foundry's cloud-based evaluators.
1. Host a specialist agent over the Agent-to-Agent (A2A) protocol and consume it remotely.

The module pages are generated automatically during docs build and preview from source README files in the lab directories under `labs/agent-framework-dotnet`.

## Scenario

Throughout the lab, you will build the **Trip Disruption Concierge** - a multi-agent travel assistant that helps passengers understand their rights and options when flights are cancelled or delayed. **Emma Chen**'s flight AU123 AKL→SYD has been cancelled with only three hours' notice and she contacts the concierge to work through her options. Starting with a single-turn agent in Module 02, the concierge is incrementally enriched across the lab: multi-turn conversation context is maintained with `AgentSession`; flight status and booking tools are wired in as local C# functions; a Python MCP server provides live flight-operations data; a knowledge base grounds the agent in passenger-rights documents via Azure AI Search; a memory provider surfaces Emma's passenger profile automatically in every turn; chat history is serialised and restored across process restarts; specialist sub-agents for rebooking, accommodation, and compensation are composed into a multi-agent orchestration; the concierge is packaged as a containerised hosted agent on Azure Container Apps; identity and authentication are applied end-to-end with `DefaultAzureCredential` and Entra Agent Identity; the entire system is instrumented with OpenTelemetry and traces are visualised in the Aspire Dashboard; the concierge is wrapped in the Agent Harness using `AsHarnessAgent()`, combining `TodoProvider`, `FileMemoryProvider`, `LoopAgent`, and `TodoCompletionLoopEvaluator` into a single batteries-included harness agent; agent quality is measured with local and Azure AI Foundry cloud evaluators; and the Compensation Specialist is moved out of process and reconnected over the Agent-to-Agent (A2A) protocol.

## Modules

| #  | Module | Estimated Time | Required | End State |
|----|--------|----------------|:--------:|-----------|
| 1  | [Environment Setup](./01-setup/README.md) | 15 min | ✅ | .NET SDK, Python, and dotenv configured with verified Foundry access - no agent created yet. |
| 2  | [Your First Agent](./02-first-agent/README.md) | 15 min | ✅ | A single-turn `AIAgent` running against your Foundry project with streaming output. |
| 3  | [Multi-turn & Threads](./03-multi-turn/README.md) | 20 min | ✅ | An `AgentSession` holding conversation state across multiple turns. |
| 4  | [Function Tools](./04-function-tools/README.md) | 20 min | ✅ | The agent extended with flight-lookup and booking C# function tools. |
| 5  | [MCP Tools](./05-mcp-tools/README.md) | 25 min | ✅ | A local Python MCP server wired into the agent via `McpServer`. |
| 6  | [Knowledge Bases](./06-knowledge-bases/README.md) | 25 min | ✅ | An `AIContextProvider` grounding the agent in passenger-rights documents via Azure AI Search. |
| 7  | [Memory & Context](./07-memory/README.md) | 20 min | ✅ | A `PassengerProfileMemory` provider surfacing passenger context automatically in every turn. |
| 8  | [Chat History](./08-chat-history/README.md) | 20 min | ✅ | Session state serialised to disk and restored correctly across process restarts. |
| 9  | [Multi-agent Orchestration](./09-multi-agent/README.md) | 25 min | ✅ | A concierge agent orchestrating specialist sub-agents for rebooking, accommodation, and compensation. |
| 10 | [Hosted Agents](./10-hosted-agents/README.md) | 30 min | ✅ | The concierge deployed as a hosted agent on Azure Container Apps. |
| 11 | [Agent Identity & Auth](./11-agent-auth/README.md) | 20 min | ✅ | `DefaultAzureCredential` and Entra Agent Identity applied end-to-end. |
| 12 | [Observability & Tracing](./12-observability/README.md) | 25 min | ✅ | OpenTelemetry traces visualised in the Aspire Dashboard. |
| 13 | [ConciergeClaw - Agent Harness](./13-concierge-claw/README.md) | 35 min | ✅ | The concierge wrapped with `AsHarnessAgent()`, adding planning, file memory, loop evaluation, and session serialisation in one call. |
| 14 | [Evaluation & Quality](./14-evaluation/README.md) | 25 min | ✅ | Agent responses scored with both a `LocalEvaluator` and Azure AI Foundry's cloud-based `FoundryEvals`. |
| 15 | [Agent-to-Agent (A2A)](./15-agent-to-agent/README.md) | 30 min | ✅ | The Compensation Specialist hosted as an A2A server and consumed remotely by the concierge. |

Total time: approximately 5–6 hours, depending on your .NET familiarity and how many modules you complete. Each module builds on the previous ones, so we recommend following them in order. If you are short on time, each module's `solution` folder contains a working reference implementation you can run directly.

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

The starter file contains numbered TODO comments with the code you need to add, commented out directly below each one. The solution folder contains the complete working implementation. To run any solution directly:

```bash
dotnet run --project labs/agent-framework-dotnet/02-first-agent/solution/TripConcierge.FirstAgent.csproj
```

Replace `02-first-agent` and `TripConcierge.FirstAgent` with the module you want.

For the Agent Framework documentation, see [Microsoft Agent Framework on Microsoft Learn](https://learn.microsoft.com/en-us/agent-framework/).
