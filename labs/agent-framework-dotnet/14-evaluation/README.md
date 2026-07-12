---
title: '14. Evaluation & Quality'
description: 'Complete this lab to evaluation & quality.'
lastUpdated: '2026-07-13'
track: 'agent-framework-dotnet'
module: 14
slug: '14-evaluation'
estimatedTimeMinutes: 25
difficulty: 'advanced'
prerequisites: ['Module 13']
audience:
  - 'attendee'
technologies:
  - 'Microsoft Agent Framework'
  - 'Microsoft Foundry'
tags:
  - 'agent-framework'
  - 'evaluation'
  - 'and'
  - 'quality'
status: 'active'
contentType: 'lab'
---
# 14. Evaluation & Quality

**Estimated time:** 25 minutes

![Microsoft Agent Framework overview: an open-source engine for building and orchestrating AI agents, summarised in five pillars - Unified SDK (AIAgent, AgentThread, and AgentTool primitives built on Microsoft.Extensions.AI), Local-first and cloud-agnostic (run agents locally then move the same code to Foundry Agent Service or any cloud containers), Multi-agent orchestration (sequential, concurrent, handoff, group chat, magentic, and workflow patterns), Tools and extensibility (out-of-the-box integrations plus functions, APIs, and MCP servers as tools), and Enterprise-grade foundations (approval flows, content-policy hooks, OpenTelemetry observability, and long-running execution).](../../../docs/assets/diagrams/agent-framework-introduction.png)

> [!IMPORTANT]
> This module builds on [Module 04](../04-function-tools/README.md). The compensation tool from Module 04 is reused here so both the keyword check and the tool-call check have something meaningful to verify.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Build a `LocalEvaluator` from built-in `EvalChecks` and a custom `FunctionEvaluator`.
- Run an agent against test queries and score the responses with `EvaluateAsync`.
- Build a `FoundryEvals` instance for cloud-based, LLM-as-judge scoring.
- Read pass/fail summaries, per-item metrics, and the Foundry portal report link.

## Concepts

### The evaluation framework

The Microsoft Agent Framework ships a built-in evaluation framework on top of [Microsoft.Extensions.AI.Evaluation](https://learn.microsoft.com/dotnet/api/microsoft.extensions.ai.evaluation). It is built around three types:

| Type | Purpose |
|---|---|
| `EvalItem` | A single item to evaluate - wraps the conversation and derives query/response. |
| `Evaluator` | A provider that scores items - local checks, Azure AI Foundry, or a custom implementation. |
| `EvalResults` | Aggregated results - pass/fail counts, per-item detail, and an optional portal link. |

`EvaluateAsync` is an extension method on `AIAgent`. It runs the agent once per query, converts each interaction into an `EvalItem`, and passes the batch to the evaluator you supply.

### Local evaluators

A `LocalEvaluator` runs checks entirely offline - no API calls, no cost, fast enough for CI. It accepts any number of check functions:

```csharp
var localEvaluator = new LocalEvaluator(
    EvalChecks.KeywordCheck("compensation"),
    EvalChecks.ToolCalledCheck("calculate_compensation"),
    FunctionEvaluator.Create("is_concise",
        (string response) => response.Split(' ').Length < 200));
```

`EvalChecks.KeywordCheck` confirms the response mentions specific terms. `EvalChecks.ToolCalledCheck` confirms the agent actually invoked a named tool rather than guessing the answer. `FunctionEvaluator.Create` wraps any function you write as a custom check.

### Foundry cloud evaluators

`FoundryEvals` connects to the Azure AI Foundry evaluation service for LLM-as-judge scoring. Results are viewable in the Foundry portal with dashboards and comparison views:

```csharp
var foundryEvaluator = new FoundryEvals(
    projectClient,
    model,
    FoundryEvals.Relevance,
    FoundryEvals.Coherence,
    FoundryEvals.TaskAdherence);
```

`FoundryEvals` requires a Foundry project with a model deployment - the `model` parameter is the judge model. It provides constants for every built-in evaluator: agent behaviour (`TaskAdherence`, `TaskCompletion`, `IntentResolution`), tool usage (`ToolCallAccuracy`, `ToolSelection`), quality (`Coherence`, `Fluency`, `Relevance`, `Groundedness`), and safety (`Violence`, `SelfHarm`, `HateUnfairness`).

### Reading results

Both evaluator types return an `AgentEvaluationResults`:

```csharp
AgentEvaluationResults results = await agent.EvaluateAsync(queries, evaluator);

Console.WriteLine($"{results.Passed}/{results.Total} passed");
if (results.ReportUrl is not null)
{
    Console.WriteLine($"Report: {results.ReportUrl}");
}

results.AssertAllPassed();  // Throws if any item failed - useful in CI
```

## Steps

### Part 1 - Complete the starter code

#### 1. Open the starter file

- [ ] Open `src/Program.cs` in the editor.

#### 2. Create the agent under test (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  var agent = projectClient.AsAIAgent(
      model: model,
      instructions:
          "You are the Trip Disruption Concierge. When a passenger asks " +
          "about compensation, always call the calculate_compensation tool " +
          "with the actual delay hours and ticket price before answering. " +
          "State the calculated amount clearly in your response.",
      tools: [calculateCompensation]);
  ```

#### 3. Build the local evaluator (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
  var localEvaluator = new LocalEvaluator(
      EvalChecks.KeywordCheck("compensation"),
      EvalChecks.ToolCalledCheck("calculate_compensation"),
      FunctionEvaluator.Create("is_concise",
          (string response) => response.Split(' ').Length < 200));
  ```

