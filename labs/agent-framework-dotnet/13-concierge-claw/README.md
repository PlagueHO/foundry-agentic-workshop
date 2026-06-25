# 13. ConciergeClaw — Agent Harness

**Estimated time:** 35 minutes

![Agent Systems in Microsoft Agent Framework — diagram showing Agent Loops (goal-driven orchestration with a Coordinator Agent routing to specialist agents backed by Memory) alongside Workflows (deterministic, step-by-step execution). The ConciergeClaw harness uses the Agent Loop pattern, combining LoopAgent, FileMemoryProvider, and tool invocation into a single AsHarnessAgent() call.](../../../docs/assets/diagrams/agent-framework-agent-systems.png)

> [!IMPORTANT]
> This module builds on [Module 12](../12-observability/README.md). Ensure your environment is set up and `.env` is configured before continuing.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Build an `IChatClient` using the Foundry Responses API chain.
- Use `AsHarnessAgent()` with `HarnessAgentOptions` to wrap a chat client in the Agent Framework harness.
- Switch between plan and execute modes with `AgentModeProvider`.
- Register a custom function tool and observe the harness invoke it automatically.
- Understand how `FileMemoryProvider` persists session notes to disk.
- Configure `LoopAgent` with `TodoCompletionLoopEvaluator` to run until all todos are resolved.
- Export a live session with `SerializeSessionAsync` and restore it with `DeserializeSessionAsync`.
- Recognise where the agent loop runs in `HarnessAgent` versus `ChatClientAgent` and Foundry Hosted Agents.

## Concepts

### The Agent Harness

The Agent Framework harness is a batteries-included wrapper around any `IChatClient`. A single call to `AsHarnessAgent()` adds seven complementary features without requiring you to wire each one up manually:

| Feature | Provider / decorator | What it does |
|---|---|---|
| Planning | `TodoProvider` + `AgentModeProvider` | Tracks a structured todo list; switches between plan and execute modes |
| File memory | `FileMemoryProvider` | Writes per-session notes to disk so context survives restarts |
| File access | `FileAccessProvider` | Lets the agent read and write arbitrary files in your file system |
| Web search | Built-in hosted tool | Searches the web when supported by your Foundry Responses endpoint |
| Tool invocation | Built-in | Calls your function tools in-process and feeds results back to the model |
| Loop | `LoopAgent` | Repeatedly calls the inner agent until a `LoopEvaluator` says to stop |
| Session I/O | `SerializeSessionAsync` / `DeserializeSessionAsync` | Exports and restores the full session state including todo list and memory paths |

Use `Disable*` flags in `HarnessAgentOptions` to turn off any feature you don't need.

### The Responses API chain

Earlier modules used `client.AsAIAgent(model: ...)` as a shortcut. The harness requires an `IChatClient` directly, obtained by chaining through the Foundry project client:

```csharp
var credential = new AzureCliCredential();
IChatClient chatClient =
    new AIProjectClient(new Uri(endpoint), credential)
        .GetProjectOpenAIClient()
        .GetResponsesClient()
        .AsIChatClient(model);
```

This chain gives the harness access to Responses API features such as hosted web search.

