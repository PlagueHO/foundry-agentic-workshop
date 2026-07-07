# 11. Agent Identity & Auth

**Estimated time:** 20 minutes

![Microsoft Agent Framework overview: an open-source engine for building and orchestrating AI agents, summarised in five pillars - Unified SDK (AIAgent, AgentThread, and AgentTool primitives built on Microsoft.Extensions.AI), Local-first and cloud-agnostic (run agents locally then move the same code to Foundry Agent Service or any cloud containers), Multi-agent orchestration (sequential, concurrent, handoff, group chat, magentic, and workflow patterns), Tools and extensibility (out-of-the-box integrations plus functions, APIs, and MCP servers as tools), and Enterprise-grade foundations (approval flows, content-policy hooks, OpenTelemetry observability, and long-running execution).](../../../docs/assets/diagrams/agent-identity-anatomy.png)

> [!IMPORTANT]
> This module builds on [Module 02](../02-first-agent/README.md). You have used `AzureCliCredential` in every module since Module 02 — this module explains why, then shows the recommended production-ready upgrade. Your `.env` file must contain `FOUNDRY_PROJECT_ENDPOINT` - see [Module 01](../01-setup/README.md) or copy `shared/.env.example`.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Compare `AzureCliCredential` (explicit, dev-only) and `ChainedTokenCredential` (combining `ManagedIdentityCredential` and `AzureCliCredential`) as the recommended dev-to-production pattern.
- Build a `ChainedTokenCredential` that works on a developer laptop and in production without any code changes.
- Understand Entra Agent Identity - the service principal automatically assigned to every Azure AI Foundry Hosted Agent.
- Run the agent with each credential strategy and observe that both succeed on a developer laptop.

## Concepts

### Credential types

| Credential | Where it works | How it authenticates |
|---|---|---|
| `AzureCliCredential` | Developer laptop | `az login` session |
| `ManagedIdentityCredential` | Azure VM, Container App, AKS | Assigned managed identity |
| `WorkloadIdentityCredential` | GitHub Actions, AKS | OIDC federation |
| `DefaultAzureCredential` | Anywhere (tries a chain) | Falls through a preset list |

### Entra Agent Identity

When you deploy a Hosted Agent to Azure AI Foundry, the platform provisions a **system-assigned managed identity** for the Container App that runs your agent. That identity is granted the minimum Foundry roles needed for your agent to call the model and read the vector store. You do not need to manage secrets.

### Recommended pattern

```csharp
// Works on a developer laptop (AzureCliCredential) and in production
// (ManagedIdentityCredential), without changing any code:
var credential = new ChainedTokenCredential(
    new ManagedIdentityCredential(new ManagedIdentityCredentialOptions(ManagedIdentityId.SystemAssigned)
    {
        Retry = { MaxRetries = 0 }    // Fail fast on dev laptops; on Azure, IMDS responds immediately
    }),
    new AzureCliCredential());
```

For more information, see [Credential chains in the Azure Identity client library](https://learn.microsoft.com/en-us/dotnet/azure/sdk/authentication/credential-chains) and [Agent identity and authorization](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/agent-identity) on Microsoft Learn.

## Steps

### Part 1 - Use AzureCliCredential

#### 1. Open the starter file

- [ ] Open `src/Program.cs` in the editor.

#### 2. Create an agent with AzureCliCredential (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
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
  ```

### Part 2 - Use a ChainedTokenCredential

#### 3. Create an agent with ChainedTokenCredential (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Auth] Strategy 2: ChainedTokenCredential " +
                    "(WorkloadIdentity → AzureCLI)");
  Console.ResetColor();

  var chainedCredential = new ChainedTokenCredential(
      new WorkloadIdentityCredential(),   // CI/CD with OIDC (GitHub Actions, AKS) — fails fast on dev
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
  ```

  > [!NOTE]
  > `WorkloadIdentityCredential` throws `CredentialUnavailableException` immediately when `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_FEDERATED_TOKEN_FILE` are not set, which lets `ChainedTokenCredential` fall through to `AzureCliCredential` with no delay on your dev laptop. In a production **Hosted Agent** (Module 10), replace it with `ManagedIdentityCredential(ManagedIdentityId.SystemAssigned)` as shown in the Concepts section — Foundry provisions the managed identity automatically so IMDS is always reachable.

### Part 3 - Run and verify

#### 4. Run the starter

- [ ] In a terminal, run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/11-agent-auth/src/TripConcierge.AgentAuth.csproj
  ```

## Validation

- The output shows `[Auth] Strategy 1: AzureCliCredential` and `[Auth] Strategy 2: ChainedTokenCredential (WorkloadIdentity → AzureCLI)` lines.
- Both strategies succeed in making a model call on a developer laptop after `az login`.
- No tokens or secrets appear in the console output.

## Congratulations 🎉

You compared two credential strategies — the explicit `AzureCliCredential` used throughout this workshop and the production-ready `ChainedTokenCredential` — and built the recommended pattern that works on a developer laptop and in a production Hosted Agent without any code changes. You also understand Entra Agent Identity and how Foundry provisions it automatically when you deploy.

> [!TIP]
> **Next up → [Module 12: Observability & Tracing](../12-observability/README.md)**
> Instrument the agent with OpenTelemetry and visualise agent runs, tool calls, and model interactions as trace spans in the Aspire Dashboard.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `AuthenticationFailedException` with `AzureCliCredential` | Run `az login` and confirm with `az account show` that the correct subscription is active |
| `CredentialUnavailableException` with `ManagedIdentityCredential` | Expected on a dev laptop — ensure the `ChainedTokenCredential` fallback to `AzureCliCredential` is in place |
| `NotImplementedException` | A TODO is still incomplete |