#### 4. Run the local evaluation (TODO 3)

- [ ] Locate `// ── TODO 3` and replace the commented-out block with:

  ```csharp
  AgentEvaluationResults localResults = await agent.EvaluateAsync(queries, localEvaluator);

  Console.ForegroundColor = ConsoleColor.Green;
  Console.WriteLine($"[Eval] Local: {localResults.Passed}/{localResults.Total} passed");
  Console.ResetColor();

  foreach (var item in localResults.Items)
  {
      foreach (var metric in item.Metrics)
      {
          Console.WriteLine($"  {metric.Key}: {metric.Value}");
      }
  }
  ```

#### 5. Build the Foundry evaluator (TODO 4)

- [ ] Locate `// ── TODO 4` and replace the commented-out block with:

  ```csharp
  var foundryEvaluator = new FoundryEvals(
      projectClient,
      model,
      FoundryEvals.Relevance,
      FoundryEvals.Coherence,
      FoundryEvals.TaskAdherence);
  ```

#### 6. Run the Foundry evaluation (TODO 5)

- [ ] Locate `// ── TODO 5` and replace the commented-out block with:

  ```csharp
  AgentEvaluationResults foundryResults = await agent.EvaluateAsync(queries, foundryEvaluator);

  Console.ForegroundColor = ConsoleColor.Green;
  Console.WriteLine($"[Eval] Foundry: {foundryResults.Passed}/{foundryResults.Total} passed");
  Console.ResetColor();

  if (foundryResults.ReportUrl is not null)
  {
      Console.WriteLine($"[Eval] Report: {foundryResults.ReportUrl}");
  }

  foundryResults.AssertAllPassed();
  ```

### Part 2 - Run and verify

#### 7. Run the starter

- [ ] In a terminal, run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/14-evaluation/src/TripConcierge.Evaluation.csproj
  ```

#### 8. Inspect the results

- [ ] Confirm the console prints `[Eval] Local: 2/2 passed` (or close to it - LLM responses vary slightly between runs).
- [ ] Confirm the console prints `[Eval] Foundry: 2/2 passed` followed by a report URL.
- [ ] Open the report URL and review the per-query relevance, coherence, and task adherence scores in the Foundry portal.

## Validation

- The local evaluator prints per-item metrics for the keyword, tool-call, and conciseness checks.
- The Foundry evaluator prints a pass/fail summary and a portal report URL.
- No unhandled exception is thrown - `AssertAllPassed()` only throws if a check genuinely fails.

## Congratulations 🎉

You built both an offline `LocalEvaluator` and a cloud-based `FoundryEvals` pipeline for the Trip Disruption Concierge, scoring the same agent for keyword presence, correct tool usage, conciseness, relevance, coherence, and task adherence. This is the same evaluation pattern you would wire into CI to catch regressions before they reach production.

> [!TIP]
> **Next up → [Module 15: Agent-to-Agent (A2A)](../15-agent-to-agent/README.md)**
> Expose a specialist agent over the network and consume it as a remote A2A agent.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `FOUNDRY_PROJECT_ENDPOINT is not set` | Copy `shared/.env.example` to `.env` in the repository root and fill in your values |
| Foundry evaluator throws an authentication error | Run `az login` and confirm your account has access to the Foundry project |
| `AssertAllPassed` throws | Inspect `results.Items[i].Metrics` to see which check failed and why |
| Local evaluator conciseness check fails intermittently | Model responses vary in length between runs - this is expected LLM non-determinism |
| `NotImplementedException` | A TODO is still incomplete |
