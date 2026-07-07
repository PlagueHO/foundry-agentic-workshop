#pragma warning disable OPENAI001
#pragma warning disable MAAI001

using System.ComponentModel;
using Azure.AI.Projects;
using Azure.Identity;
using DotNetEnv;
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Foundry;
using Microsoft.Agents.AI.Hosting.AGUI.AspNetCore;
using Microsoft.Extensions.AI;

// Load environment variables from .env in the repository root (searches parent directories)
Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var model = Environment.GetEnvironmentVariable("AGENT_MODEL") ?? "chat";

Console.WriteLine("=== Trip Disruption Concierge - Module 16: AG-UI Server ===");
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"  Model : {model}");
Console.ResetColor();
Console.WriteLine();

var builder = WebApplication.CreateBuilder(args);

// ── Register AG-UI services ───────────────────────────────────────────────────
// AddAGUI() registers the SSE request handling and routing infrastructure
// that MapAGUI needs to stream AG-UI events to browser clients.
builder.Services.AddHttpClient().AddLogging();
builder.Services.AddAGUI();

var app = builder.Build();

// ── Create the concierge agent ────────────────────────────────────────────────
// AsAIAgent() is the same pattern used since Module 02. Here we add one scalar
// backend tool: GetFlightStatus (string → string). A scalar return type avoids
// the JsonSerializerContext requirement for complex types (see MS Learn docs).
AIAgent agent = new AIProjectClient(new Uri(endpoint), new DefaultAzureCredential())
    .AsAIAgent(
        model: model,
        name: "trip-disruption-concierge",
        instructions:
            """
            You are the Trip Disruption Concierge for Air New Zealand.
            You help passengers affected by flight cancellations and delays.

            When a passenger reports a disrupted flight:
            1. Call get_flight_status to confirm the current status of their flight.
            2. Acknowledge the disruption with empathy.
            3. Explain their options: rebooking on the next flight,
               hotel accommodation if overnight, and compensation entitlements.

            Keep responses concise, clear, and supportive.
            """,
        tools: [AIFunctionFactory.Create(GetFlightStatus)]);

// ── Map the AG-UI endpoint ────────────────────────────────────────────────────
// MapAGUI registers an HTTP handler at "/" that:
//   • Receives a POST request from the CopilotKit runtime (Next.js side)
//   • Runs the agent
//   • Streams AG-UI SSE events (RUN_STARTED, TEXT_MESSAGE_CONTENT, TOOL_CALL_*, etc.)
app.MapAGUI("/", agent);

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Server] AG-UI endpoint mapped at /");
Console.WriteLine("[Server] Waiting for CopilotKit connections (port 8888)...");
Console.ResetColor();
Console.WriteLine();

await app.RunAsync();

// ── Backend tool ──────────────────────────────────────────────────────────────
// GetFlightStatus runs on the .NET server. The AI model calls it as a function
// tool; the result is returned to the model and also streamed to the browser as
// a TOOL_CALL_RESULT AG-UI event — no client-side code needed.

[Description("Get the current status of a flight.")]
static string GetFlightStatus(
    [Description("The flight number to look up, for example AU123.")] string flightNumber)
{
    Console.ForegroundColor = ConsoleColor.Yellow;
    Console.WriteLine($"[Tool] → get_flight_status({flightNumber})");
    Console.ResetColor();

    var status = flightNumber.ToUpperInvariant() switch
    {
        "AU123" => $"Flight {flightNumber}: Cancelled. Next available service AU125 departs 17:45.",
        "AU456" => $"Flight {flightNumber}: Delayed 2 hours. New estimated departure 14:30.",
        _       => $"Flight {flightNumber}: On time.",
    };

    Console.ForegroundColor = ConsoleColor.Yellow;
    Console.WriteLine($"[Tool] ← {status}");
    Console.ResetColor();

    return status;
}
