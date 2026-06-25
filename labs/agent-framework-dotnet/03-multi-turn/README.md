# 03. Multi-turn Conversations

**Estimated time:** 15 minutes

![Microsoft Agent Framework overview: an open-source engine for building and orchestrating AI agents, summarised in five pillars - Unified SDK (AIAgent, AgentThread, and AgentTool primitives built on Microsoft.Extensions.AI), Local-first and cloud-agnostic (run agents locally then move the same code to Foundry Agent Service or any cloud containers), Multi-agent orchestration (sequential, concurrent, handoff, group chat, magentic, and workflow patterns), Tools and extensibility (out-of-the-box integrations plus functions, APIs, and MCP servers as tools), and Enterprise-grade foundations (approval flows, content-policy hooks, OpenTelemetry observability, and long-running execution).](../../../docs/assets/diagrams/agent-framework-introduction.png)

> [!IMPORTANT]
> This module builds on [Module 02](../02-first-agent/README.md). You must have a working `AIAgent` from Module 02 before continuing.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Create an `AgentSession` with `agent.CreateSessionAsync()`.
- Pass the session to each `RunAsync` call so context is preserved.
- Observe how the agent references earlier turns without being re-prompted.

## Concepts

### Why sessions are needed

In Module 02, every `RunAsync` call was independent - the agent had no memory of earlier messages. That works for single-shot queries but not for a support conversation where the passenger must not repeat themselves every turn.

An `AgentSession` solves this by maintaining the conversation history. Pass the **same session** to every `RunAsync` call and the model sees the full message history before generating each response.

### Creating and using a session

```csharp
var session = await agent.CreateSessionAsync();

// Turn 1 - agent receives only this message
var result1 = await agent.RunAsync("My name is Emma.", session: session);

// Turn 2 - agent sees Turn 1 + this message
var result2 = await agent.RunAsync("What did I just tell you?", session: session);
```

The session maps server-side to a durable Foundry thread. You can correlate conversation turns in the Foundry portal Traces tab - run the solution and look for the session in the Conversations grid.

### What the session stores

The session accumulates every user and assistant message in order. Context providers (introduced in Module 07) can also attach state to the session, such as a passenger profile.

