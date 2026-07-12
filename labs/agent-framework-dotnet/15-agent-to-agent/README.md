---
title: '15. Agent-to-Agent (A2A)'
description: 'Complete this lab to agent-to-agent (a2a).'
lastUpdated: '2026-07-13'
track: 'agent-framework-dotnet'
module: 15
slug: '15-agent-to-agent'
estimatedTimeMinutes: 30
difficulty: 'advanced'
prerequisites: ['Module 14']
audience:
  - 'attendee'
technologies:
  - 'Microsoft Agent Framework'
  - 'Microsoft Foundry'
tags:
  - 'agent-framework'
  - 'agent'
  - 'a2a'
status: 'active'
contentType: 'lab'
---
# 15. Agent-to-Agent (A2A)

**Estimated time:** 30 minutes

![Microsoft Agent Framework overview: an open-source engine for building and orchestrating AI agents, summarised in five pillars - Unified SDK (AIAgent, AgentThread, and AgentTool primitives built on Microsoft.Extensions.AI), Local-first and cloud-agnostic (run agents locally then move the same code to Foundry Agent Service or any cloud containers), Multi-agent orchestration (sequential, concurrent, handoff, group chat, magentic, and workflow patterns), Tools and extensibility (out-of-the-box integrations plus functions, APIs, and MCP servers as tools), and Enterprise-grade foundations (approval flows, content-policy hooks, OpenTelemetry observability, and long-running execution).](../../../docs/assets/diagrams/agent-framework-introduction.png)

> [!IMPORTANT]
> This module builds on [Module 09](../09-multi-agent/README.md). The Compensation Specialist you orchestrated in-process there now runs as its own web service, and the concierge reaches it over the network using the Agent-to-Agent (A2A) protocol.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Host an `AIAgent` as an A2A server with `AddA2AServer` and `MapA2AHttpJson`.
- Publish an agent card at the A2A well-known discovery path.
- Discover a remote A2A agent from a client with `A2ACardResolver`.
- Expose a remote `AIAgent` as a callable `AIFunction` with `AsAIFunction()`, so an orchestrating concierge can invoke it like any other tool.
- Run a query and confirm the concierge delegates it across a process boundary.

## Concepts

### Why cross a process boundary?

In [Module 09](../09-multi-agent/README.md), the concierge and its specialists all ran in the same process. That works well when every agent shares a runtime, a team, and a deployment. Real systems often need more:

- **Service boundaries.** The Compensation Specialist might be owned by a different team, written in a different language, or deployed independently.
- **Organisational boundaries.** A partner airline or regulator might expose a compliance agent you can call but never see the code for.

**Agent-to-Agent (A2A)** is an open protocol for exactly this: it lets agents discover each other, exchange messages, and coordinate on tasks over HTTP - regardless of framework or language.

### Hosting an agent over A2A

The `Microsoft.Agents.AI.Hosting.A2A.AspNetCore` package bridges an `AIAgent` to the A2A protocol in an ASP.NET Core application:

```csharp
builder.Services.AddKeyedSingleton<AIAgent>("compensation-specialist", (_, _) =>
    projectClient.AsAIAgent(model: model, instructions: "..."));

builder.AddA2AServer("compensation-specialist");

var app = builder.Build();
app.MapA2AHttpJson("compensation-specialist", "/a2a/compensation-specialist");
app.MapWellKnownAgentCard(new AgentCard { Name = "CompensationSpecialist", ... });
```

`AddA2AServer` resolves the keyed `AIAgent` from the DI container and wires up request handling and session storage. `MapA2AHttpJson` exposes the HTTP+JSON protocol binding at the path you choose. `MapWellKnownAgentCard` publishes an [agent card](https://a2a-protocol.org/latest/specification/#5-agent-discovery-the-agent-card) - metadata describing the agent's name, description, and supported interfaces - so remote clients can discover it before sending requests.

> [!NOTE]
> The in-memory session and task stores used here are for development only. State is lost on restart and is not shared across instances - production deployments register durable implementations.

### Consuming a remote agent

The `Microsoft.Agents.AI.A2A` package provides `A2ACardResolver`, which fetches a remote agent's card and wraps it as a standard `AIAgent` in one call:

```csharp
var resolver = new A2ACardResolver(new Uri("http://localhost:5000"));
AIAgent compensationSpecialist = await resolver.GetAIAgentAsync();
```

From here, `compensationSpecialist` behaves exactly like any other `AIAgent` - `RunAsync` and `RunStreamingAsync` work unchanged. To let the concierge delegate to it, expose it as a callable tool with `AsAIFunction()`:

```csharp
var concierge = client.AsAIAgent(
    model: model,
    instructions: "...",
    tools: [compensationSpecialist.AsAIFunction()]);
```

`AsAIFunction()` wraps any `AIAgent` - local or remote - as a standard `AIFunction`. The concierge calls it exactly like the local C# function tools from [Module 04](../04-function-tools/README.md); it does not need to know or care that this particular tool call travels over HTTP to a different process.

## Steps

### Part 1 - Run the Compensation Specialist as an A2A server

#### 1. Open the server starter file

- [ ] Open `server-src/Program.cs` in the editor.

#### 2. Register the specialist agent (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  builder.Services.AddKeyedSingleton<AIAgent>(AgentName, (_, _) =>
  {
      var credential = new DefaultAzureCredential();
      return new AIProjectClient(new Uri(endpoint), credential)
          .AsAIAgent(
              model: model,
              name: AgentName,
              instructions:
                  "You are the Compensation Specialist. Your sole focus is " +
                  "explaining and calculating passenger compensation " +
                  "entitlements under airline disruption policies. Provide " +
                  "clear figures and actionable next steps. Do not discuss " +
                  "rebooking or hotels.",
              description:
                  "Explains and calculates the passenger's compensation entitlement.");
  });
  ```

#### 3. Register the A2A server (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
  builder.AddA2AServer(AgentName);
  ```

