using System.Text;
using System.Text.RegularExpressions;
using Azure.Identity;
using Azure.AI.Projects;
using DotNetEnv;
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Foundry;
using Microsoft.Extensions.AI;

// Load environment variables from .env in the repository root (searches parent directories)
Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var model = Environment.GetEnvironmentVariable("AGENT_MODEL") ?? "chat";

Console.WriteLine("=== Trip Disruption Concierge - Module 07: Memory & Context Providers ===");
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"  Model : {model}");
Console.ResetColor();
Console.WriteLine();

var credential = new AzureCliCredential();
var projectClient = new AIProjectClient(new Uri(endpoint), credential);

// ── Step 1: Get a raw IChatClient from Foundry ────────────────────────────────
// We need the IChatClient so we can wrap it with custom AIContextProviders.
// AsAIAgent() creates an agent from the project client; GetService<IChatClient>()
// extracts the underlying chat client from it.
IChatClient chatClient = projectClient
    .AsAIAgent(new ChatClientAgentOptions { ChatOptions = new() { ModelId = model } })
    .GetService<IChatClient>()
    ?? throw new InvalidOperationException("Could not retrieve IChatClient.");

// ── Step 2: Wrap the IChatClient with a memory-aware agent ────────────────────
// chatClient.AsAIAgent() creates a fresh agent with the PassengerProfileMemory
// context provider attached.  The context provider intercepts each turn to
// extract and persist the passenger profile, then inject it as instructions.
AIAgent agent = chatClient.AsAIAgent(new ChatClientAgentOptions
{
    ChatOptions = new()
    {
        ModelId = model,
        Instructions =
            "You are the Trip Disruption Concierge. " +
            "You help passengers who have experienced flight disruptions. " +
            "Always address the passenger by name if known. " +
            "Reference their specific flight number when relevant. " +
            "Be empathetic and provide clear, actionable guidance."
    },
    AIContextProviders = [new PassengerProfileMemory()]
});

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Agent] Agent ready with passenger profile memory.");
Console.ResetColor();
Console.WriteLine();

// ── Multi-turn session ────────────────────────────────────────────────────────
var session = await agent.CreateSessionAsync();
int turn = 0;

async Task AskAsync(string question)
{
    turn++;
    Console.WriteLine($"─── Turn {turn} {'─',68}");
    Console.WriteLine();

    Console.ForegroundColor = ConsoleColor.Cyan;
    Console.WriteLine($"[User] {question}");
    Console.ResetColor();
    Console.WriteLine();

    var result = await agent.RunAsync(question, session: session);

    Console.ForegroundColor = ConsoleColor.Green;
    Console.WriteLine($"[Agent] {result.Text}");
    Console.ResetColor();
    Console.WriteLine();
}

await AskAsync(
    "Hi, my name is Emma Chen. My flight AU123 AKL→SYD was cancelled with " +
    "only 3 hours' notice. What are my options?");

await AskAsync("What compensation am I typically entitled to for a cancellation like mine?");

await AskAsync("What should I do if the airline just offers a voucher and not cash?");

// Deliberately ask for memory recall without re-stating the name or flight:
await AskAsync("Can you remind me - what was my flight number again?");

Console.WriteLine("Module 07 complete. ✓");

// ── PassengerProfileMemory ────────────────────────────────────────────────────
// A custom AIContextProvider that extracts and remembers the passenger's name
// and flight number from conversation messages, then injects them as
// personalised instructions before every model call.
internal sealed class PassengerProfileMemory : AIContextProvider
{
    private static readonly Regex NamePattern =
        new(@"(?i)my name is\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)", RegexOptions.Compiled);

    private static readonly Regex FlightPattern =
        new(@"(?i)\bflight\s+([A-Z]{1,3}\d{1,5})\b", RegexOptions.Compiled);

    private readonly ProviderSessionState<PassengerProfile> _state;

    public PassengerProfileMemory()
    {
        _state = new ProviderSessionState<PassengerProfile>(
            _ => new PassengerProfile(),
            GetType().Name);
    }

    // Expose the state key so the framework can serialise it correctly.
    public override IReadOnlyList<string> StateKeys => [_state.StateKey];

    // Called BEFORE the model: inject the remembered profile as instructions.
    protected override ValueTask<AIContext> ProvideAIContextAsync(
        InvokingContext context, CancellationToken cancellationToken = default)
    {
        var profile = _state.GetOrInitializeState(context.Session);

        if (profile.Name is null && profile.FlightNumber is null)
            return ValueTask.FromResult(new AIContext());

        var sb = new StringBuilder("Current passenger profile:\n");
        if (profile.Name is not null)
            sb.AppendLine($"  Name          : {profile.Name}");
        if (profile.FlightNumber is not null)
            sb.AppendLine($"  Flight number : {profile.FlightNumber}");

        Console.ForegroundColor = ConsoleColor.Yellow;
        Console.WriteLine($"\n[Memory] Injecting profile - {sb.ToString().Trim()}");
        Console.ResetColor();

        return ValueTask.FromResult(new AIContext { Instructions = sb.ToString() });
    }

    // Called AFTER the model: scan user messages for name and flight details.
    protected override ValueTask StoreAIContextAsync(
        InvokedContext context, CancellationToken cancellationToken = default)
    {
        var profile = _state.GetOrInitializeState(context.Session);
        bool changed = false;

        foreach (var msg in context.RequestMessages.Where(m => m.Role == ChatRole.User))
        {
            var text = msg.Text ?? string.Empty;

            if (profile.Name is null)
            {
                var nameMatch = NamePattern.Match(text);
                if (nameMatch.Success)
                {
                    profile.Name = nameMatch.Groups[1].Value.Trim();
                    changed = true;
                }
            }

            if (profile.FlightNumber is null)
            {
                var flightMatch = FlightPattern.Match(text);
                if (flightMatch.Success)
                {
                    profile.FlightNumber = flightMatch.Groups[1].Value.ToUpperInvariant();
                    changed = true;
                }
            }
        }

        if (changed)
        {
            _state.SaveState(context.Session, profile);

            Console.ForegroundColor = ConsoleColor.Yellow;
            Console.WriteLine($"\n[Memory] Profile updated - Name: {profile.Name ?? "(unknown)"}, " +
                              $"Flight: {profile.FlightNumber ?? "(unknown)"}");
            Console.ResetColor();
        }

        return ValueTask.CompletedTask;
    }
}

// ── PassengerProfile ──────────────────────────────────────────────────────────
internal sealed class PassengerProfile
{
    public string? Name { get; set; }
    public string? FlightNumber { get; set; }
}
