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

Console.WriteLine("=== Trip Disruption Concierge — Module 11: Agent Identity & Auth ===");
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("This module compares Azure credential strategies for agent applications.");
Console.ResetColor();
Console.WriteLine();

// ── TODO 1 ───────────────────────────────────────────────────────────────────
// Create an agent using DefaultAzureCredential and run one turn.
// DefaultAzureCredential tries a chain of credential sources automatically.
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Auth] Strategy 1: DefaultAzureCredential");
// Console.ResetColor();
//
// var defaultCredential = new AzureCliCredential();
// AIAgent agentDefault = new AIProjectClient(new Uri(endpoint), defaultCredential)
//     .AsAIAgent(
//         model: model,
//         instructions: "You are the Trip Disruption Concierge. Be concise.");
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {await agentDefault.RunAsync(
//     "My flight AU123 was cancelled. What is the first thing I should do?")}");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 2 ───────────────────────────────────────────────────────────────────
// Create an agent using a ChainedTokenCredential that combines
// ManagedIdentityCredential (production) and AzureCliCredential (dev).
// On a developer laptop the managed identity is unavailable, so the chain
// falls through to the CLI credential automatically.
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Auth] Strategy 2: ChainedTokenCredential " +
//                   "(ManagedIdentity → AzureCLI)");
// Console.ResetColor();
//
// var chainedCredential = new ChainedTokenCredential(
//     new ManagedIdentityCredential(),
//     new AzureCliCredential());
//
// AIAgent agentChained = new AIProjectClient(new Uri(endpoint), chainedCredential)
//     .AsAIAgent(
//         model: model,
//         instructions: "You are the Trip Disruption Concierge. Be concise.");
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {await agentChained.RunAsync(
//     "What compensation am I entitled to for a 3-hour notice cancellation?")}");
// Console.ResetColor();
// Console.WriteLine();
//
// Console.WriteLine("Module 11 complete. ✓");
//
// ─────────────────────────────────────────────────────────────────────────────

throw new NotImplementedException(
    "Complete the TODOs above, then remove this line and the throw statement.");