#### 4. Map the endpoint and agent card (TODO 3)

- [ ] Locate `// ── TODO 3` and replace the commented-out block with:

  ```csharp
  app.MapA2AHttpJson(AgentName, "/a2a/compensation-specialist");

  app.MapWellKnownAgentCard(new AgentCard
  {
      Name = "CompensationSpecialist",
      Description =
          "Explains and calculates passenger compensation entitlements " +
          "under airline disruption policies.",
      Version = "1.0",
      DefaultInputModes = ["text"],
      DefaultOutputModes = ["text"],
      SupportedInterfaces =
      [
          new AgentInterface
          {
              Url = "http://localhost:5000/a2a/compensation-specialist",
              ProtocolBinding = ProtocolBindingNames.HttpJson,
              ProtocolVersion = "1.0",
          }
      ]
  });

  app.Run();
  ```

#### 5. Start the server

- [ ] In a terminal, run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/15-agent-to-agent/server-src/TripConcierge.CompensationService.csproj --urls http://localhost:5000
  ```

- [ ] Confirm the console prints `Serving compensation-specialist at /a2a/compensation-specialist`.

  > [!NOTE]
  > Keep this terminal open. The client in Part 2 connects to this running server.

### Part 2 - Consume the remote agent from the concierge

#### 6. Open the client starter file

- [ ] In a second terminal, open `src/Program.cs` in the editor.

#### 7. Discover the remote agent (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  var resolver = new A2ACardResolver(new Uri(a2aServerUrl));
  AIAgent compensationSpecialist = await resolver.GetAIAgentAsync();
  ```

#### 8. Expose the remote agent as a function tool (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
  var concierge = client
      .AsAIAgent(
          model: model,
          instructions:
              "You are the Trip Disruption Concierge. For all compensation " +
              "and refund queries, use the compensation specialist tool - " +
              "never calculate compensation yourself. You may provide a " +
              "brief introduction or closing summary.",
          tools: [compensationSpecialist.AsAIFunction()]);
  ```

#### 9. Run a query that delegates over the network (TODO 3)

- [ ] Locate `// ── TODO 3` and replace the commented-out block with:

  ```csharp
  var query =
      "I was given only 3 hours' notice and my ticket cost AUD 420. " +
      "How much compensation can I claim, and how do I file it?";

  Console.ForegroundColor = ConsoleColor.Cyan;
  Console.WriteLine($"[User] {query}");
  Console.ResetColor();
  Console.WriteLine();

  var result = await concierge.RunAsync(query);

  Console.ForegroundColor = ConsoleColor.Green;
  Console.WriteLine($"[Agent] {result.Text}");
  Console.ResetColor();
  ```

### Part 3 - Run and verify

#### 10. Run the client starter

- [ ] With the server from Part 1 still running, run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/15-agent-to-agent/src/TripConcierge.AgentToAgent.csproj
  ```

#### 11. Confirm the delegation happened over A2A

- [ ] Confirm the console prints `[Agent]` with a compensation figure and next steps.
- [ ] Check the server terminal - it should show activity as the request arrives over HTTP.
- [ ] Stop the client, then stop the server with `Ctrl+C`.

## Validation

- The server terminal confirms `Serving compensation-specialist at /a2a/compensation-specialist`.
- The client resolves the agent card and prints `[Loop] Resolved remote Compensation Specialist via A2A agent card.`
- The concierge's final `[Agent]` response contains a specific compensation figure, proving the remote specialist actually ran.

## Congratulations 🎉

You moved a specialist agent out of process and reconnected it over the Agent-to-Agent protocol - the concierge calls `AsAIFunction()` on the remote agent exactly as it would a local C# function tool, now spanning a network boundary. Any A2A-compliant client, in any language or framework, could discover and call your Compensation Specialist the same way.

This is the newest module in the lab - an AG-UI module and a capstone are planned next.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Connection refused` when running the client | Confirm the server from Part 1 is still running on `http://localhost:5000` |
| `A2A_SERVER_URL` points to the wrong host | Set it in `.env` if the server runs on a different port or host |
| Agent card not found (404) | Confirm the server started without errors and `MapWellKnownAgentCard` ran before `app.Run()` |
| `FOUNDRY_PROJECT_ENDPOINT is not set` | Copy `shared/.env.example` to `.env` in the repository root and fill in your values |
| `NotImplementedException` | A TODO is still incomplete in either `server-src/Program.cs` or `src/Program.cs` |
