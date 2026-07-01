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

// ── TODO 1 ───────────────────────────────────────────────────────────────────
// Discover the remote Compensation Specialist over A2A. The resolver fetches
// the agent card from the well-known path and wraps the endpoint as a
// standard AIAgent - the concierge cannot tell it apart from a local agent.
//
// var resolver = new A2ACardResolver(new Uri(a2aServerUrl));
// AIAgent compensationSpecialist = await resolver.GetAIAgentAsync();
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Loop] Resolved remote Compensation Specialist via A2A agent card.");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 2 ───────────────────────────────────────────────────────────────────
// Create the concierge and expose the remote specialist as a function tool -
// AsAIFunction() wraps any AIAgent (local or remote) as a callable AIFunction,
// so the concierge invokes it exactly like a local function tool.
//
// var concierge = client
//     .AsAIAgent(
//         model: model,
//         instructions:
//             "You are the Trip Disruption Concierge. For all compensation " +
//             "and refund queries, use the compensation specialist tool - " +
//             "never calculate compensation yourself. You may provide a " +
//             "brief introduction or closing summary.",
//         tools: [compensationSpecialist.AsAIFunction()]);
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Loop] Concierge ready - 1 remote specialist exposed as a function tool.");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 3 ───────────────────────────────────────────────────────────────────
// Run a query that must be delegated across the network to the remote agent.
//
// var query =
//     "I was given only 3 hours' notice and my ticket cost AUD 420. " +
//     "How much compensation can I claim, and how do I file it?";
//
// Console.ForegroundColor = ConsoleColor.Cyan;
// Console.WriteLine($"[User] {query}");
// Console.ResetColor();
// Console.WriteLine();
//
// var result = await concierge.RunAsync(query);
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {result.Text}");
// Console.ResetColor();
//
// ─────────────────────────────────────────────────────────────────────────────

throw new NotImplementedException(
    "Complete the TODOs above, then remove this line and the throw statement.");
