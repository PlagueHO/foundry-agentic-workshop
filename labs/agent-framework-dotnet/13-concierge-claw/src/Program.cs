#pragma warning disable OPENAI001
#pragma warning disable MAAI001
#pragma warning disable CS0219 // Starter: variables used only in commented-out TODO blocks
#pragma warning disable CS8321 // Starter: local functions used only in commented-out TODO blocks

using System.ComponentModel;
using System.Text.Json;
using Azure.AI.Projects;
using Azure.Identity;
using DotNetEnv;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;

Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var model = Environment.GetEnvironmentVariable("AGENT_MODEL") ?? "chat";

Console.WriteLine("=== Trip Disruption Concierge - Module 13: ConciergeClaw - Agent Harness ===");
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"  Model    : {model}");
Console.ResetColor();
Console.WriteLine();

var conciergeInstructions =
    """
    ## Trip Disruption Concierge Instructions

    You are an empathetic trip disruption concierge helping airline passengers
    affected by flight cancellations or significant delays.

    When a passenger reports a disruption:
    1. Look up alternative flights using the get_flight_alternatives tool.
    2. Use web search to find hotels near the affected airport.
    3. Explain the passenger's compensation entitlements under relevant rules.
    4. Provide a clear, prioritised action plan.

    Keep a file called `passenger-profile.md` with the passenger's name,
    flight number, disruption type, and current resolution status.
    Update it as the conversation progresses.

    Be concise, action-oriented, and cite any regulatory information you reference.
    """;

// ── TODO 1 ───────────────────────────────────────────────────────────────────
// Build an IChatClient using the Foundry Responses API chain.
// The harness requires an IChatClient - not the AsAIAgent(model: ...) shortcut.
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Harness] Building IChatClient via Foundry Responses API...");
// Console.ResetColor();
//
// var credential = new AzureCliCredential();
// IChatClient chatClient = new AIProjectClient(new Uri(endpoint), credential)
//    .GetProjectOpenAIClient()
//    .GetResponsesClient()
//    .AsIChatClient(model);
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 2 ───────────────────────────────────────────────────────────────────
// Wrap chatClient in a HarnessAgent. Configure: Name, Description,
// FileMemoryStore, LoopEvaluators, LoopAgentOptions, and ChatOptions.
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Harness] Creating ConciergeClaw HarnessAgent...");
// Console.ResetColor();
//
// var agentFilesPath = Path.Combine(AppContext.BaseDirectory, "agent-files");
//
// AIAgent agent = chatClient.AsHarnessAgent(new HarnessAgentOptions
// {
//     Name        = "ConciergeClaw",
//     Description = "An empathetic trip disruption concierge that plans and resolves passenger disruptions end-to-end.",
//     FileMemoryStore    = new FileSystemAgentFileStore(agentFilesPath),
//     LoopEvaluators     =
//     [
//         new TodoCompletionLoopEvaluator(
//             new TodoCompletionLoopEvaluatorOptions { Modes = ["execute"] }),
//     ],
//     LoopAgentOptions   = new LoopAgentOptions { MaxIterations = 5 },
//     ChatOptions        = new ChatOptions
//     {
//         Instructions = conciergeInstructions,
//         Tools        = [AIFunctionFactory.Create(GetFlightAlternatives)],
//     },
// });
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Harness] ConciergeClaw ready.");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 3 ───────────────────────────────────────────────────────────────────
// Create a session: var session = await agent.CreateSessionAsync();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 4 ───────────────────────────────────────────────────────────────────
// Get AgentModeProvider from the agent and switch to execute mode.
//
// var modeProvider = agent.GetService<AgentModeProvider>();
// modeProvider?.SetMode(session, "execute");
//
// var currentMode = modeProvider?.GetMode(session) ?? "unknown";
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine($"[Harness] Session ready. Mode: {currentMode}");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── Turn 1 setup ──────────────────────────────────────────────────────────────
Console.WriteLine($"─── Turn 1 {'─',68}");
Console.WriteLine();

var query1 =
    "I'm Emma Chen. My flight AU123 from Auckland to Sydney was cancelled " +
    "with only 3 hours' notice. I need rebooking options, overnight accommodation " +
    "near Auckland Airport, and to understand my compensation entitlements.";

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine($"[User] {query1}");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Harness] Running - LoopAgent will iterate until all todos are resolved...");
Console.ResetColor();
Console.WriteLine();

