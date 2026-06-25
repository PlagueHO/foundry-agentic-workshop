# 02. Your First Agent

**Estimated time:** 20 minutes

![Microsoft Agent Framework overview: an open-source engine for building and orchestrating AI agents, summarised in five pillars - Unified SDK (AIAgent, AgentThread, and AgentTool primitives built on Microsoft.Extensions.AI), Local-first and cloud-agnostic (run agents locally then move the same code to Foundry Agent Service or any cloud containers), Multi-agent orchestration (sequential, concurrent, handoff, group chat, magentic, and workflow patterns), Tools and extensibility (out-of-the-box integrations plus functions, APIs, and MCP servers as tools), and Enterprise-grade foundations (approval flows, content-policy hooks, OpenTelemetry observability, and long-running execution).](../../../docs/assets/diagrams/what-is-an-agent.png)

> [!IMPORTANT]
> This module builds on [Module 01](../01-setup/README.md). Complete Module 01 and confirm your `.env` is configured before starting here.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Create an `AIProjectClient` using `AzureCliCredential`.
- Create an `AIAgent` using `client.AsAIAgent()`.
- Run a single-turn prompt with `RunAsync` and print the response.
- Stream a second response token-by-token with `RunStreamingAsync`.

## Concepts

### What is AIProjectClient?

`AIProjectClient` is the entry point to your Azure AI Foundry project from .NET. You construct it with your project endpoint and an Azure credential - no API keys required. Once created, the client gives you access to models, agents, and other Foundry resources inside the project.

```csharp
var credential = new AzureCliCredential();
var client = new AIProjectClient(new Uri(endpoint), credential);
```

`AzureCliCredential` authenticates using the identity from your active `az login` session. In environments where multiple credential sources are present - such as VS Code, GitHub Copilot, or managed identity - `DefaultAzureCredential` may resolve a different identity before reaching the CLI, which can cause permission errors. Using `AzureCliCredential` makes the authentication path explicit.

### What is AIAgent?

`AIAgent` is the core agent abstraction in the Microsoft Agent Framework. You obtain one by calling `.AsAIAgent()` on a client, providing a model and system instructions:

```csharp
var agent = client.AsAIAgent(
    model: "chat",
    instructions: "You are a helpful travel assistant.");
```

The agent holds no conversation state by default - each `RunAsync` call is an independent single turn. You add state in [Module 03](../03-multi-turn/README.md) using `AgentSession`.

### Single-turn vs streaming

The framework provides two ways to get a response from an agent:

| Method | Returns | When to use |
|---|---|---|
| `RunAsync` | A completed `AgentResult` | Batch scenarios, offline processing, simple scripts |
| `RunStreamingAsync` | An `IAsyncEnumerable<AgentChunk>` | Real-time UIs, long responses, CLI output |

Streaming prints each token as the model generates it, which makes the response feel faster and lets you react to partial output.

For a deeper introduction to the framework, see the [Microsoft Agent Framework documentation](https://learn.microsoft.com/en-us/agent-framework/overview/) on Microsoft Learn.

## Steps

### Part 1 - Complete the starter code

#### 1. Open the starter file

- [ ] Open `src/Program.cs` in the editor.
- [ ] Read through the file to see the four `TODO` comments and the console output already wired up between them.

#### 2. Create the project client (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  var credential = new AzureCliCredential();
  var client = new AIProjectClient(new Uri(endpoint), credential);
  ```

  `AzureCliCredential` uses your active `az login` session directly. `AIProjectClient` connects to the Foundry project at the endpoint in your `.env`.

#### 3. Create the agent (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
  var agent = client.AsAIAgent(
      model: model,
      instructions:
          "You are the Trip Disruption Concierge. You help airline passengers " +
          "understand their rights and options when flights are cancelled, delayed, " +
          "or disrupted. Be concise, empathetic, and actionable. " +
          "Focus on practical next steps the passenger can take right now.");
  ```

  The `model` variable is read from the `AGENT_MODEL` environment variable (defaulting to `chat`). The instructions define the agent's role for every turn.

#### 4. Run a single-turn prompt (TODO 3)

- [ ] Locate `// ── TODO 3` and replace the commented-out block with:

  ```csharp
  var result = await agent.RunAsync(
      "My flight AKL\u2192SYD was cancelled with only 3 hours' notice. " +
      "What are my rights as a passenger?");

  Console.ForegroundColor = ConsoleColor.Green;
  Console.WriteLine($"[Agent] {result.Text}");
  Console.ResetColor();
  Console.WriteLine();
  ```

  `RunAsync` sends the message, waits for the full response, and returns it as `result.Text`.

#### 5. Stream a second response (TODO 4)

We will send a second prompt to the agent and stream the response token-by-token. This is a separate prompt to demonstrate the streaming API, but in a real application you would typically continue the conversation with the same agent.

- [ ] Locate `// ── TODO 4` and replace the commented-out block with:

  ```csharp
  Console.ForegroundColor = ConsoleColor.Green;
  Console.Write("[Agent] ");
  await foreach (var chunk in agent.RunStreamingAsync(
      "Can I demand a full refund, or must I accept the rebooking?"))
  {
      if (chunk.Text is not null)
          Console.Write(chunk.Text);
  }
  Console.ResetColor();
  ```

  `RunStreamingAsync` returns each token as it is generated. The `await foreach` loop prints each chunk immediately, producing a live-streaming effect.

### Part 2 - Run and verify

#### 6. Run the starter

- [ ] In a terminal, run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/02-first-agent/src/TripConcierge.FirstAgent.csproj
  ```

- [ ] Confirm the terminal prints a green `[Agent]` block answering the passenger rights question.
- [ ] Confirm a second `[Agent]` block streams the response one token at a time.

## Validation

- The terminal prints a coloured `[Agent]` response to the first question.
- A second response streams token-by-token to the console.
- Both responses address the passenger rights question about a cancelled flight.

> [!NOTE]
> The reference `solution/` includes additional diagnostic output - status lines, timing, and a completion message - added for readability. Your completed starter shows only the `[User]` and `[Agent]` blocks above.

## Congratulations 🎉

You created your first agent with the Microsoft Agent Framework. You connected to an Azure AI Foundry project using a keyless credential, gave the model a role with system instructions, and retrieved a response both as a completed result and as a real-time token stream.

> [!TIP]
> **Next up → [Module 03: Multi-turn Conversations](../03-multi-turn/README.md)**
> Add an `AgentSession` so the agent remembers what Emma said earlier - no more repeating context across turns.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `FOUNDRY_PROJECT_ENDPOINT is not set` | Copy `shared/.env.example` to `.env` in the repository root and fill in your Foundry details |
| `AuthenticationFailedException` | Run `az login` or confirm your managed identity has the correct role |
| `NotImplementedException` | A TODO is still incomplete - check the starter code |
