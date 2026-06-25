using Azure.Identity;
using Azure.AI.Projects;
using DotNetEnv;
using Microsoft.Agents.AI.Foundry;

Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var model = Environment.GetEnvironmentVariable("AGENT_MODEL") ?? "chat";

Console.WriteLine("=== Trip Disruption Concierge - Module 03: Multi-turn & Threads ===");
Console.WriteLine();

// ── TODO 1 ───────────────────────────────────────────────────────────────────
// Create the AIProjectClient and AIAgent (same pattern as Module 02).
//
// var credential = new AzureCliCredential();
// var client = new AIProjectClient(new Uri(endpoint), credential);
// var agent = client.AsAIAgent(
//     model: model,
//     instructions:
//         "You are the Trip Disruption Concierge. Help passengers with flight " +
//         "disruptions. Remember everything from earlier in the conversation - " +
//         "the passenger must not need to repeat information they have already " +
//         "provided.");
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 2 ───────────────────────────────────────────────────────────────────
// Create an AgentSession. Sessions persist conversation history across turns.
//
// var session = await agent.CreateSessionAsync();
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Loop] Session ready.");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 3 ───────────────────────────────────────────────────────────────────
// Run Turn 1. Pass session: as a named argument so the framework stores context.
//
// var turn1 = "My name is Emma. My flight AU123 AKL→SYD was just cancelled. " +
//             "I have a separate connecting flight SYD→MEL. What should I do first?";
//
// Console.ForegroundColor = ConsoleColor.Cyan;
// Console.WriteLine($"[User] {turn1}");
// Console.ResetColor();
// Console.WriteLine();
//
// var result1 = await agent.RunAsync(turn1, session: session);
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {result1.Text}");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 4 ───────────────────────────────────────────────────────────────────
// Run Turn 2 and Turn 3 with the same session.
// Notice: you do NOT need to repeat Emma's name or the flight number.
//
// var turn2 = "The airline is offering a rebooking on tomorrow's flight. " +
//             "But I will miss my connecting flight. What are my options?";
//
// Console.ForegroundColor = ConsoleColor.Cyan;
// Console.WriteLine($"[User] {turn2}");
// Console.ResetColor();
// Console.WriteLine();
//
// var result2 = await agent.RunAsync(turn2, session: session);
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {result2.Text}");
// Console.ResetColor();
// Console.WriteLine();
//
// var turn3 = "Given everything we have discussed, what is the single best " +
//             "outcome I can realistically push for with the airline?";
//
// Console.ForegroundColor = ConsoleColor.Cyan;
// Console.WriteLine($"[User] {turn3}");
// Console.ResetColor();
// Console.WriteLine();
//
// var result3 = await agent.RunAsync(turn3, session: session);
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {result3.Text}");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

throw new NotImplementedException(
    "Complete the TODOs above, then remove this line and the throw statement.");
