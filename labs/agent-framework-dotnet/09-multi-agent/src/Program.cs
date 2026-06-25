using Azure.Identity;
using Azure.AI.Projects;
using DotNetEnv;
using Microsoft.Agents.AI.Foundry;

Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var model = Environment.GetEnvironmentVariable("AGENT_MODEL") ?? "chat";

Console.WriteLine("=== Trip Disruption Concierge — Module 09: Multi-agent Orchestration ===");
Console.WriteLine();

var credential = new AzureCliCredential();
var client = new AIProjectClient(new Uri(endpoint), credential);

// ── TODO 1 ───────────────────────────────────────────────────────────────────
// Create three specialist agents — each an AIAgent with focused instructions.
//
// var rebookingSpecialist = client.AsAIAgent(
//     model: model,
//     instructions:
//         "You are the Rebooking Specialist. Your only role is to find " +
//         "alternative flight options for disrupted passengers. " +
//         "Always list specific flight numbers, times, and seat availability. " +
//         "Be direct and practical.");
//
// var accommodationSpecialist = client.AsAIAgent(
//     model: model,
//     instructions:
//         "You are the Accommodation Specialist. Your only role is to help " +
//         "stranded passengers find hotel accommodation near the airport. " +
//         "Suggest two or three specific options with estimated cost.");
//
// var compensationSpecialist = client.AsAIAgent(
//     model: model,
//     instructions:
//         "You are the Compensation Specialist. Your only role is to explain " +
//         "and calculate passenger compensation entitlements under airline " +
//         "disruption policies. Provide clear figures and next steps.");
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Loop] Specialist agents created: rebooking, accommodation, compensation");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 2 ───────────────────────────────────────────────────────────────────
// Create the orchestrating concierge and attach specialists as skills using
// .WithAgentSkill(). The concierge will route queries to the right specialist.
//
// var concierge = client
//     .AsAIAgent(
//         model: model,
//         instructions:
//             "You are the Trip Disruption Concierge. You coordinate with " +
//             "specialist agents to help passengers. For flight rebooking, " +
//             "always call RebookFlight. For hotel accommodation, call FindHotel. " +
//             "For compensation questions, call CalculateCompensation. " +
//             "Never answer these topics yourself — always delegate to the " +
//             "appropriate specialist.")
//     .WithAgentSkill(
//         rebookingSpecialist,
//         "RebookFlight",
//         "Find alternative flight options for a disrupted passenger.")
//     .WithAgentSkill(
//         accommodationSpecialist,
//         "FindHotel",
//         "Find hotel accommodation options near the airport for a stranded passenger.")
//     .WithAgentSkill(
//         compensationSpecialist,
//         "CalculateCompensation",
//         "Explain and calculate the passenger's compensation entitlement.");
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Loop] Concierge created with 3 specialist skills.");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 3 ───────────────────────────────────────────────────────────────────
// Run three queries that route to different specialists.
// Watch the [Loop] output to see which specialist is invoked each time.
//
// var q1 = "My flight AU123 AKL→SYD was cancelled. What flights can I get today?";
// var q2 = "I am stranded at Auckland airport overnight. What hotels are nearby?";
// var q3 = "I was given only 3 hours' notice and my ticket cost AUD 420. " +
//           "How much compensation can I claim, and how do I file it?";
//
// foreach (var query in new[] { q1, q2, q3 })
// {
//     Console.ForegroundColor = ConsoleColor.Cyan;
//     Console.WriteLine($"[User] {query}");
//     Console.ResetColor();
//     Console.WriteLine();
//
//     Console.ForegroundColor = ConsoleColor.DarkGray;
//     Console.WriteLine("[Loop] RunAsync — concierge will delegate to a specialist...");
//     Console.ResetColor();
//     Console.WriteLine();
//
//     var result = await concierge.RunAsync(query);
//
//     Console.ForegroundColor = ConsoleColor.Green;
//     Console.WriteLine($"[Agent] {result.Text}");
//     Console.ResetColor();
//     Console.WriteLine();
//     Console.WriteLine(new string('─', 72));
//     Console.WriteLine();
// }
//
// ─────────────────────────────────────────────────────────────────────────────

throw new NotImplementedException(
    "Complete the TODOs above, then remove this line and the throw statement.");
