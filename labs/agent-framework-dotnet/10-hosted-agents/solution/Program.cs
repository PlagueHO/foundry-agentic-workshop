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

// ── Create agent ──────────────────────────────────────────────────────────────
// The name and description are passed to Foundry so they appear in the portal
// when the agent is deployed as a Hosted Agent.
AIAgent agent = new AIProjectClient(new Uri(endpoint), credential)
    .AsAIAgent(
        model: model,
        name: agentName,
        instructions:
            "You are the Trip Disruption Concierge, a helpful assistant " +
            "for passengers experiencing flight delays or cancellations. " +
            "Help passengers understand their rights, claim compensation, " +
            "and arrange alternative travel. Be empathetic and concise.",
        description:
            "Helps passengers with flight disruption questions and compensation claims.");

// ── Configure web host ────────────────────────────────────────────────────────
var builder = WebApplication.CreateBuilder(args);

// AddFoundryResponses registers the Foundry Responses API services,
// including the request handler and session management for this agent.
builder.Services.AddFoundryResponses(agent);

var app = builder.Build();

// MapFoundryResponses adds the /api/responses route (and a root metadata route)
// that Foundry calls when routing messages to this Hosted Agent.
app.MapFoundryResponses();

// Start the web server.  Azure Container Apps (used by Foundry Hosted Agents)
// will set ASPNETCORE_URLS automatically; locally Kestrel listens on :5000.
app.Run();
