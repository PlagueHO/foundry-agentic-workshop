# 07. Memory & Context Providers

**Estimated time:** 20 minutes

![Microsoft Agent Framework overview: an open-source engine for building and orchestrating AI agents, summarised in five pillars — Unified SDK (AIAgent, AgentThread, and AgentTool primitives built on Microsoft.Extensions.AI), Local-first and cloud-agnostic (run agents locally then move the same code to Foundry Agent Service or any cloud containers), Multi-agent orchestration (sequential, concurrent, handoff, group chat, magentic, and workflow patterns), Tools and extensibility (out-of-the-box integrations plus functions, APIs, and MCP servers as tools), and Enterprise-grade foundations (approval flows, content-policy hooks, OpenTelemetry observability, and long-running execution).](../../../docs/assets/diagrams/agent-framework-introduction.png)

> [!IMPORTANT]
> This module builds on [Module 06](../06-knowledge-bases/README.md). The `AIContextProvider` pattern introduced there is extended here to store per-session state.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Understand `ProviderSessionState<T>` for per-session state.
- Override `StateKeys` to let the framework serialise your state correctly.
- Implement extraction logic in `StoreAIContextAsync`.
- Inject personalised instructions in `ProvideAIContextAsync`.

## Concepts

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

1. **`ProvideAIContextAsync`** (before model call) — read the stored profile and inject it as instructions so the model knows who it is talking to.
1. **`StoreAIContextAsync`** (after model call) — scan the user's messages for name and flight-number patterns and persist them for future turns.

## Steps

### Part 1 — Complete the starter code

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

#### 4. Implement StoreAIContextAsync (TODO 3)

- [ ] Scroll down to the `PassengerProfileMemory` class in `Program.cs`.
- [ ] Locate `// ── TODO 3` inside `StoreAIContextAsync` and implement regex extraction for the passenger name (`"my name is X"`) and flight number (`"flight AU\d+"`):

  ```csharp
  // Extract name
  var nameMatch = Regex.Match(userText, @"(?i)my name is (\w+)");
  if (nameMatch.Success)
      profile.Name = nameMatch.Groups[1].Value;

  // Extract flight number
  var flightMatch = Regex.Match(userText, @"(?i)flight (AU\d+)");
  if (flightMatch.Success)
      profile.FlightNumber = flightMatch.Groups[1].Value;
  ```

#### 5. Implement ProvideAIContextAsync (TODO 4)

- [ ] Locate `// ── TODO 4` inside `ProvideAIContextAsync` and inject the stored profile as instructions:

  ```csharp
  var instructions = new StringBuilder();
  if (!string.IsNullOrEmpty(profile.Name))
      instructions.AppendLine($"The passenger's name is {profile.Name}.");
  if (!string.IsNullOrEmpty(profile.FlightNumber))
      instructions.AppendLine($"Their flight number is {profile.FlightNumber}.");
  return new AIContext { Instructions = instructions.ToString() };
  ```

### Part 2 — Run and verify

#### 6. Run the starter

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
> **Next up → [Module 08: Session Persistence](../08-chat-history/README.md)**
> Serialise the session so a passenger can resume their disruption claim conversation across application restarts.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Agent does not remember the name | Ensure `StoreAIContextAsync` regex captures lowercase too: `(?i)my name is (\w+)` |
| `InvalidOperationException: Could not retrieve IChatClient` | The Foundry agent package must be registered — confirm `Microsoft.Agents.AI.Foundry` is referenced |
| `NotImplementedException` | A TODO is still incomplete |
