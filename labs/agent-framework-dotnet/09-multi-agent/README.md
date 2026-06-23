# 09. Multi-agent Orchestration

**Estimated time:** 25 minutes

![Microsoft Agent Framework multi-agent architecture diagram: an orchestrating agent receives a user request and delegates to specialist agents. Each specialist agent has its own instructions, tools, and knowledge, and returns a result to the orchestrator, which composes the final response.](../../../docs/assets/diagrams/agent-framework-agent-systems.png)

> [!IMPORTANT]
> This module builds on [Module 02](../02-first-agent/README.md). You should be comfortable creating `AIAgent` instances before continuing.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Create specialist agents as discrete `AIAgent` instances.
- Register specialists as skills on the orchestrating concierge with `.WithAgentSkill()`.
- Observe the concierge routing to the correct specialist for each query.
- See the `[Agent →]` delegation lines in the terminal showing the routing decisions.

## Concepts

### Multi-agent orchestration

A single agent with broad instructions often produces inconsistent results. The **multi-agent pattern** solves this by splitting responsibility: an **orchestrator** focuses only on understanding the user's intent and routing, while **specialist agents** focus only on their specific domain.

This improves quality because each agent's instructions are shorter and more focused, and reduces the risk of one concern interfering with another.

### WithAgentSkill

`.WithAgentSkill()` registers an `AIAgent` as a callable skill on the orchestrator. The orchestrator treats the skill like a tool: it calls it with a natural-language description of the task, receives a response, and incorporates the result into its own reply:

```csharp
var concierge = client
    .AsAIAgent(model: model, instructions: "...")
    .WithAgentSkill(
        rebookingSpecialist,
        "RebookFlight",
        "Find alternative flight options for a disrupted passenger.");
```

When the concierge's instructions tell it to call `RebookFlight`, the framework routes the request to `rebookingSpecialist` and returns the result.

## Steps

### Part 1 — Create the specialist agents

#### 1. Open the starter file

- [ ] Open `src/Program.cs` in the editor.

#### 2. Create the three specialist agents (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  var rebookingSpecialist = client.AsAIAgent(
      model: model,
      instructions:
          "You are the Rebooking Specialist. Your only role is to find " +
          "alternative flight options for disrupted passengers. " +
          "Always list specific flight numbers, times, and seat availability. " +
          "Be direct and practical.");

  var accommodationSpecialist = client.AsAIAgent(
      model: model,
      instructions:
          "You are the Accommodation Specialist. Your only role is to help " +
          "stranded passengers find hotel accommodation near the airport. " +
          "Suggest two or three specific options with estimated cost.");

  var compensationSpecialist = client.AsAIAgent(
      model: model,
      instructions:
          "You are the Compensation Specialist. Your only role is to explain " +
          "and calculate passenger compensation entitlements under airline " +
          "disruption policies. Provide clear figures and next steps.");

  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Loop] Specialist agents created: rebooking, accommodation, compensation");
  Console.ResetColor();
  Console.WriteLine();
  ```

### Part 2 — Build the orchestrating concierge

#### 3. Create the concierge with agent skills (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
  var concierge = client
      .AsAIAgent(
          model: model,
          instructions:
              "You are the Trip Disruption Concierge. You coordinate with " +
              "specialist agents to help passengers. For flight rebooking, " +
              "always call RebookFlight. For hotel accommodation, call FindHotel. " +
              "For compensation questions, call CalculateCompensation. " +
              "Never answer these topics yourself — always delegate to the " +
              "appropriate specialist.")
      .WithAgentSkill(
          rebookingSpecialist,
          "RebookFlight",
          "Find alternative flight options for a disrupted passenger.")
      .WithAgentSkill(
          accommodationSpecialist,
          "FindHotel",
          "Find hotel accommodation options near the airport for a stranded passenger.")
      .WithAgentSkill(
          compensationSpecialist,
          "CalculateCompensation",
          "Explain and calculate the passenger's compensation entitlement.");

  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Loop] Concierge created with 3 specialist skills.");
  Console.ResetColor();
  Console.WriteLine();
  ```

#### 4. Run queries that exercise all three specialists (TODO 3)

- [ ] Locate `// ── TODO 3` and replace the commented-out block with the three queries already commented out there.

  > [!NOTE]
  > The third query should be phrased to require multiple specialists in a single turn. Watch for multiple `[Agent →]` delegation lines in the terminal output.

### Part 3 — Run and verify

#### 5. Run the starter

- [ ] In a terminal, run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/09-multi-agent/src/TripConcierge.MultiAgent.csproj
  ```

## Validation

- Each specialist agent logs its name when activated (yellow `[Specialist]` lines).
- The concierge routes each query to a different specialist.
- Query 3 triggers multiple specialists within a single turn.

## Congratulations 🎉

You built a multi-agent system where a concierge orchestrates three specialist agents. Each specialist stays focused on its domain while the concierge handles routing — producing more consistent, higher-quality responses than a single broad-purpose agent would.

> [!TIP]
> **Next up → [Module 10: Hosted Agents](../10-hosted-agents/README.md)**
> Package the Trip Disruption Concierge as an ASP.NET Core web service that exposes the standard Foundry Responses API endpoint.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Concierge answers without calling specialists | Strengthen the routing instructions in the concierge system prompt |
| `WithAgentSkill` not found | Confirm `Microsoft.Agents.AI.Foundry` prerelease package is restored |
| `NotImplementedException` | A TODO is still incomplete |
