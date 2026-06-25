# 07. Memory & Context Providers

**Estimated time:** 20 minutes

![Microsoft Agent Framework overview: an open-source engine for building and orchestrating AI agents, summarised in five pillars - Unified SDK (AIAgent, AgentThread, and AgentTool primitives built on Microsoft.Extensions.AI), Local-first and cloud-agnostic (run agents locally then move the same code to Foundry Agent Service or any cloud containers), Multi-agent orchestration (sequential, concurrent, handoff, group chat, magentic, and workflow patterns), Tools and extensibility (out-of-the-box integrations plus functions, APIs, and MCP servers as tools), and Enterprise-grade foundations (approval flows, content-policy hooks, OpenTelemetry observability, and long-running execution).](../../../docs/assets/diagrams/agent-framework-introduction.png)

> [!IMPORTANT]
> This module builds on [Module 06](../06-knowledge-bases/README.md). The `AIContextProvider` pattern introduced there is extended here to store per-session state.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Extend `AIContextProvider` to build a custom memory component.
- Understand `ProviderSessionState<T>` for per-session state.
- Override `StateKeys` to let the framework serialise your state correctly.
- Return an `AIContext` with injected instructions from `ProvideAIContextAsync`.
- Implement extraction logic in `StoreAIContextAsync`.

## Concepts

