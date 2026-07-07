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

Console.WriteLine("=== Trip Disruption Concierge - Module 11: Agent Identity & Auth ===");
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("This module compares Azure credential strategies for agent applications.");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Auth] Strategy 1: AzureCliCredential");
Console.ResetColor();

var cliCredential = new AzureCliCredential();
AIAgent agentCli = new AIProjectClient(new Uri(endpoint), cliCredential)
    .AsAIAgent(
        model: model,
        instructions: "You are the Trip Disruption Concierge. Be concise.");

Console.ForegroundColor = ConsoleColor.Green;
Console.WriteLine($"[Agent] {(await agentCli.RunAsync(
    "My flight AU123 was cancelled. What is the first thing I should do?")).Text}");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Auth] Strategy 2: ChainedTokenCredential " +
                  "(WorkloadIdentity \u2192 AzureCLI)");
Console.ResetColor();

var chainedCredential = new ChainedTokenCredential(
    new WorkloadIdentityCredential(),   // CI/CD with OIDC — fails fast on dev
    new AzureCliCredential());

AIAgent agentChained = new AIProjectClient(new Uri(endpoint), chainedCredential)
    .AsAIAgent(
        model: model,
        instructions: "You are the Trip Disruption Concierge. Be concise.");

Console.ForegroundColor = ConsoleColor.Green;
Console.WriteLine($"[Agent] {(await agentChained.RunAsync(
    "What are the rebooking options when a flight is cancelled?")).Text}");
Console.ResetColor();
Console.WriteLine();

Console.WriteLine("Module 11 complete. \u2713");
