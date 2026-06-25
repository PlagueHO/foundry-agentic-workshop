# 04. Function Tools

**Estimated time:** 20 minutes

![Microsoft Agent Framework overview: an open-source engine for building and orchestrating AI agents, summarised in five pillars - Unified SDK (AIAgent, AgentThread, and AgentTool primitives built on Microsoft.Extensions.AI), Local-first and cloud-agnostic (run agents locally then move the same code to Foundry Agent Service or any cloud containers), Multi-agent orchestration (sequential, concurrent, handoff, group chat, magentic, and workflow patterns), Tools and extensibility (out-of-the-box integrations plus functions, APIs, and MCP servers as tools), and Enterprise-grade foundations (approval flows, content-policy hooks, OpenTelemetry observability, and long-running execution).](../../../docs/assets/diagrams/agent-framework-introduction.png)

> [!IMPORTANT]
> This module builds on [Module 02](../02-first-agent/README.md). The `AIAgent` pattern from Module 02 is used here with an added tool.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Create a typed C# function and register it as an agent tool with `AIFunctionFactory.Create()`.
- Pass tools to an agent via the `tools:` parameter in `AsAIAgent()`.
- Observe the `[Tool]` log lines that show when the agent invokes the tool.

## Concepts

### What is a function tool?

A **function tool** is a local C# method that the agent can call during its reasoning loop. When the model determines a tool call is needed, the framework:

1. Extracts the arguments from the model's response.
1. Calls your function with those arguments.
1. Injects the return value back into the conversation as a tool result.
1. Asks the model to continue reasoning with the result.

Your code never manually handles the tool-call protocol - the framework manages it transparently.

### AIFunctionFactory.Create

`AIFunctionFactory.Create` wraps any lambda or method as an `AIFunction` the framework can register:

```csharp
var myTool = AIFunctionFactory.Create(
    (string input) => $"Processed: {input}",
    "my_tool",
    "Describe what this tool does so the model knows when to call it.");
```

Use `[Description]` attributes on parameters to guide the model when choosing argument values.

For the full API reference, see the [Microsoft Agent Framework overview](https://learn.microsoft.com/en-us/agent-framework/overview/) in the Microsoft documentation.

### Attaching tools to an agent

Pass tools via the `tools:` parameter when calling `AsAIAgent()`:

```csharp
var agent = client
    .AsAIAgent(model: model, instructions: "...", tools: [myTool]);
```

The agent will automatically call `myTool` when the model decides it is needed.

## Steps

### Part 1 - Define the function tool

#### 1. Open the starter file

- [ ] Open `src/Program.cs` in the editor.

#### 2. Create the compensation function (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  var calculateCompensation = AIFunctionFactory.Create(
      (
          [Description("Hours of delay, or hours of notice given before cancellation")]
          int delayOrNoticeHours,
          [Description("Original one-way ticket price in Australian dollars")]
          decimal ticketPriceAud
      ) =>
      {
          Console.ForegroundColor = ConsoleColor.Yellow;
          Console.WriteLine(
              $"[Tool] → calculate_compensation(" +
              $"delayHours={delayOrNoticeHours}, ticketPrice={ticketPriceAud:C2})");
          Console.ResetColor();

          decimal compensation = delayOrNoticeHours switch
          {
              < 3 => 0m,
              < 5 => ticketPriceAud * 0.25m,
              _ => ticketPriceAud * 0.50m,
          };

          Console.ForegroundColor = ConsoleColor.Yellow;
          Console.WriteLine($"[Tool] ← compensation = {compensation:C2}");
          Console.ResetColor();
          Console.WriteLine();

          return $"Compensation entitlement: {compensation:C2} " +
                 $"(rule: <3h = nil, 3-5h = 25%, 5h+ = 50% of ticket price)";
      },
      "calculate_compensation",
      "Calculates the passenger compensation entitlement based on delay duration " +
      "and ticket price using the standard airline disruption policy.");
  ```

  The `[Description]` attributes guide the model when it selects argument values. The yellow `[Tool]` lines make the invocation visible in the terminal.

### Part 2 - Attach the tool and run the agent

#### 3. Create the agent with the tool (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
  var credential = new AzureCliCredential();
  var client = new AIProjectClient(new Uri(endpoint), credential);
  var agent = client
      .AsAIAgent(
          model: model,
          instructions:
              "You are the Trip Disruption Concierge. When a passenger asks " +
              "about compensation, always call the calculate_compensation tool " +
              "with the actual delay hours and ticket price before answering. " +
              "State the calculated amount clearly in your response.",
          tools: [calculateCompensation]);
  ```

#### 4. Run a prompt that triggers the tool (TODO 3)

- [ ] Locate `// ── TODO 3` and replace the commented-out block with the prompt code already commented out there.

  > [!NOTE]
  > The commented-out prompt already includes an explicit delay duration (`3 hours`) and ticket price (`AUD 420`) so the model can extract the exact values to pass to `calculate_compensation`.

#### 5. Run the starter

- [ ] In a terminal, run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/04-function-tools/src/TripConcierge.FunctionTools.csproj
  ```

## Validation

- The terminal shows a yellow `[Tool] → calculate_compensation(...)` line.
- The `[Tool] ←` line shows the calculated compensation value.
- The final `[Agent]` response quotes the calculated amount.

> [!NOTE]
> The solution project runs a second turn (`AUD 650, 6-hour delay`) to demonstrate the tool being called again with different values. The completed starter produces only the single turn above.

## Congratulations 🎉

You gave your agent a local C# function it can call autonomously. The model decided when the tool was needed, extracted the right arguments, and incorporated the result into its final response - all without any manual orchestration in your code. To see tools work alongside streaming output, swap `RunAsync` for `RunStreamingAsync` - the framework invokes your function at the right moment in the stream.

> [!TIP]
> **Next up → [Module 05: MCP Tools](../05-mcp-tools/README.md)**
> Replace the local function tool with a remote MCP server. The agent calls live flight-status and rebooking tools over the network.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `[Tool]` lines never appear | Rephrase the prompt to explicitly mention delay hours and ticket price |
| Tool returns unexpected value | Check the compensation tier logic in the function body |
| Build error: `AIFunctionFactory` not found | Add `using Microsoft.Extensions.AI;` - it is pulled in transitively |
| `NotImplementedException` | A TODO is still incomplete |
| `AuthenticationFailedException` | Run `az login` or confirm your Entra account has the Foundry User role on the project |
