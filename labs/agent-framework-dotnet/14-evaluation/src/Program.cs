using System.ComponentModel;
using Azure.Identity;
using Azure.AI.Projects;
using DotNetEnv;
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Foundry;
using Microsoft.Extensions.AI;

Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var model = Environment.GetEnvironmentVariable("AGENT_MODEL") ?? "chat";

Console.WriteLine("=== Trip Disruption Concierge - Module 14: Evaluation & Quality ===");
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"  Model : {model}");
Console.ResetColor();
Console.WriteLine();

var credential = new DefaultAzureCredential();
var projectClient = new AIProjectClient(new Uri(endpoint), credential);

var calculateCompensation = AIFunctionFactory.Create(
    (
        [Description("Hours of delay, or hours of notice given before cancellation")]
        int delayOrNoticeHours,
        [Description("Original one-way ticket price in Australian dollars")]
        decimal ticketPriceAud
    ) =>
    {
        decimal compensation = delayOrNoticeHours switch
        {
            < 3 => 0m,
            < 5 => ticketPriceAud * 0.25m,
            _ => ticketPriceAud * 0.50m,
        };

        return $"Compensation entitlement: {compensation:C2} " +
               $"(rule: <3h = nil, 3\u20135h = 25%, 5h+ = 50% of ticket price)";
    },
    "calculate_compensation",
    "Calculates the passenger compensation entitlement based on delay duration " +
    "and ticket price using the standard airline disruption policy.");

var queries = new[]
{
    "My flight AU123 AKL\u2192SYD was cancelled with only 3 hours' notice. My ticket cost AUD 420. How much compensation am I entitled to?",
    "What if my ticket had cost AUD 650 and the delay was 6 hours?",
};

// ── TODO 1 ───────────────────────────────────────────────────────────────────
// Create the Trip Disruption Concierge agent with the compensation tool
// attached, matching the Module 04 pattern.
//
// var agent = projectClient.AsAIAgent(
//     model: model,
//     instructions:
//         "You are the Trip Disruption Concierge. When a passenger asks " +
//         "about compensation, always call the calculate_compensation tool " +
//         "with the actual delay hours and ticket price before answering. " +
//         "State the calculated amount clearly in your response.",
//     tools: [calculateCompensation]);
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Loop] Agent created with compensation tool attached.");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 2 ───────────────────────────────────────────────────────────────────
// Build a LocalEvaluator with three checks: the response must mention
// "compensation", the agent must have called calculate_compensation, and a
// custom function check confirms the reply stays concise.
//
// var localEvaluator = new LocalEvaluator(
//     EvalChecks.KeywordCheck("compensation"),
//     EvalChecks.ToolCalledCheck("calculate_compensation"),
//     FunctionEvaluator.Create("is_concise",
//         (string response) => response.Split(' ').Length < 200));
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Loop] Local evaluator ready: keyword + tool + conciseness checks.");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 3 ───────────────────────────────────────────────────────────────────
// Run the agent against the test queries and score the responses locally.
// EvaluateAsync runs the agent once per query, then applies every check.
//
// AgentEvaluationResults localResults = await agent.EvaluateAsync(queries, localEvaluator);
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Eval] Local: {localResults.Passed}/{localResults.Total} passed");
// Console.ResetColor();
//
// foreach (var item in localResults.Items)
// {
//     foreach (var metric in item.Metrics)
//     {
//         Console.WriteLine($"  {metric.Key}: {metric.Value}");
//     }
// }
//
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 4 ───────────────────────────────────────────────────────────────────
// Build a FoundryEvals instance for cloud-based LLM-as-judge scoring. This
// calls the Foundry Evals service using the same model deployment as the judge.
//
// var foundryEvaluator = new FoundryEvals(
//     projectClient,
//     model,
//     FoundryEvals.Relevance,
//     FoundryEvals.Coherence,
//     FoundryEvals.TaskAdherence);
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Loop] Foundry evaluator ready: relevance + coherence + task adherence.");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 5 ───────────────────────────────────────────────────────────────────
// Run the same queries through the Foundry cloud evaluators and print the
// portal report link alongside the pass/fail summary.
//
// AgentEvaluationResults foundryResults = await agent.EvaluateAsync(queries, foundryEvaluator);
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Eval] Foundry: {foundryResults.Passed}/{foundryResults.Total} passed");
// Console.ResetColor();
//
// if (foundryResults.ReportUrl is not null)
// {
//     Console.WriteLine($"[Eval] Report: {foundryResults.ReportUrl}");
// }
//
// foundryResults.AssertAllPassed();
//
// ─────────────────────────────────────────────────────────────────────────────

throw new NotImplementedException(
    "Complete the TODOs above, then remove this line and the throw statement.");