For full API details, see the [Microsoft Agent Framework documentation](https://learn.microsoft.com/en-us/agent-framework/overview/).

### AIContextProvider

`AIContextProvider` is the abstract base class your memory class extends. Override two methods to plug into the agent pipeline:

```csharp
internal sealed class PassengerProfileMemory : AIContextProvider
{
    // Expose the keys the framework uses to serialise this provider's state.
    public override IReadOnlyList<string> StateKeys => [_state.StateKey];

    // Called BEFORE the model call - inject stored context as instructions.
    protected override ValueTask<AIContext> ProvideAIContextAsync(
        InvokingContext context, CancellationToken cancellationToken = default)
    { ... }

    // Called AFTER the model call - extract and persist new information.
    protected override ValueTask StoreAIContextAsync(
        InvokedContext context, CancellationToken cancellationToken = default)
    { ... }
}
```

Both methods receive `context.Session`, which is used with `ProviderSessionState<T>` to read and write per-session data.

### ProviderSessionState\<T>

`ProviderSessionState<T>` is a helper that stores a strongly-typed value alongside the agent session, keyed by a name you choose:

```csharp
var state = new ProviderSessionState<PassengerProfile>(
    _ => new PassengerProfile(),   // factory for an empty default
    GetType().Name);               // storage key

var profile = state.GetOrInitializeState(context.Session);
state.SaveState(context.Session, profile);
```

### Provider flow

1. **`ProvideAIContextAsync`** (before model call) - read the stored profile and inject it as instructions so the model knows who it is talking to.
1. **`StoreAIContextAsync`** (after model call) - scan the user's messages for name and flight-number patterns and persist them for future turns.

## Steps

### Part 1 - Complete the starter code

#### 1. Open the starter file

- [ ] Open `src/Program.cs` in the editor.

#### 2. Obtain an IChatClient (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  IChatClient chatClient = projectClient
      .AsAIAgent(new ChatClientAgentOptions { ChatOptions = new() { ModelId = model } })
      .GetService<IChatClient>()
      ?? throw new InvalidOperationException("Could not retrieve IChatClient.");
  ```

#### 3. Wrap with PassengerProfileMemory (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
  AIAgent agent = chatClient.AsAIAgent(new ChatClientAgentOptions
  {
      ChatOptions = new()
      {
          ModelId = model,
          Instructions =
              "You are the Trip Disruption Concierge. " +
              "You help passengers who have experienced flight disruptions. " +
              "Always address the passenger by name if known. " +
              "Reference their specific flight number when relevant."
      },
      AIContextProviders = [new PassengerProfileMemory()]
  });

  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Agent] Agent ready with passenger profile memory.");
  Console.ResetColor();
  Console.WriteLine();
  ```

#### 4. Complete the multi-turn session (TODO 3)

- [ ] Locate `// ── TODO 3` in the top-level code and replace the commented-out block with:

  ```csharp
  var session = await agent.CreateSessionAsync();

  Console.ForegroundColor = ConsoleColor.Green;
  Console.WriteLine($"[Agent] {await agent.RunAsync(
      \"Hi, my name is Emma Chen. My flight AU123 AKL\u2192SYD was cancelled with \" +
      \"3 hours' notice. What are my options?\",
      session: session)}");
  Console.ResetColor();
  Console.WriteLine();

  Console.ForegroundColor = ConsoleColor.Cyan;
  Console.WriteLine("[User] What compensation is typically available for a cancellation?");
  Console.ResetColor();
  Console.WriteLine();

  Console.ForegroundColor = ConsoleColor.Green;
  Console.WriteLine($"[Agent] {await agent.RunAsync(
      \"What compensation is typically available for a cancellation like mine?\",
      session: session)}");
  Console.ResetColor();
  Console.WriteLine();

  Console.ForegroundColor = ConsoleColor.Cyan;
  Console.WriteLine("[User] Can you remind me - what was my flight number?");
  Console.ResetColor();
  Console.WriteLine();

  Console.ForegroundColor = ConsoleColor.Green;
  Console.WriteLine($"[Agent] {await agent.RunAsync(
      \"By the way, can you remind me - what was my flight number?\",
      session: session)}");
  Console.ResetColor();
  Console.WriteLine();
  ```

- [ ] Remove the `throw new NotImplementedException(...)` line immediately below the TODO block.

#### 5. Implement StoreAIContextAsync (TODO 4)

- [ ] Scroll down to the `PassengerProfileMemory` class in `Program.cs`.
- [ ] Locate `// ── TODO 4` inside `StoreAIContextAsync` and implement regex extraction for the passenger name and flight number:

  ```csharp
  foreach (var msg in context.RequestMessages.Where(m => m.Role == ChatRole.User))
  {
      var text = msg.Text ?? string.Empty;

      // Extract name
      var nameMatch = Regex.Match(text, @"(?i)my name is (\w+)");
      if (nameMatch.Success)
          profile.Name = nameMatch.Groups[1].Value;

      // Extract flight number
      var flightMatch = Regex.Match(text, @"(?i)flight (AU\d+)");
      if (flightMatch.Success)
          profile.FlightNumber = flightMatch.Groups[1].Value;
  }
  _state.SaveState(context.Session, profile);
  ```

#### 6. Implement ProvideAIContextAsync (TODO 5)

- [ ] Locate `// ── TODO 5` inside `ProvideAIContextAsync` and inject the stored profile as instructions:

  ```csharp
  var sb = new StringBuilder();
  if (profile.Name is not null)
      sb.AppendLine($"The passenger's name is {profile.Name}.");
  if (profile.FlightNumber is not null)
      sb.AppendLine($"Their flight number is {profile.FlightNumber}.");
  return new AIContext { Instructions = sb.ToString() };
  ```

### Part 2 - Run and verify

#### 7. Run the starter

- [ ] In a terminal, run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/07-memory/src/TripConcierge.Memory.csproj
  ```

## Validation

- The agent addresses Emma by name after she introduces herself, even in later turns where her name is no longer in the prompt.
- The agent correctly recalls the flight number `AU123` throughout the session.
- Yellow `[Memory]` lines show the profile being built up turn-by-turn.

## Congratulations 🎉

You implemented a custom memory provider that extracts passenger details from natural language and injects them as personalised instructions before every model call. The agent now addresses Emma by name and recalls her flight number without her repeating them.

> [!TIP]
> **Next up → [Module 08: Session Persistence (Chat History)](../08-chat-history/README.md)**
> Serialise the session so a passenger can resume their disruption claim conversation across application restarts.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Agent does not remember the name | Ensure `StoreAIContextAsync` regex captures lowercase too: `(?i)my name is (\w+)` |
| `InvalidOperationException: Could not retrieve IChatClient` | The Foundry agent package must be registered - confirm `Microsoft.Agents.AI.Foundry` is referenced |
| `AuthenticationFailedException` | Run `az login` and confirm `FOUNDRY_PROJECT_ENDPOINT` in `.env` matches the provisioned project |
| `NotImplementedException` | A TODO is still incomplete |
