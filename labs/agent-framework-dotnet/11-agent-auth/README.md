# 11. Agent Identity & Auth

**Estimated time:** 35 minutes

![Anatomy of a Foundry agent identity: a sample identity card listing its four attributes - Agent ID (a unique identifier for each agent identity), Agent name (the name shown when the agent is used), Sponsor (the human user responsible for the agent), and Blueprint (the reusable template the identity is created from).](../../../docs/assets/diagrams/agent-identity-anatomy.png)

> [!IMPORTANT]
> This module builds on [Module 02](../02-first-agent/README.md) and [Module 10](../10-hosted-agents/README.md). Part 1 explains the credential strategies you have used since Module 02. Part 2 connects to a server-side agent named `trip-concierge-storage` that your organizer provisioned during `azd provision`, so it can reach Azure Storage as its own agent identity. Your `.env` must contain `FOUNDRY_PROJECT_ENDPOINT` and `AGENT_NAME_STORAGE` - see [Module 01](../01-setup/README.md) or copy `shared/.env.example`.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Compare `AzureCliCredential` and `ChainedTokenCredential` as the dev-to-production pattern for authenticating **your code** to Foundry.
- Understand the Foundry agent object model and the Entra **agent identity** every agent receives at creation.
- Distinguish the **unattended** (application-only) and **attended** (on-behalf-of) agent identity flows.
- Connect Agent Framework to a server-side agent and watch it reach Azure Storage as its **own** agent identity - no user, no secrets.

## Concepts

### Credential types

| Credential | Where it works | How it authenticates |
|---|---|---|
| `AzureCliCredential` | Developer laptop | `az login` session |
| `ManagedIdentityCredential` | Azure VM, Container App, AKS | Assigned managed identity |
| `WorkloadIdentityCredential` | GitHub Actions, AKS | OIDC federation |
| `DefaultAzureCredential` | Anywhere (tries a chain) | Falls through a preset list |

### Entra agent identity

There are two different identities in this module, and keeping them apart is the key insight:

- **Your identity** authenticates _your code_ to Foundry when you build or invoke an agent. That is what the credential strategies above (Part 1) are about.
- The **agent identity** authenticates _the agent_ to downstream services when it calls a tool. In the current Foundry object model, every agent receives its **own** Entra service principal - its `instance_identity` - the moment it is created. You never see or manage a secret for it.

Because the agent identity is created _with_ the agent, its RBAC roles can only be assigned _after_ the agent exists. In this workshop your organizer's provisioning step creates the `trip-concierge-storage` agent and grants its identity **Storage Blob Data Contributor** on the demo storage account.

### Unattended vs attended

Agent identities support two authentication flows:

| Flow | OAuth grant | Who acts | Governed by |
|---|---|---|---|
| **Unattended** (application-only) | Client credentials | The agent, under its own authority | The agent identity's own RBAC roles |
| **Attended** (on-behalf-of) | On-behalf-of (OBO) | The agent, on behalf of a signed-in user | The user's delegated permissions |

This module demonstrates the **unattended** flow against Azure Storage. The attended flow maps to Foundry's [OAuth identity passthrough](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/mcp-authentication) for MCP tools, where each user signs in once and the agent acts with that user's permissions.

### How the unattended flow reaches Azure Storage

Agent identity authentication is available for **MCP** and **A2A** tools, so the agent reaches Azure Storage _through_ an MCP server. The `trip-concierge-storage` agent has an MCP tool bound to a **project connection** whose authentication type is `AgenticIdentityToken` and whose **audience** is `https://storage.azure.com`. When the agent calls the tool:

1. Agent Service exchanges the agent's `instance_identity` for an access token scoped to the Storage audience.
1. It passes that token to the **Blob Relay** MCP server (an Azure Container App).
1. The relay forwards the token straight to the Azure Blob REST API - it is a thin passthrough that holds no credentials of its own and is pinned to a single storage account and container.
1. Storage validates the token and checks the **agent identity's** RBAC role.

Your code never handles a token. For more information, see [Agent identity concepts](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/agent-identity) on Microsoft Learn.

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