// ── TODO 5 ───────────────────────────────────────────────────────────────────
// Stream Turn 1 using agent.RunStreamingAsync(query1, session: session).
// Print each chunk.Text that is not null. Add blank lines after.
//
// Console.ForegroundColor = ConsoleColor.Green;
// await foreach (var chunk in agent.RunStreamingAsync(query1, session: session))
// {
//     if (chunk.Text is not null)
//         Console.Write(chunk.Text);
// }
// Console.ResetColor();
// Console.WriteLine();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── Turn 2 setup ──────────────────────────────────────────────────────────────
Console.WriteLine($"─── Turn 2 {'─',68}");
Console.WriteLine();

var query2 = "Which of those rebooking options has the earliest departure?";

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine($"[User] {query2}");
Console.ResetColor();
Console.WriteLine();

// ── TODO 6 ───────────────────────────────────────────────────────────────────
// Stream Turn 2 using agent.RunStreamingAsync(query2, session: session).
// Print each chunk.Text that is not null. Add blank lines after.
//
// Console.ForegroundColor = ConsoleColor.Green;
// await foreach (var chunk in agent.RunStreamingAsync(query2, session: session))
// {
//     if (chunk.Text is not null)
//         Console.Write(chunk.Text);
// }
// Console.ResetColor();
// Console.WriteLine();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── Session export / import setup ────────────────────────────────────────────
Console.WriteLine($"─── Session Export / Import {'─',50}");
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Harness] Exporting session to snapshot...");
Console.ResetColor();

// ── TODO 7 ───────────────────────────────────────────────────────────────────
// Serialise the session and restore it:
//   SerializeSessionAsync(session)   → JsonElement snapshot
//   DeserializeSessionAsync(snapshot) → IAgentSession restoredSession
//
// JsonElement snapshot = await agent.SerializeSessionAsync(session);
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Harness] Snapshot captured. Restoring session from snapshot...");
// Console.ResetColor();
//
// var restoredSession = await agent.DeserializeSessionAsync(snapshot);
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Harness] Session restored. Continuing on restored session...");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── Turn 3 setup ──────────────────────────────────────────────────────────────
Console.WriteLine($"─── Turn 3 (restored session) {'─',47}");
Console.WriteLine();

var query3 = "Can you give me a quick summary of everything you've arranged for me?";

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine($"[User] {query3}");
Console.ResetColor();
Console.WriteLine();

// ── TODO 8 ───────────────────────────────────────────────────────────────────
// Stream Turn 3 using the restored session.
// Use agent.RunStreamingAsync(query3, session: restoredSession).
// Print each chunk.Text that is not null. Add blank lines after.
//
// Console.ForegroundColor = ConsoleColor.Green;
// await foreach (var chunk in agent.RunStreamingAsync(query3, session: restoredSession))
// {
//     if (chunk.Text is not null)
//         Console.Write(chunk.Text);
// }
// Console.ResetColor();
// Console.WriteLine();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

throw new NotImplementedException(
    "Complete the TODOs above, then remove this line and the throw statement.");

// ── get_flight_alternatives tool ──────────────────────────────────────────────
[Description("Look up alternative flights for a cancelled or delayed service.")]
static FlightOption[] GetFlightAlternatives(
    [Description("The disrupted flight number, e.g. AU123.")]  string flightNumber,
    [Description("IATA origin airport code, e.g. AKL.")]       string origin,
    [Description("IATA destination airport code, e.g. SYD.")]  string destination)
{
    Console.ForegroundColor = ConsoleColor.Yellow;
    Console.WriteLine(
        $"\n[Tool] → get_flight_alternatives(flightNumber={flightNumber}, {origin}→{destination})");
    Console.ResetColor();

    // Illustrative mock data - replace with a live flights API in production.
    FlightOption[] options = flightNumber.ToUpperInvariant() switch
    {
        "AU123" =>
        [
            new("AU125", "AKL", "SYD", DateTimeOffset.UtcNow.AddHours(3), "Economy",  8),
            new("AU127", "AKL", "SYD", DateTimeOffset.UtcNow.AddHours(6), "Economy", 32),
            new("QZ451", "AKL", "SYD", DateTimeOffset.UtcNow.AddHours(4), "Economy", 15),
        ],
        _ => [new("No alternatives found", origin, destination, DateTimeOffset.UtcNow.AddHours(24), "N/A", 0)]
    };

    Console.ForegroundColor = ConsoleColor.Yellow;
    Console.WriteLine($"[Tool] ← {options.Length} option(s) returned");
    Console.ResetColor();

    return options;
}

// ── FlightOption record ───────────────────────────────────────────────────────
record FlightOption(
    string         FlightNumber,
    string         Origin,
    string         Destination,
    DateTimeOffset DepartureUtc,
    string         CabinClass,
    int            SeatsAvailable);
