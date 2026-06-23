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

Console.WriteLine("=== Trip Disruption Concierge — Module 03: Multi-turn & Threads ===");
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"  Model : {model}");
Console.ResetColor();
Console.WriteLine();

// ── Create agent ──────────────────────────────────────────────────────────────
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Creating agent...");
Console.ResetColor();

var credential = new AzureCliCredential();
var client = new AIProjectClient(new Uri(endpoint), credential);

var agent = client.AsAIAgent(
    model: model,
    instructions:
        "You are the Trip Disruption Concierge. Help passengers with flight disruptions. " +
        "Remember everything from earlier in the conversation — the passenger must not " +
        "need to repeat information they have already provided.");

// ── Create session ────────────────────────────────────────────────────────────
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Creating agent session...");
Console.ResetColor();

var session = await agent.CreateSessionAsync();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"[Loop] Session ready — ID: {session.Id}");
Console.ResetColor();
Console.WriteLine();

// ── Multi-turn helper ─────────────────────────────────────────────────────────
int turnNumber = 0;

async Task TurnAsync(string userInput)
{
    turnNumber++;

    Console.WriteLine($"─── Turn {turnNumber} {'─',68}");
    Console.WriteLine();

    Console.ForegroundColor = ConsoleColor.Cyan;
    Console.WriteLine($"[User] {userInput}");
    Console.ResetColor();
    Console.WriteLine();

    Console.ForegroundColor = ConsoleColor.DarkGray;
    Console.Write($"[Loop] Turn {turnNumber} — RunAsync (session: {session.Id[..8]}...)...");
    Console.ResetColor();

    var sw = Stopwatch.StartNew();
    var result = await agent.RunAsync(userInput, session: session);
    sw.Stop();

    Console.ForegroundColor = ConsoleColor.DarkGray;
    Console.WriteLine($" done ({sw.ElapsedMilliseconds} ms)");
    Console.ResetColor();
    Console.WriteLine();

    Console.ForegroundColor = ConsoleColor.Green;
    Console.WriteLine($"[Agent] {result.Text}");
    Console.ResetColor();
    Console.WriteLine();
}

// ── Conversation ──────────────────────────────────────────────────────────────
// Turn 1 — establish the scenario context
await TurnAsync(
    "My name is Emma. My flight AU123 AKL→SYD was just cancelled. " +
    "I have a separate connecting flight SYD→MEL booked independently. " +
    "What should I do first?");

// Turn 2 — follow-up; agent remembers Emma's name, AU123, and the connecting flight
await TurnAsync(
    "The airline is offering a rebooking on tomorrow's flight. " +
    "But I will miss my connecting flight to Melbourne. What are my options?");

// Turn 3 — ask for a synthesis; agent draws on the full conversation history
await TurnAsync(
    "Given everything we have discussed, what is the single best outcome " +
    "I can realistically push for with the airline?");

// ── Summary ───────────────────────────────────────────────────────────────────
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"[Loop] Session complete — {turnNumber} turns, session ID: {session.Id}");
Console.ResetColor();
Console.WriteLine();

Console.WriteLine("Module 03 complete. ✓");