> [!WARNING]
> The session is an **in-memory object**. It is lost when the process stops, and it is not shared between service instances. This is fine for a local demo but unsuitable for production services that restart, scale out, or need durable conversation history. See the [Extra Credit](#extra-credit---session-persistence) section for durable alternatives, and [Module 08](../08-chat-history/README.md) for a full walkthrough of serialisation and restore.

<!-- markdownlint-disable-next-line MD028 -->
> [!NOTE]
> For the full `AgentSession` API reference and further background, see the [Microsoft Agent Framework .NET SDK documentation](https://learn.microsoft.com/en-us/agent-framework/).

## Steps

### Part 1 - Complete the starter code

#### 1. Open the starter file

- [ ] Open `src/Program.cs` in the editor.

#### 2. Create the client and agent (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  var credential = new AzureCliCredential();
  var client = new AIProjectClient(new Uri(endpoint), credential);
  var agent = client.AsAIAgent(
      model: model,
      instructions:
          "You are the Trip Disruption Concierge. Help passengers with flight " +
          "disruptions. Remember everything from earlier in the conversation - " +
          "the passenger must not need to repeat information they have already " +
          "provided.");
  ```

#### 3. Create a session (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
  var session = await agent.CreateSessionAsync();
  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Loop] Session ready.");
  Console.ResetColor();
  Console.WriteLine();
  ```

  All subsequent `RunAsync` calls must pass this same `session` object.

#### 4. Run Turn 1 (TODO 3)

- [ ] Locate `// ── TODO 3` and replace the commented-out block with:

  ```csharp
  var turn1 = "My name is Emma. My flight AU123 AKL→SYD was just cancelled. " +
              "I have a separate connecting flight SYD→MEL. What should I do first?";

  Console.ForegroundColor = ConsoleColor.Cyan;
  Console.WriteLine($"[User] {turn1}");
  Console.ResetColor();
  Console.WriteLine();

  var result1 = await agent.RunAsync(turn1, session: session);

  Console.ForegroundColor = ConsoleColor.Green;
  Console.WriteLine($"[Agent] {result1.Text}");
  Console.ResetColor();
  Console.WriteLine();
  ```

#### 5. Run Turn 2 and Turn 3 (TODO 4)

- [ ] Locate `// ── TODO 4` and replace the commented-out block with the additional turns already commented out there.

  > [!NOTE]
  > Notice that the Turn 2 message does not repeat Emma's name or the flight number - the session carries that context automatically.

### Part 2 - Run and verify

#### 6. Run the starter

- [ ] In a terminal, run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/03-multi-turn/src/TripConcierge.MultiTurn.csproj
  ```

## Validation

- The session completes all 3 turns without errors.
- In Turn 2 the agent references earlier context from Turn 1 (such as the AKL→SYD route or the Melbourne connecting flight) without it being re-stated.
- In Turn 3 the agent synthesises all previous context into a summary recommendation.
- _(Solution only)_ Each turn also shows a `[Loop] Turn N - RunAsync...` timing line.

## Congratulations 🎉

You held a persistent multi-turn conversation using an `AgentSession`. The agent remembered Emma's name, flight number, and connecting flight across every turn - without any repeated context from your code.

> [!TIP]
> **Next up → [Module 04: Function Tools](../04-function-tools/README.md)**
> Give the agent a local C# function it can call to calculate compensation - and watch the tool invocation logged in your terminal.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Agent forgets earlier turns | Confirm you are passing the **same** `session` object to every `RunAsync` call |
| `CreateSessionAsync` not found | Confirm the `Microsoft.Agents.AI.Foundry` package restored correctly |
| `NotImplementedException` | A TODO is still incomplete |
| `AuthenticationFailedException` | Run `az login` and confirm the signed-in account has Foundry User rights on the project |

## Extra Credit - Session Persistence

The `AgentSession` in this module lives entirely in process memory. If the application restarts, the session is gone and the next conversation starts from scratch. The following approaches address this at increasing levels of production-readiness.

### Option 1 - Serialize and restore (manual persistence)

The Agent Framework provides `SerializeSessionAsync` / `DeserializeSessionAsync` to export the full session state to a portable `JsonElement` that you can write to any storage medium:

```csharp
// Capture the session after a conversation
JsonElement snapshot = await agent.SerializeSessionAsync(session);

// Write to disk, Redis, SQL, or any store
File.WriteAllText("session.json", JsonSerializer.Serialize(snapshot));

// ── On the next application start ────────────────────────────────────────────

var stored = JsonSerializer.Deserialize<JsonElement>(
    File.ReadAllText("session.json"));

// Restore on a brand-new agent instance
var restored = await agent.DeserializeSessionAsync(stored);

// Continue - the agent remembers everything from before the restart
var result = await agent.RunAsync("So, where were we?", session: restored);
```

A complete working example is in the Agent Framework repository:
[Agent_Step03_PersistedConversations](https://github.com/microsoft/agent-framework/tree/main/dotnet/samples/02-agents/Agents/Agent_Step03_PersistedConversations)

[Module 08](../08-chat-history/README.md) of this workshop walks through this pattern end-to-end.

> [!NOTE]
> Manual serialization pushes every production concern onto your code - concurrent writers can overwrite each other's snapshot, a crash mid-write corrupts the store, and every service replica must reach the same storage. This approach is appropriate for single-instance tools and local development, not for scaled-out services.

### Option 2 - Foundry Agent Service (server-managed threads)

When you target [Foundry Agent Service](https://learn.microsoft.com/azure/ai-foundry/agents/overview) using `AIProjectClient`, thread storage is managed server-side automatically. The session ID is durable across restarts and scales horizontally without any extra code:

```csharp
// AIProjectClient routes to Foundry Agent Service - threads are persisted in Azure
var client = new AIProjectClient(new Uri(endpoint), credential);
var agent = client.AsAIAgent(model: model, instructions: "...");

// Session ID is stable across process restarts - no serialization needed
var session = await agent.CreateSessionAsync();
```

This is exactly what the solution code in this module already does. The `AIProjectClient` routes all thread state to Azure, so you get cloud-durable sessions with no extra plumbing.

### Option 3 - Custom `ChatHistoryProvider` (bring your own store)

For self-hosted or multi-cloud deployments, you can plug in any storage backend by implementing a `ChatHistoryProvider`. The framework passes a session state bag to your provider on every turn; you read and write history against your own store. The session pointer (a key or ID into your store) round-trips automatically through session serialization.

A [reference implementation using an in-process vector store](https://github.com/microsoft/agent-framework/tree/main/dotnet/samples/02-agents/Agents/Agent_Step04_3rdPartyChatHistoryStorage) is available in the Agent Framework sample repository. Swap `InMemoryVectorStore` for a cloud connector such as `AzureCosmosDBNoSQLVectorStore` to get a fully durable, horizontally scalable conversation store.

### Choosing the right option

| Option | Managed by | Best for |
|---|---|---|
| Serialize / restore to file or DB | Your code | Single-instance tools, local development |
| Foundry Agent Service (server threads) | Azure | Cloud-hosted agents deployed to Foundry |
| Custom `ChatHistoryProvider` + Cosmos DB | Your code + Azure | Self-hosted or multi-cloud services |
