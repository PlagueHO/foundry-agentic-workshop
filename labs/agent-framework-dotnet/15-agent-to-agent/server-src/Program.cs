using A2A;
using A2A.AspNetCore;
using Azure.Identity;
using Azure.AI.Projects;
using DotNetEnv;
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Foundry;

// Load environment variables from .env in the repository root (searches parent directories)
Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var model = Environment.GetEnvironmentVariable("AGENT_MODEL") ?? "chat";

const string AgentName = "compensation-specialist";

Console.WriteLine("=== Trip Disruption Concierge - Module 15: Compensation Specialist (A2A server) ===");
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"  Agent : {AgentName}");
Console.WriteLine($"  Model : {model}");
Console.ResetColor();
Console.WriteLine();

var builder = WebApplication.CreateBuilder(args);

// ── TODO 1 ───────────────────────────────────────────────────────────────────
// Register the Compensation Specialist as a keyed singleton AIAgent. The A2A
// hosting extensions resolve agents from the DI container using this key.
//
// builder.Services.AddKeyedSingleton<AIAgent>(AgentName, (_, _) =>
// {
//     var credential = new DefaultAzureCredential();
//     return new AIProjectClient(new Uri(endpoint), credential)
//         .AsAIAgent(
//             model: model,
//             name: AgentName,
//             instructions:
//                 "You are the Compensation Specialist. Your sole focus is " +
//                 "explaining and calculating passenger compensation " +
//                 "entitlements under airline disruption policies. Provide " +
//                 "clear figures and actionable next steps. Do not discuss " +
//                 "rebooking or hotels.",
//             description:
//                 "Explains and calculates the passenger's compensation entitlement.");
// });
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 2 ───────────────────────────────────────────────────────────────────
// Register the A2A server for the Compensation Specialist agent.
//
// builder.AddA2AServer(AgentName);
//
// ─────────────────────────────────────────────────────────────────────────────

var app = builder.Build();

// ── TODO 3 ───────────────────────────────────────────────────────────────────
// Map the A2A HTTP+JSON endpoint and publish the well-known agent card so
// remote clients can discover this agent's capabilities before calling it.
//
// app.MapA2AHttpJson(AgentName, "/a2a/compensation-specialist");
//
// app.MapWellKnownAgentCard(new AgentCard
// {
//     Name = "CompensationSpecialist",
//     Description =
//         "Explains and calculates passenger compensation entitlements " +
//         "under airline disruption policies.",
//     Version = "1.0",
//     DefaultInputModes = ["text"],
//     DefaultOutputModes = ["text"],
//     SupportedInterfaces =
//     [
//         new AgentInterface
//         {
//             Url = "http://localhost:5000/a2a/compensation-specialist",
//             ProtocolBinding = ProtocolBindingNames.HttpJson,
//             ProtocolVersion = "1.0",
//         }
//     ]
// });
//
// app.Run();
//
// ─────────────────────────────────────────────────────────────────────────────

throw new NotImplementedException(
    "Complete the TODOs above, then remove this line and the throw statement.");
