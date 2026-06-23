using Azure.Identity;
using Azure.AI.Projects;
using DotNetEnv;
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Foundry;
using Microsoft.Agents.AI.Foundry.Hosting;

// Load environment variables from .env in the repository root (searches parent directories)
Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var model = Environment.GetEnvironmentVariable("AGENT_MODEL") ?? "chat";
var agentName = Environment.GetEnvironmentVariable("HOSTED_AGENT_NAME") ?? "trip-disruption-concierge";

var credential = new AzureCliCredential();

// ── TODO 1 ───────────────────────────────────────────────────────────────────
// Create the AIAgent.  Use AIProjectClient.AsAIAgent() with a name and
// description so Foundry can identify this agent.
//
// AIAgent agent = new AIProjectClient(new Uri(endpoint), credential)
//     .AsAIAgent(
//         model: model,
//         name: agentName,
//         instructions:
//             "You are the Trip Disruption Concierge, a helpful assistant " +
//             "for passengers experiencing flight delays or cancellations. " +
//             "Help passengers understand their rights and next steps.",
//         description:
//             "Helps passengers with flight disruption questions and compensation claims.");
//
// ─────────────────────────────────────────────────────────────────────────────

var builder = WebApplication.CreateBuilder(args);

// ── TODO 2 ───────────────────────────────────────────────────────────────────
// Register the Foundry Responses services with the DI container.
//
// builder.Services.AddFoundryResponses(agent);
//
// ─────────────────────────────────────────────────────────────────────────────

var app = builder.Build();

// ── TODO 3 ───────────────────────────────────────────────────────────────────
// Map the Foundry Responses endpoint and start the web server.
//
// app.MapFoundryResponses();
// app.Run();
//
// ─────────────────────────────────────────────────────────────────────────────

throw new NotImplementedException(
    "Complete the TODOs above, then remove this line and the throw statement.");