For an overview of the framework, see [Microsoft Agent Framework overview](https://learn.microsoft.com/en-us/agent-framework/overview/). For more information on credential chains and agent identity, see [Credential chains in the Azure Identity client library](https://learn.microsoft.com/en-us/dotnet/azure/sdk/authentication/credential-chains) and [Agent identity and authorization](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/agent-identity) on Microsoft Learn.

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

  The `model` variable is read from the `AGENT_MODEL` environment variable (defaulting to `chat`).

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

### Part 3 - Reach Azure Storage as the agent identity

#### 4. Connect to the storage agent and invoke it (TODO 3)

The `trip-concierge-storage` agent already exists server-side - your organizer provisioned it with the `AgenticIdentityToken` MCP connection and granted its identity the Storage role. You connect to it by name via `AIProjectClient.AgentAdministrationClient.GetAgentAsync(...)` and then wrap it as an `AIAgent`; the whole agent loop, including the token exchange, runs in Agent Service.

- [ ] Locate `// ── TODO 3` and replace the commented-out block with:

  ```csharp
  var storageAgentName = Environment.GetEnvironmentVariable("AGENT_NAME_STORAGE")
      ?? "trip-concierge-storage";

  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine($"[Auth] Part 3: connecting to server-side agent '{storageAgentName}' (unattended identity).");
  Console.ResetColor();
  Console.WriteLine();

  var projectClient = new AIProjectClient(new Uri(endpoint), new AzureCliCredential());
  var storageAgentRecord = await projectClient.AgentAdministrationClient.GetAgentAsync(storageAgentName);
  AIAgent storageAgent = projectClient.AsAIAgent(storageAgentRecord);

  Console.ForegroundColor = ConsoleColor.Green;
  Console.WriteLine($"[Agent] {(await storageAgent.RunAsync(
      "Read the passenger case file 'welcome.txt' and summarise the entitlements it records.")).Text}");
  Console.ResetColor();
  Console.WriteLine();

  Console.WriteLine("Module 11 complete. ✓");
  ```

- [ ] Remove the `throw new NotImplementedException(...)` line once all three TODOs are complete.

  > [!NOTE]
  > `GetAgentAsync` retrieves the existing server-side agent (its latest version), and `AsAIAgent` wraps it as an `AIAgent` you can call. This is the connect-to-existing pattern, distinct from the `AsAIAgent(model, instructions)` calls in Parts 1 and 2 that define a fresh agent in your process.

### Part 4 - Run and verify

#### 5. Run the starter

- [ ] In a terminal, run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/11-agent-auth/src/TripConcierge.AgentAuth.csproj
  ```

  > [!TIP]
  > If you get stuck, run the reference implementation instead:
  >
  > ```bash
  > dotnet run --project labs/agent-framework-dotnet/11-agent-auth/solution/TripConcierge.AgentAuth.csproj
  > ```

## Validation

- The output shows `[Auth] Strategy 1: AzureCliCredential` and `[Auth] Strategy 2: ChainedTokenCredential (WorkloadIdentity → AzureCLI)` lines, both succeeding after `az login`.
- Part 3 connects to `trip-concierge-storage` and prints an `[Agent]` summary of the passenger case file, proving the agent read a blob from Azure Storage as its **own** identity.
- No tokens or secrets appear in the console output.

## Congratulations 🎉

You compared two credential strategies for authenticating your code to Foundry, then connected Agent Framework to a server-side agent and watched it reach Azure Storage as its **own** Entra agent identity - the unattended, application-only flow, with no user and no secrets. You now understand where the agent identity comes from, how it differs from your own credential, and how the `AgenticIdentityToken` connection routes a Storage-scoped token through an MCP server.

> [!TIP]
> **Next up → [Module 12: Observability & Tracing](../12-observability/README.md)**
> Instrument the agent with OpenTelemetry and visualise agent runs, tool calls, and model interactions as trace spans in the Aspire Dashboard.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `AuthenticationFailedException` with `AzureCliCredential` | Run `az login` and confirm with `az account show` that the correct subscription is active |
| `CredentialUnavailableException` with `ManagedIdentityCredential` | Expected on a dev laptop — ensure the `ChainedTokenCredential` fallback to `AzureCliCredential` is in place |
| `NotImplementedException` | A TODO is still incomplete |
| Agent `trip-concierge-storage` not found | The agent is provisioned by `azd provision` (the `provision-agent-identity-demo` postprovision step). Confirm provisioning completed and `AGENT_NAME_STORAGE` matches the provisioned name |
| Agent replies that Storage returned `403` | The agent identity's `Storage Blob Data Contributor` role assignment may still be propagating (allow a few minutes), or the demo storage account is unreachable — see the note below |
| Agent replies that Storage is unreachable | The Blob Relay reaches Storage over the public endpoint, so the demo storage account must allow public network access. Some subscriptions enforce private-only storage by policy; in that case the account needs a private endpoint reachable from the Container Apps environment |
