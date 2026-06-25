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

// ── TODO 1 ───────────────────────────────────────────────────────────────────
// Obtain an IChatClient from the Foundry project client so we can wrap it with
// custom AIContextProviders.
//
// IChatClient chatClient = projectClient
//     .AsAIAgent(new ChatClientAgentOptions { ChatOptions = new() { ModelId = model } })
//     .GetService<IChatClient>()
//     ?? throw new InvalidOperationException("Could not retrieve IChatClient.");
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 2 ───────────────────────────────────────────────────────────────────
// Wrap the IChatClient with an agent that uses PassengerProfileMemory.
// The memory provider will extract passenger details from user messages and
// inject them as instructions before each model call.
//
// AIAgent agent = chatClient.AsAIAgent(new ChatClientAgentOptions
// {
//     ChatOptions = new()
//     {
//         ModelId = model,
//         Instructions =
//             "You are the Trip Disruption Concierge. " +
//             "You help passengers who have experienced flight disruptions. " +
//             "Always address the passenger by name if known. " +
//             "Reference their specific flight number when relevant."
//     },
//     AIContextProviders = [new PassengerProfileMemory()]
// });
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Agent] Agent ready with passenger profile memory.");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine("[User] Hi, my name is Emma Chen. My flight AU123 was cancelled.");
Console.ResetColor();
Console.WriteLine();

// ── TODO 3 ───────────────────────────────────────────────────────────────────
// Run a multi-turn session and observe the agent recalling the profile.
//
// var session = await agent.CreateSessionAsync();
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {await agent.RunAsync(
//     "Hi, my name is Emma Chen. My flight AU123 AKL→SYD was cancelled with " +
//     "3 hours' notice. What are my options?",
//     session: session)}");
// Console.ResetColor();
// Console.WriteLine();
//
// Console.ForegroundColor = ConsoleColor.Cyan;
// Console.WriteLine("[User] What compensation is typically available for a cancellation?");
// Console.ResetColor();
// Console.WriteLine();
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {await agent.RunAsync(
//     "What compensation is typically available for a cancellation like mine?",
//     session: session)}");
// Console.ResetColor();
// Console.WriteLine();
//
// Console.ForegroundColor = ConsoleColor.Cyan;
// Console.WriteLine("[User] Can you remind me - what was my flight number?");
// Console.ResetColor();
// Console.WriteLine();
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {await agent.RunAsync(
//     "By the way, can you remind me - what was my flight number?",
//     session: session)}");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

throw new NotImplementedException(
    "Complete the TODOs above, then remove this line and the throw statement.");

// ── PassengerProfileMemory ────────────────────────────────────────────────────
// A custom AIContextProvider that remembers the passenger's name and flight
// number, then injects them as personalised instructions before every model call.
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

    // Called AFTER the model: scan user messages for name and flight details.
    protected override ValueTask StoreAIContextAsync(
        InvokedContext context, CancellationToken cancellationToken = default)
    {
        var profile = _state.GetOrInitializeState(context.Session);

        // ── TODO 4 ───────────────────────────────────────────────────────────────
        // Scan all user messages and extract the passenger's name and flight number.
        // Save the updated profile so it persists across turns.
        //
        // foreach (var msg in context.RequestMessages.Where(m => m.Role == ChatRole.User))
        // {
        //     var text = msg.Text ?? string.Empty;
        //     if (profile.Name is null)
        //     {
        //         var nameMatch = NamePattern.Match(text);
        //         if (nameMatch.Success)
        //             profile.Name = nameMatch.Groups[1].Value.Trim();
        //     }
        //     if (profile.FlightNumber is null)
        //     {
        //         var flightMatch = FlightPattern.Match(text);
        //         if (flightMatch.Success)
        //             profile.FlightNumber = flightMatch.Groups[1].Value.ToUpperInvariant();
        //     }
        // }
        // _state.SaveState(context.Session, profile);
        //
        // ─────────────────────────────────────────────────────────────────────────

        return ValueTask.CompletedTask;
    }

    // Called BEFORE the model: inject the remembered profile as instructions.
    protected override ValueTask<AIContext> ProvideAIContextAsync(
        InvokingContext context, CancellationToken cancellationToken = default)
    {
        var profile = _state.GetOrInitializeState(context.Session);

        // ── TODO 5 ───────────────────────────────────────────────────────────────
        // Read the stored profile and return it as instructions.
        // Return an empty AIContext when nothing has been stored yet.
        //
        // var sb = new StringBuilder();
        // if (profile.Name is not null)
        //     sb.AppendLine($"The passenger's name is {profile.Name}.");
        // if (profile.FlightNumber is not null)
        //     sb.AppendLine($"Their flight number is {profile.FlightNumber}.");
        // return new AIContext { Instructions = sb.ToString() };
        //
        // ─────────────────────────────────────────────────────────────────────────

        return ValueTask.FromResult(new AIContext());
    }
}

// ── PassengerProfile ──────────────────────────────────────────────────────────
internal sealed class PassengerProfile
{
    public string? Name { get; set; }
    public string? FlightNumber { get; set; }
}
