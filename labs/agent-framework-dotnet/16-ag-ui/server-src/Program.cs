#pragma warning disable OPENAI001
#pragma warning disable MAAI001
#pragma warning disable CS8321 // GetFlightStatus is referenced only inside TODO 2 comments

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

// ── TODO 1 ───────────────────────────────────────────────────────────────────
// Register AG-UI services with the DI container.
// AddAGUI() wires up the SSE request handling infrastructure needed by MapAGUI.
//
// ┋ builder.Services.AddHttpClient().AddLogging();
// ┋ builder.Services.AddAGUI();
//
// ─────────────────────────────────────────────────────────────────────────────

var app = builder.Build();

// ── TODO 2 ───────────────────────────────────────────────────────────────────
// Create the Trip Disruption Concierge agent with a scalar GetFlightStatus tool.
// Use AsAIAgent() from earlier modules, then pass AIFunctionFactory.Create(GetFlightStatus).
// A scalar (string → string) tool avoids the JsonSerializerContext requirement.
//
// ┋ AIAgent agent = new AIProjectClient(new Uri(endpoint), new DefaultAzureCredential())
// ┋     .AsAIAgent(
// ┋         model: model,
// ┋         name: "trip-disruption-concierge",
// ┋         instructions:
// ┋             """
// ┋             You are the Trip Disruption Concierge for Air New Zealand.
// ┋             When a passenger reports a disrupted flight:
// ┋             1. Call get_flight_status to confirm the current status of their flight.
// ┋             2. Acknowledge the disruption with empathy.
// ┋             3. Explain their options: rebooking, accommodation, compensation.
// ┋             Keep responses concise and supportive.
// ┋             """,
// ┋         tools: [AIFunctionFactory.Create(GetFlightStatus)]);
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 3 ───────────────────────────────────────────────────────────────────
// Map the AG-UI SSE endpoint and start the server.
// MapAGUI("/", agent) registers the handler at / and streams AG-UI events back.
//
// ┋ app.MapAGUI("/", agent);
// ┋
// ┋ Console.ForegroundColor = ConsoleColor.DarkGray;
// ┋ Console.WriteLine("[Server] AG-UI endpoint mapped at /");
// ┋ Console.WriteLine("[Server] Waiting for CopilotKit connections (port 8888)...");
// ┋ Console.ResetColor();
// ┋ Console.WriteLine();
// ┋
// ┋ await app.RunAsync();
//
// ─────────────────────────────────────────────────────────────────────────────

throw new NotImplementedException("Complete the TODOs above, then remove this line and the throw statement.");

// ── Backend tool ──────────────────────────────────────────────────────────────
// This function runs on the server. The result is streamed to the browser as a
// TOOL_CALL_RESULT AG-UI event — the CopilotKit sidebar shows it automatically.

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
