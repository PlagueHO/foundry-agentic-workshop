# 03. Multi-turn Conversations

**Estimated time:** 15 minutes

![Microsoft Agent Framework overview: an open-source engine for building and orchestrating AI agents, summarised in five pillars — Unified SDK (AIAgent, AgentThread, and AgentTool primitives built on Microsoft.Extensions.AI), Local-first and cloud-agnostic (run agents locally then move the same code to Foundry Agent Service or any cloud containers), Multi-agent orchestration (sequential, concurrent, handoff, group chat, magentic, and workflow patterns), Tools and extensibility (out-of-the-box integrations plus functions, APIs, and MCP servers as tools), and Enterprise-grade foundations (approval flows, content-policy hooks, OpenTelemetry observability, and long-running execution).](../../../docs/assets/diagrams/agent-framework-introduction.png)

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

In Module 02, every `RunAsync` call was independent — the agent had no memory of earlier messages. That works for single-shot queries but not for a support conversation where the passenger must not repeat themselves every turn.

An `AgentSession` solves this by maintaining the conversation history. Pass the **same session** to every `RunAsync` call and the model sees the full message history before generating each response.

### Creating and using a session

```csharp
var session = await agent.CreateSessionAsync();

// Turn 1 — agent receives only this message
var result1 = await agent.RunAsync("My name is Emma.", session: session);

// Turn 2 — agent sees Turn 1 + this message
var result2 = await agent.RunAsync("What did I just tell you?", session: session);
```

The session ID is stable and unique. If you print it, you can correlate turns in portal traces.

### What the session stores

The session accumulates every user and assistant message in order. Context providers (introduced in Module 07) can also attach state to the session, such as a passenger profile. The session is an in-memory object — it does not automatically persist across application restarts. Module 08 covers serialisation and restore.

## Steps

### Part 1 — Complete the starter code

#### 1. Open the starter file

- [ ] Open `src/Program.cs` in the editor.

#### 2. Create the client and agent (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  var credential = new DefaultAzureCredential();
  var client = new AIProjectClient(new Uri(endpoint), credential);
  var agent = client.AsAIAgent(
      model: model,
      instructions:
          "You are the Trip Disruption Concierge. Help passengers with flight " +
          "disruptions. Remember everything from earlier in the conversation — " +
          "the passenger must not need to repeat information they have already " +
          "provided.");
  ```

#### 3. Create a session (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
  var session = await agent.CreateSessionAsync();
  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine($"[Loop] Session created — ID: {session.Id}");
  Console.ResetColor();
  Console.WriteLine();
  ```

  All subsequent `RunAsync` calls must pass this same `session` object.

#### 4. Run Turn 1 (TODO 3)

- [ ] Locate `// ── TODO 3` and replace the commented-out block with:

  ```csharp
  var turn1 = "My name is Emma. My flight AU123 AKL\u2192SYD was just cancelled. " +
              "I have a separate connecting flight SYD\u2192MEL. What should I do first?";

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
  > Notice that the Turn 2 message does not repeat Emma's name or the flight number — the session carries that context automatically.

### Part 2 — Run and verify

#### 6. Run the starter

- [ ] In a terminal, run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/03-multi-turn/src/TripConcierge.MultiTurn.csproj
  ```

## Validation

- Each turn shows a `[Loop] Turn N` counter in the terminal.
- In Turn 2 the agent references the flight number (AU123) from Turn 1 without it being re-stated.
- In Turn 3 the agent synthesises all previous context into a summary recommendation.

## Congratulations 🎉

You held a persistent multi-turn conversation using an `AgentSession`. The agent remembered Emma's name, flight number, and connecting flight across every turn — without any repeated context from your code.

> [!TIP]
> **Next up → [Module 04: Function Tools](../04-function-tools/README.md)**
> Give the agent a local C# function it can call to calculate compensation — and watch the tool invocation logged in your terminal.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Agent forgets earlier turns | Confirm you are passing the **same** `session` object to every `RunAsync` call |
| `CreateSessionAsync` not found | Confirm the `Microsoft.Agents.AI.Foundry` package restored correctly |
| `NotImplementedException` | A TODO is still incomplete |
