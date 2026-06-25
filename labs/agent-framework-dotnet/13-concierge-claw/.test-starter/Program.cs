#pragma warning disable OPENAI001
#pragma warning disable MAAI001

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

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Harness] Building IChatClient via Foundry Responses API...");
Console.ResetColor();

IChatClient chatClient =
    new AIProjectClient(new Uri(endpoint), new DefaultAzureCredential())
        .GetProjectOpenAIClient()
        .GetResponsesClient()
        .AsIChatClient(model);

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Harness] Creating ConciergeClaw HarnessAgent...");
Console.ResetColor();

var agentFilesPath = Path.Combine(AppContext.BaseDirectory, "agent-files");

AIAgent agent = chatClient.AsHarnessAgent(new HarnessAgentOptions
{
    Name        = "ConciergeClaw",
    Description = "An empathetic trip disruption concierge that plans and resolves passenger disruptions end-to-end.",
    FileMemoryStore    = new FileSystemAgentFileStore(agentFilesPath),
    LoopEvaluators     =
    [
        new TodoCompletionLoopEvaluator(
            new TodoCompletionLoopEvaluatorOptions { Modes = ["execute"] }),
    ],
    LoopAgentOptions   = new LoopAgentOptions { MaxIterations = 5 },
    ChatOptions        = new ChatOptions
    {
        Instructions = conciergeInstructions,
        Tools        = [AIFunctionFactory.Create(GetFlightAlternatives)],
    },
});

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Harness] ConciergeClaw ready.");
Console.ResetColor();
Console.WriteLine();

var session = await agent.CreateSessionAsync();

var modeProvider = agent.GetService<AgentModeProvider>();
modeProvider?.SetMode(session, "execute");

var currentMode = modeProvider?.GetMode(session) ?? "unknown";
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"[Harness] Session ready. Mode: {currentMode}");
Console.ResetColor();
Console.WriteLine();

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

Console.ForegroundColor = ConsoleColor.Green;
await foreach (var chunk in agent.RunStreamingAsync(query1, session: session))
{
    if (chunk.Text is not null)
        Console.Write(chunk.Text);
}
Console.ResetColor();
Console.WriteLine();
Console.WriteLine();

// ── Turn 2 setup ──────────────────────────────────────────────────────────────
Console.WriteLine($"─── Turn 2 {'─',68}");
Console.WriteLine();

var query2 = "Which of those rebooking options has the earliest departure?";

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine($"[User] {query2}");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Green;
await foreach (var chunk in agent.RunStreamingAsync(query2, session: session))
{
    if (chunk.Text is not null)
        Console.Write(chunk.Text);
}
Console.ResetColor();
Console.WriteLine();
Console.WriteLine();

// ── Session export / import setup ────────────────────────────────────────────
Console.WriteLine($"─── Session Export / Import {'─',50}");
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Harness] Exporting session to snapshot...");
Console.ResetColor();

JsonElement snapshot = await agent.SerializeSessionAsync(session);

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Harness] Snapshot captured. Restoring session from snapshot...");
Console.ResetColor();

var restoredSession = await agent.DeserializeSessionAsync(snapshot);

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Harness] Session restored. Continuing on restored session...");
Console.ResetColor();
Console.WriteLine();

// ── Turn 3 setup ──────────────────────────────────────────────────────────────
Console.WriteLine($"─── Turn 3 (restored session) {'─',47}");
Console.WriteLine();

var query3 = "Can you give me a quick summary of everything you've arranged for me?";

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine($"[User] {query3}");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Green;
await foreach (var chunk in agent.RunStreamingAsync(query3, session: restoredSession))
{
    if (chunk.Text is not null)
        Console.Write(chunk.Text);
}
Console.ResetColor();
Console.WriteLine();
Console.WriteLine();

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
