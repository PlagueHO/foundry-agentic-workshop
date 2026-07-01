using System.Diagnostics;
using A2A;
using Azure.Identity;
using Azure.AI.Projects;
using DotNetEnv;
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Foundry;

Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var model = Environment.GetEnvironmentVariable("AGENT_MODEL") ?? "chat";
var a2aServerUrl = Environment.GetEnvironmentVariable("A2A_SERVER_URL") ?? "http://localhost:5000";

Console.WriteLine("=== Trip Disruption Concierge - Module 15: Agent-to-Agent (A2A) ===");
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"  Model         : {model}");
Console.WriteLine($"  A2A server    : {a2aServerUrl}");
Console.ResetColor();
Console.WriteLine();

var credential = new DefaultAzureCredential();
var client = new AIProjectClient(new Uri(endpoint), credential);

// ── Discover the remote Compensation Specialist over A2A ──────────────────────
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Resolving remote Compensation Specialist agent card...");
Console.ResetColor();

var resolver = new A2ACardResolver(new Uri(a2aServerUrl));
AIAgent compensationSpecialist = await resolver.GetAIAgentAsync();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Resolved remote Compensation Specialist via A2A agent card.");
Console.ResetColor();
Console.WriteLine();

// ── Create the concierge and attach the remote specialist as a skill ─────────
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Creating Trip Disruption Concierge with remote specialist skill...");
Console.ResetColor();

var concierge = client
    .AsAIAgent(
        model: model,
        instructions:
            "You are the Trip Disruption Concierge. For all compensation " +
            "and refund queries, use the compensation specialist tool - " +
            "never calculate compensation yourself. You may provide a " +
            "brief introduction or closing summary.",
        tools: [compensationSpecialist.AsAIFunction()]);

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Concierge ready - 1 remote specialist exposed as a function tool.");
Console.ResetColor();
Console.WriteLine();

// ── Run a query that must be delegated across the network ────────────────────
var query =
    "I was given only 3 hours' notice and my ticket cost AUD 420. " +
    "How much compensation can I claim, and how do I file it?";

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine($"[User] {query}");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] RunAsync - concierge will delegate over A2A to the remote specialist...");
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

Console.WriteLine("Module 15 complete. \u2713");
