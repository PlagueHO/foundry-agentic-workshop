using System.ComponentModel;
using Azure.Identity;
using Azure.AI.Projects;
using DotNetEnv;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;

Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var model = Environment.GetEnvironmentVariable("AGENT_MODEL") ?? "chat";

Console.WriteLine("=== Trip Disruption Concierge - Module 04: Function Tools ===");
Console.WriteLine();

// ── TODO 1 ───────────────────────────────────────────────────────────────────
// Create a function tool using AIFunctionFactory.Create().
// The lambda must print a [Tool] line before and after it executes so the
// audience can see the agent invoking local code.
//
// var calculateCompensation = AIFunctionFactory.Create(
//     (
//         [Description("Hours of delay, or hours of notice given before cancellation")]
//         int delayOrNoticeHours,
//         [Description("Original one-way ticket price in Australian dollars")]
//         decimal ticketPriceAud
//     ) =>
//     {
//         Console.ForegroundColor = ConsoleColor.Yellow;
//         Console.WriteLine(
//             $"[Tool] → calculate_compensation(" +
//             $"delayHours={delayOrNoticeHours}, ticketPrice={ticketPriceAud:C2})");
//         Console.ResetColor();
//
//         decimal compensation = delayOrNoticeHours switch
//         {
//             < 3 => 0m,
//             < 5 => ticketPriceAud * 0.25m,
//             _ => ticketPriceAud * 0.50m,
//         };
//
//         Console.ForegroundColor = ConsoleColor.Yellow;
//         Console.WriteLine($"[Tool] ← compensation = {compensation:C2}");
//         Console.ResetColor();
//         Console.WriteLine();
//
//         return $"Compensation entitlement: {compensation:C2} " +
//                $"(rule: <3h = nil, 3–5h = 25%, 5h+ = 50% of ticket price)";
//     },
//     "calculate_compensation",
//     "Calculates the passenger compensation entitlement based on delay duration " +
//     "and ticket price using the standard airline disruption policy.");
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 2 ───────────────────────────────────────────────────────────────────
// Create the AIAgent and pass the function tool via the tools: parameter.
//
// var credential = new AzureCliCredential();
// var client = new AIProjectClient(new Uri(endpoint), credential);
// var agent = client
//     .AsAIAgent(
//         model: model,
//         instructions:
//             "You are the Trip Disruption Concierge. When a passenger asks " +
//             "about compensation, always call the calculate_compensation tool " +
//             "with the actual delay hours and ticket price before answering. " +
//             "State the calculated amount clearly in your response.",
//         tools: [calculateCompensation]);
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 3 ───────────────────────────────────────────────────────────────────
// Run a prompt that should trigger the tool. The agent will call
// calculate_compensation automatically - watch for the [Tool] log lines.
//
// var query =
//     "My flight AU123 AKL→SYD was cancelled with only 3 hours' notice. " +
//     "My ticket cost AUD 420. How much compensation am I entitled to?";
//
// Console.ForegroundColor = ConsoleColor.Cyan;
// Console.WriteLine($"[User] {query}");
// Console.ResetColor();
// Console.WriteLine();
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Loop] RunAsync - agent may call tools before responding...");
// Console.ResetColor();
// Console.WriteLine();
//
// var result = await agent.RunAsync(query);
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {result.Text}");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

throw new NotImplementedException(
    "Complete the TODOs above, then remove this line and the throw statement.");