For the full API reference see the [Microsoft Agent Framework documentation](https://learn.microsoft.com/en-us/agent-framework/overview/).

### Plan vs execute mode

The harness ships with two modes:

- **Plan mode** (default): the agent asks clarifying questions and presents a plan for your approval before acting.
- **Execute mode**: the agent acts immediately, following its todo list until all items are done.

Switch modes programmatically:

```csharp
var modeProvider = agent.GetService<AgentModeProvider>();
modeProvider?.SetMode(session, "execute");
```

### LoopAgent and TodoCompletionLoopEvaluator

`LoopAgent` keeps calling the inner agent until a `LoopEvaluator` signals completion. `TodoCompletionLoopEvaluator` stops the loop when all todos are marked done — only while in execute mode:

```csharp
LoopEvaluators     =
[
    new TodoCompletionLoopEvaluator(
        new TodoCompletionLoopEvaluatorOptions { Modes = ["execute"] }),
],
LoopAgentOptions   = new LoopAgentOptions { MaxIterations = 5 },
```

### Where does the loop run?

| Mode | Loop location | How to recognise |
|---|---|---|
| `ChatClientAgent` | **Your code** | You control the turn cycle; tools execute in-process |
| `HarnessAgent` | **Harness loop** | Framework manages tool calling, planning, memory, and approvals |
| `Foundry Hosted Agent` | **Agent Service** | Service manages the loop; you just call and await |

## Steps

### Part 1 — Build the IChatClient

#### 1. Open the starter file

- [ ] Open `src/Program.cs` in the editor.

#### 2. Build the IChatClient (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Harness] Building IChatClient via Foundry Responses API...");
  Console.ResetColor();

  var credential = new AzureCliCredential();
  IChatClient chatClient =
      new AIProjectClient(new Uri(endpoint), credential)
          .GetProjectOpenAIClient()
          .GetResponsesClient()
          .AsIChatClient(model);
  ```

  > [!NOTE]
  > `AzureCliCredential` picks up the session established by `az login`. Run `az login` before running the module if you haven't already.

### Part 2 — Create the HarnessAgent

#### 3. Wrap the IChatClient in a HarnessAgent (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Harness] Creating ConciergeClaw HarnessAgent...");
  Console.ResetColor();

  var agentFilesPath = Path.Combine(AppContext.BaseDirectory, "agent-files");

  AIAgent agent = chatClient.AsHarnessAgent(new HarnessAgentOptions
  {
      Name        = "ConciergeClaw",
      Description = "An empathetic trip disruption concierge that plans and resolves passenger disruptions end-to-end.",
      FileMemoryStore    = new FileSystemAgentFileStore(agentFilesPath),
      LoopEvaluators     =
      [
          new TodoCompletionLoopEvaluator(
              new TodoCompletionLoopEvaluatorOptions { Modes = ["execute"] }),
      ],
      LoopAgentOptions   = new LoopAgentOptions { MaxIterations = 5 },
      ChatOptions        = new ChatOptions
      {
          Instructions = conciergeInstructions,
          Tools        = [AIFunctionFactory.Create(GetFlightAlternatives)],
      },
  });

  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Harness] ConciergeClaw ready.");
  Console.ResetColor();
  Console.WriteLine();
  ```

  `AIFunctionFactory.Create(GetFlightAlternatives)` reads the `[Description]` attributes from the `GetFlightAlternatives` static function at the bottom of the file to generate the JSON schema the model uses when deciding whether to call the tool.

### Part 3 — Create the session

#### 4. Create a session (TODO 3)

- [ ] Locate `// ── TODO 3` and replace the single comment line with:

  ```csharp
  var session = await agent.CreateSessionAsync();
  ```

#### 5. Switch to execute mode (TODO 4)

- [ ] Locate `// ── TODO 4` and replace the commented-out block with:

  ```csharp
  var modeProvider = agent.GetService<AgentModeProvider>();
  modeProvider?.SetMode(session, "execute");

  var currentMode = modeProvider?.GetMode(session) ?? "unknown";
  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine($"[Harness] Session ready. Mode: {currentMode}");
  Console.ResetColor();
  Console.WriteLine();
  ```

### Part 4 — Run the first two turns

#### 6. Stream Turn 1 — Emma's disruption (TODO 5)

- [ ] Locate `// ── TODO 5` and replace the commented-out block with:

  ```csharp
  Console.ForegroundColor = ConsoleColor.Green;
  await foreach (var chunk in agent.RunStreamingAsync(query1, session: session))
  {
      if (chunk.Text is not null)
          Console.Write(chunk.Text);
  }
  Console.ResetColor();
  Console.WriteLine();
  Console.WriteLine();
  ```

  Watch the terminal for yellow `[Tool]` lines when the agent calls `get_flight_alternatives`, and for the LoopAgent iterating as it works through its todo list.

#### 7. Stream Turn 2 — follow-up (TODO 6)

- [ ] Locate `// ── TODO 6` and replace the commented-out block with:

  ```csharp
  Console.ForegroundColor = ConsoleColor.Green;
  await foreach (var chunk in agent.RunStreamingAsync(query2, session: session))
  {
      if (chunk.Text is not null)
          Console.Write(chunk.Text);
  }
  Console.ResetColor();
  Console.WriteLine();
  Console.WriteLine();
  ```

### Part 5 — Export, restore, and resume the session

#### 8. Export and restore the session (TODO 7)

- [ ] Locate `// ── TODO 7` and replace the commented-out block with:

  ```csharp
  JsonElement snapshot = await agent.SerializeSessionAsync(session);

  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Harness] Snapshot captured. Restoring session from snapshot...");
  Console.ResetColor();

  var restoredSession = await agent.DeserializeSessionAsync(snapshot);

  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Harness] Session restored. Continuing on restored session...");
  Console.ResetColor();
  Console.WriteLine();
  ```

  `SerializeSessionAsync` returns a `JsonElement` containing the full session state. `DeserializeSessionAsync` restores it into a fresh session object that can be used in any subsequent `RunAsync` or `RunStreamingAsync` call.

#### 9. Stream Turn 3 from the restored session (TODO 8)

- [ ] Locate `// ── TODO 8` and replace the commented-out block with:

  ```csharp
  Console.ForegroundColor = ConsoleColor.Green;
  await foreach (var chunk in agent.RunStreamingAsync(query3, session: restoredSession))
  {
      if (chunk.Text is not null)
          Console.Write(chunk.Text);
  }
  Console.ResetColor();
  Console.WriteLine();
  Console.WriteLine();
  ```

#### 10. Remove the NotImplementedException and run

- [ ] Delete the `throw new NotImplementedException(...)` line.
- [ ] Run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/13-concierge-claw/src/TripConcierge.ConciergeClaw.csproj
  ```

## Validation

- The terminal shows `[Harness] ConciergeClaw ready.` and `Mode: execute`.
- Yellow `[Tool]` lines appear when the agent calls `get_flight_alternatives`.
- Multiple model invocations are visible as the LoopAgent iterates through its todo list.
- `[Harness] Snapshot captured.` and `[Harness] Session restored.` appear in the export/import section.
- Turn 3 answers correctly using the restored session, referencing context from earlier turns.
- A `passenger-profile.md` file appears inside a timestamped session subfolder under `agent-files/` in the build output (for example `agent-files/20260625_123456_<guid>/passenger-profile.md`).

## Congratulations 🎉

You built the ConciergeClaw — a full Agent Framework harness agent that combines planning, file memory, tool invocation, and loop-driven execution in a single `AsHarnessAgent()` call. You also demonstrated portable session state with `SerializeSessionAsync` and `DeserializeSessionAsync`.

> [!TIP]
> **You've completed the Agent Framework .NET lab!** Return to the [lab README](../../README.md) to review what you built across all modules, or explore the [Microsoft Agent Framework samples](https://github.com/microsoft/agent-framework/tree/main/dotnet/samples) for further patterns.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `CS0103: The name 'HarnessAgentOptions' does not exist` | Run `dotnet restore` — confirm `Microsoft.Agents.AI.Harness` prerelease is in `Directory.Packages.props` |
| `OPENAI001` compiler warning | Add `#pragma warning disable OPENAI001` at the top of the file |
| `AuthenticationFailedException` | Run `az login` to refresh your local credential session |
| `InvalidOperationException: FOUNDRY_PROJECT_ENDPOINT is not set` | Copy `shared/.env.example` to `.env` in the repository root and fill in your values |
| `NotImplementedException` | A TODO is still incomplete — check `src/Program.cs` |
