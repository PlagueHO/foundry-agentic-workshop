# 11. Agent Identity & Auth

**Estimated time:** 20 minutes

![Microsoft Agent Framework overview: an open-source engine for building and orchestrating AI agents, summarised in five pillars - Unified SDK (AIAgent, AgentThread, and AgentTool primitives built on Microsoft.Extensions.AI), Local-first and cloud-agnostic (run agents locally then move the same code to Foundry Agent Service or any cloud containers), Multi-agent orchestration (sequential, concurrent, handoff, group chat, magentic, and workflow patterns), Tools and extensibility (out-of-the-box integrations plus functions, APIs, and MCP servers as tools), and Enterprise-grade foundations (approval flows, content-policy hooks, OpenTelemetry observability, and long-running execution).](../../../docs/assets/diagrams/agent-framework-introduction.png)

> [!IMPORTANT]
> This module builds on [Module 02](../02-first-agent/README.md). You should already be comfortable with `DefaultAzureCredential` from the earlier modules before exploring credential chaining here. Your `.env` file must contain `FOUNDRY_PROJECT_ENDPOINT` - see [Module 01](../01-setup/README.md) or copy `shared/.env.example`.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Compare `DefaultAzureCredential` and `ChainedTokenCredential` (combining `ManagedIdentityCredential` and `AzureCliCredential`) as the recommended dev-to-production pattern.
- Build a `ChainedTokenCredential` that works in both dev and production.
- Understand Entra Agent Identity - the service principal automatically assigned to every Azure AI Foundry Hosted Agent.
- Run the agent with each credential variant and observe which succeeds.

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
    new ManagedIdentityCredential(ManagedIdentityId.SystemAssigned),
    new AzureCliCredential());
```

For more information, see [Credential chains in the Azure Identity client library](https://learn.microsoft.com/en-us/dotnet/azure/sdk/authentication/credential-chains) and [Agent identity and authorization](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/agent-identity) on Microsoft Learn.

## Steps

### Part 1 - Use DefaultAzureCredential

#### 1. Open the starter file

- [ ] Open `src/Program.cs` in the editor.

#### 2. Create an agent with DefaultAzureCredential (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Auth] Strategy 1: DefaultAzureCredential");
  Console.ResetColor();

  var defaultCredential = new DefaultAzureCredential();
  AIAgent agentDefault = new AIProjectClient(new Uri(endpoint), defaultCredential)
      .AsAIAgent(
          model: model,
          instructions: "You are the Trip Disruption Concierge. Be concise.");

  Console.ForegroundColor = ConsoleColor.Green;
  Console.WriteLine($"[Agent] {(await agentDefault.RunAsync(
      "My flight AU123 was cancelled. What is the first thing I should do?")).Text}");
  Console.ResetColor();
  Console.WriteLine();
  ```

  > [!NOTE]
  > `DefaultAzureCredential` tries credential sources in order - environment variables, workload identity, managed identity, Azure Developer CLI, **Azure CLI**, VS Code, and PowerShell. On machines where VS Code is signed in to a different account, `DefaultAzureCredential` may resolve to that identity rather than your `az login` session. Run `az account show` to confirm which identity is active.

### Part 2 - Use a ChainedTokenCredential

#### 3. Create an agent with ChainedTokenCredential (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Auth] Strategy 2: ChainedTokenCredential " +
                    "(ManagedIdentity → AzureCLI)");
  Console.ResetColor();

  var chainedCredential = new ChainedTokenCredential(
      new ManagedIdentityCredential(ManagedIdentityId.SystemAssigned),
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
  > On a developer laptop, `ManagedIdentityCredential` is unavailable. The chain falls through to `AzureCliCredential` automatically - no code change is needed when you deploy to a managed-identity environment.

### Part 3 - Run and verify

#### 4. Run the starter

- [ ] In a terminal, run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/11-agent-auth/src/TripConcierge.AgentAuth.csproj
  ```

## Validation

- The output shows which credential variant was used (`[Auth]` lines).
- Both `DefaultAzureCredential` and `ChainedTokenCredential` succeed in making a model call on a developer laptop after `az login`.
- No tokens or secrets appear in the console output.

## Congratulations 🎉

You compared three Azure credential strategies and built the recommended `ChainedTokenCredential` pattern that works on a developer laptop and in a production Hosted Agent without any code changes. You also understand Entra Agent Identity and how Foundry provisions it automatically when you deploy.

> [!TIP]
> **Next up → [Module 12: Observability & Tracing](../12-observability/README.md)**
> Instrument the agent with OpenTelemetry and visualise agent runs, tool calls, and model interactions as trace spans in the Aspire Dashboard.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `AuthenticationFailedException` with `AzureCliCredential` | Run `az login` |
| HTTP 403 with `DefaultAzureCredential` | `DefaultAzureCredential` resolved to a VS Code or environment credential that lacks Foundry User access. Run `az login` and confirm with `az account show` that the correct identity is active. |
| `CredentialUnavailableException` with `ManagedIdentityCredential` | Expected on a dev laptop - ensure the `ChainedTokenCredential` fallback to `AzureCliCredential` is in place |
| `NotImplementedException` | A TODO is still incomplete |
