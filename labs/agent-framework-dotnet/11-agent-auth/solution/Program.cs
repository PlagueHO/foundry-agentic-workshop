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
Console.WriteLine("Comparing Azure credential strategies for agent applications.");
Console.ResetColor();
Console.WriteLine();

// ── Strategy 1: AzureCliCredential ────────────────────────────────────────────
// AzureCliCredential authenticates using the active az login session.
// This is the explicit, dev-only credential every prior module has used.
//
// Best for: developer laptops where az login has been run.
// Trade-off: not available in production (no Azure CLI on Container Apps or AKS).
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Auth] Strategy 1: AzureCliCredential");
Console.WriteLine("[Auth] Uses the active az login session on this machine.");
Console.ResetColor();
Console.WriteLine();

var cliCredential = new AzureCliCredential();

AIAgent agentCli = new AIProjectClient(new Uri(endpoint), cliCredential)
    .AsAIAgent(
        model: model,
        instructions: "You are the Trip Disruption Concierge. Be concise.");

Console.ForegroundColor = ConsoleColor.Green;
Console.WriteLine(
    $"[Agent] {(await agentCli.RunAsync(
        "My flight AU123 was cancelled. What is the first thing I should do?")).Text}");
Console.ResetColor();
Console.WriteLine();

// ── Strategy 2: ChainedTokenCredential ──────────────────────────────────────
// ChainedTokenCredential tries credentials in the order you specify, stopping
// at the first success.
//
// WorkloadIdentityCredential → OIDC federation (GitHub Actions, AKS workload identity).
//   Throws CredentialUnavailableException immediately when AZURE_CLIENT_ID /
//   AZURE_TENANT_ID / AZURE_FEDERATED_TOKEN_FILE are not set — so on a dev
//   laptop the chain falls through to AzureCliCredential with no delay.
// AzureCliCredential         → falls back to `az login` on developer laptops.
//
// For a production Hosted Agent (Module 10), swap WorkloadIdentityCredential
// for ManagedIdentityCredential(ManagedIdentityId.SystemAssigned) — Foundry
// provisions the managed identity automatically and IMDS is always reachable.
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Auth] Strategy 2: ChainedTokenCredential (WorkloadIdentity → AzureCLI)");
Console.WriteLine("[Auth] In CI/CD: uses OIDC WorkloadIdentityCredential.");
Console.WriteLine("[Auth] On dev:   WorkloadIdentity unavailable, falls through to az login.");
Console.ResetColor();
Console.WriteLine();

var chainedCredential = new ChainedTokenCredential(
    new WorkloadIdentityCredential(),   // CI/CD with OIDC — throws CredentialUnavailableException fast on dev
    new AzureCliCredential());

AIAgent agentChained = new AIProjectClient(new Uri(endpoint), chainedCredential)
    .AsAIAgent(
        model: model,
        instructions: "You are the Trip Disruption Concierge. Be concise.");

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
