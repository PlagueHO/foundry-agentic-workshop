# 08. Session Persistence (Chat History)

**Estimated time:** 20 minutes

![Microsoft Agent Framework overview: an open-source engine for building and orchestrating AI agents, summarised in five pillars — Unified SDK (AIAgent, AgentThread, and AgentTool primitives built on Microsoft.Extensions.AI), Local-first and cloud-agnostic (run agents locally then move the same code to Foundry Agent Service or any cloud containers), Multi-agent orchestration (sequential, concurrent, handoff, group chat, magentic, and workflow patterns), Tools and extensibility (out-of-the-box integrations plus functions, APIs, and MCP servers as tools), and Enterprise-grade foundations (approval flows, content-policy hooks, OpenTelemetry observability, and long-running execution).](../../../docs/assets/diagrams/agent-framework-introduction.png)

> [!IMPORTANT]
> This module builds on [Module 03](../03-multi-turn/README.md) (sessions) and [Module 07](../07-memory/README.md) (session state). You should be comfortable with both patterns before continuing.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Use `agent.SerializeSessionAsync()` to capture the full conversation state.
- Use `agent.DeserializeSessionAsync()` to restore it in a new agent instance.
- Understand what state is preserved (messages, context provider data).
- Demonstrate that the restored agent recalls facts from before the restart.

## Concepts

### Session serialisation

Every `AIAgent` session is a lightweight object that contains the conversation history and any context-provider state. Two methods let you move it in and out of a portable JSON representation:

```csharp
// Capture
JsonElement snapshot = await agent.SerializeSessionAsync(session);

// Restore (can be done on a completely new AIAgent instance)
IAgentSession restored = await agent.DeserializeSessionAsync(snapshot);
```

This is the foundation for persistent chat history, resumable workflows, and stateful Foundry Hosted Agents.

### What is preserved

- The full message history (user, assistant, tool messages).
- Any `ProviderSessionState<T>` values stored by attached context providers.

### What is not preserved

- Open HTTP connections, in-flight API calls, or local in-memory caches that live outside the session (e.g., the `_cachedContext` in Module 06).

## Steps

### Part 1 — Complete the starter code

#### 1. Open the starter file

- [ ] Open `src/Program.cs` in the editor.

#### 2. Create the agent and initial session (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  AIAgent agent = new AIProjectClient(new Uri(endpoint), credential)
      .AsAIAgent(
          model: model,
          instructions:
              "You are the Trip Disruption Concierge. " +
              "You help passengers with flight disruption claims. " +
              "Remember details shared earlier in the conversation.");

  var session = await agent.CreateSessionAsync();
  ```

#### 3. Run the initial conversation turns (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with the initial turns already commented out there.

#### 4. Serialise the session (TODO 3)

- [ ] Locate `// ── TODO 3` and replace the commented-out block with:

  ```csharp
  var snapshot = await agent.SerializeSessionAsync(session);
  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Session] State serialised. Simulating app restart...");
  Console.ResetColor();
  Console.WriteLine();
  ```

#### 5. Restore the session and verify recall (TODO 4)

- [ ] Locate `// ── TODO 4` and replace the commented-out block with the restore and recall code already commented out there.

  > [!NOTE]
  > Create a **fresh** `AIAgent` instance before calling `DeserializeSessionAsync`. This simulates a real application restart, where the original agent object no longer exists.

### Part 2 — Run and verify

#### 6. Run the starter

- [ ] In a terminal, run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/08-chat-history/src/TripConcierge.ChatHistory.csproj
  ```

## Validation

- The console shows `[Session] State serialised.` then `[Session] Simulating restart...`.
- After the simulated restart, the agent correctly answers `"My flight AU123"` when asked to recall the flight number from the original conversation.

## Congratulations 🎉

You captured a full session snapshot and restored it into a brand-new agent instance. The restored agent recalled the flight number and passenger name from before the simulated restart — exactly what a real-world resumable support portal would need.

> [!TIP]
> **Next up → [Module 09: Multi-agent Orchestration](../09-multi-agent/README.md)**
> Build a concierge that delegates to specialist agents for rebooking, accommodation, and compensation — and watch the routing decisions logged in your terminal.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Restored agent does not remember the flight | Ensure you pass the same `session` object to both turns before serialising |
| `JsonException` on deserialise | The snapshot must be the raw `JsonElement` returned by `SerializeSessionAsync` |
| `NotImplementedException` | A TODO is still incomplete |
