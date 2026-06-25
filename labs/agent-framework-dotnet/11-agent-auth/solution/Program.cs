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
Console.WriteLine("Comparing Azure credential strategies for agent applications.");
Console.ResetColor();
Console.WriteLine();

// ── Strategy 1: DefaultAzureCredential ────────────────────────────────────────
// DefaultAzureCredential automatically tries a preset sequence of credentials:
//   EnvironmentCredential → WorkloadIdentityCredential → ManagedIdentityCredential
//   → AzureDeveloperCliCredential → AzureCliCredential → AzurePowerShellCredential
//   → AzureApplicationCredential
//
// Best for: getting started quickly; works in most environments without changes.
// Trade-off: the long chain can add latency on first authentication.
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Auth] Strategy 1: DefaultAzureCredential");
Console.WriteLine("[Auth] Tries: EnvironmentCredential → WorkloadIdentity →");
Console.WriteLine("[Auth]        ManagedIdentity → AzureDeveloperCLI → AzureCLI → ...");
Console.ResetColor();
Console.WriteLine();

var defaultCredential = new AzureCliCredential();

AIAgent agentDefault = new AIProjectClient(new Uri(endpoint), defaultCredential)
    .AsAIAgent(
        model: model,
        instructions:
            "You are the Trip Disruption Concierge. Provide concise, direct answers.");

Console.ForegroundColor = ConsoleColor.Green;
Console.WriteLine(
    $"[Agent] {(await agentDefault.RunAsync(
        "My flight AU123 was cancelled with 3 hours' notice. What should I do first?")).Text}");
Console.ResetColor();
Console.WriteLine();

// ── Strategy 2: ChainedTokenCredential (recommended pattern) ─────────────────
// ChainedTokenCredential tries credentials in the order you specify, stopping
// at the first success.
//
// ManagedIdentityCredential → works on Azure (Container Apps, AKS, VMs).
// AzureCliCredential         → falls back to `az login` on developer laptops.
//
// This two-step chain is the recommended pattern for agent applications because:
//   - It is explicit: you control exactly which credentials are attempted.
//   - It works without code changes across dev and production.
//   - ManagedIdentityCredential fails fast when no identity is assigned, so the
//     fallback to AzureCliCredential adds negligible latency on dev machines.
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Auth] Strategy 2: ChainedTokenCredential (ManagedIdentity → AzureCLI)");
Console.WriteLine("[Auth] On Azure: uses managed identity (Entra Agent Identity for Hosted Agents).");
Console.WriteLine("[Auth] On dev:   falls through to az login session.");
Console.ResetColor();
Console.WriteLine();

var chainedCredential = new ChainedTokenCredential(
    new ManagedIdentityCredential(),
    new AzureCliCredential());

AIAgent agentChained = new AIProjectClient(new Uri(endpoint), chainedCredential)
    .AsAIAgent(
        model: model,
        instructions:
            "You are the Trip Disruption Concierge. Provide concise, direct answers.");

Console.ForegroundColor = ConsoleColor.Green;
Console.WriteLine(
    $"[Agent] {(await agentChained.RunAsync(
        "What compensation am I entitled to for a cancellation with only 3 hours' notice?")).Text}");
Console.ResetColor();
Console.WriteLine();

// ── Entra Agent Identity (informational) ─────────────────────────────────────
// When you deploy an agent to Azure AI Foundry as a Hosted Agent, the platform
// automatically provisions a system-assigned managed identity for the Container
// App that runs your agent code (the web service from Module 10).
//
// That identity is granted:
//   - Azure AI Foundry User (to call models)
//   - Search Index Data Reader (if a vector store is attached)
//
// You do not manage secrets or rotate credentials.  The ChainedTokenCredential
// above uses that identity transparently when running in Foundry.
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Auth] Entra Agent Identity: automatically provisioned by Foundry when");
Console.WriteLine("[Auth] deploying a Hosted Agent. No secrets to manage in production.");
Console.ResetColor();
Console.WriteLine();

Console.WriteLine("Module 11 complete. ✓");
