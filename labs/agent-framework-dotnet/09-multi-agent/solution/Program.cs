using System.Diagnostics;
using Azure.Identity;
using Azure.AI.Projects;
using DotNetEnv;
using Microsoft.Agents.AI.Foundry;

Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var model = Environment.GetEnvironmentVariable("AGENT_MODEL") ?? "chat";

Console.WriteLine("=== Trip Disruption Concierge - Module 09: Multi-agent Orchestration ===");
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"  Model : {model}");
Console.ResetColor();
Console.WriteLine();

var credential = new AzureCliCredential();
var client = new AIProjectClient(new Uri(endpoint), credential);

// ── Create specialist agents ──────────────────────────────────────────────────
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Creating specialist agents...");
Console.ResetColor();

var rebookingSpecialist = client.AsAIAgent(
    model: model,
    instructions:
        "You are the Rebooking Specialist. Your sole focus is finding " +
        "alternative flight options for disrupted passengers. " +
        "Always list specific flight numbers, times, and seat availability. " +
        "Be direct and practical. Do not discuss hotels or compensation.");

var accommodationSpecialist = client.AsAIAgent(
    model: model,
    instructions:
        "You are the Accommodation Specialist. Your sole focus is helping " +
        "stranded passengers find hotel accommodation near the relevant airport. " +
        "Suggest two or three specific options with estimated cost per night. " +
        "Do not discuss flights or compensation.");

var compensationSpecialist = client.AsAIAgent(
    model: model,
    instructions:
        "You are the Compensation Specialist. Your sole focus is explaining " +
        "and calculating passenger compensation entitlements under airline " +
        "disruption policies. Provide clear figures and actionable next steps. " +
        "Do not discuss rebooking or hotels.");

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Specialists ready: rebooking, accommodation, compensation.");
Console.ResetColor();
Console.WriteLine();

// ── Create orchestrating concierge with specialist skills ─────────────────────
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Creating Trip Disruption Concierge with specialist skills...");
Console.ResetColor();

var concierge = client
    .AsAIAgent(
        model: model,
        instructions:
            "You are the Trip Disruption Concierge. You coordinate with " +
            "specialist agents to help passengers. " +
            "For all flight rebooking queries: delegate to RebookFlight. " +
            "For all hotel and accommodation queries: delegate to FindHotel. " +
            "For all compensation and refund queries: delegate to CalculateCompensation. " +
            "Never answer these specialist topics yourself - always delegate. " +
            "You may provide a brief introduction or closing summary.")
    .WithAgentSkill(
        rebookingSpecialist,
        "RebookFlight",
        "Find alternative flight options for a disrupted passenger.")
    .WithAgentSkill(
        accommodationSpecialist,
        "FindHotel",
        "Find hotel accommodation near the airport for a stranded passenger.")
    .WithAgentSkill(
        compensationSpecialist,
        "CalculateCompensation",
        "Explain and calculate the passenger's compensation entitlement.");

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Concierge ready - 3 specialist skills registered.");
Console.ResetColor();
Console.WriteLine();

// ── Run queries - each routes to a different specialist ───────────────────────
var queries = new[]
{
    "My flight AU123 AKL→SYD was cancelled. What flights can I get today?",
    "I am stranded at Auckland Airport overnight. What hotels are nearby?",
    "I was given only 3 hours' notice and my ticket cost AUD 420. " +
        "How much compensation can I claim, and how do I file it?",
};

int queryNumber = 0;

foreach (var query in queries)
{
    queryNumber++;
    Console.WriteLine($"─── Query {queryNumber} {'─',68}");
    Console.WriteLine();

    Console.ForegroundColor = ConsoleColor.Cyan;
    Console.WriteLine($"[User] {query}");
    Console.ResetColor();
    Console.WriteLine();

    Console.ForegroundColor = ConsoleColor.DarkGray;
    Console.WriteLine("[Loop] RunAsync - concierge will select and delegate to a specialist...");
    Console.ResetColor();
    Console.WriteLine();

    var sw = Stopwatch.StartNew();
    var result = await concierge.RunAsync(query);
    sw.Stop();

    Console.ForegroundColor = ConsoleColor.DarkGray;
    Console.WriteLine($"[Loop] RunAsync complete ({sw.ElapsedMilliseconds} ms)");
    Console.ResetColor();
    Console.WriteLine();

    Console.ForegroundColor = ConsoleColor.Green;
    Console.WriteLine($"[Agent] {result.Text}");
    Console.ResetColor();
    Console.WriteLine();
}

Console.WriteLine("Module 09 complete. ✓");
