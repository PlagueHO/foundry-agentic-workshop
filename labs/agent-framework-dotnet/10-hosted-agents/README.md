---
title: '10. Hosted Agents'
description: 'Complete this lab to hosted agents.'
lastUpdated: '2026-07-13'
track: 'agent-framework-dotnet'
module: 10
slug: '10-hosted-agents'
estimatedTimeMinutes: 30
difficulty: 'intermediate'
prerequisites: ['Module 09']
audience:
  - 'attendee'
technologies:
  - 'Microsoft Agent Framework'
  - 'Microsoft Foundry'
tags:
  - 'agent-framework'
  - 'hosted'
  - 'agents'
status: 'active'
contentType: 'lab'
---
# 10. Hosted Agents

**Estimated time:** 30 minutes

![Microsoft Agent Framework local-first, cloud-agnostic diagram: an agent is built and run locally in development, then the same code moves to Foundry Agent Service or any cloud container without changes. The local-first model lets you see every turn in your terminal before deploying.](../../../docs/assets/diagrams/agent-framework-local-first-cloud-agnostic.png)

> [!IMPORTANT]
> This module builds on [Module 02](../02-first-agent/README.md). The `AIAgent` you build here is the same as in Module 02, but wrapped in an ASP.NET Core host and then deployed to Azure AI Foundry as a source-code hosted agent.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Add the `Microsoft.Agents.AI.Foundry.Hosting` package.
- Register agent services with `builder.Services.AddFoundryResponses(agent)`.
- Map the Foundry Responses endpoint with `app.MapFoundryResponses()`.
- Run the agent locally and confirm it responds to HTTP requests.
- Configure `AgentAdministrationClient` with a `FeaturePolicy` for the preview API.
- Deploy the agent from source code to Foundry using `CreateAgentVersionFromCode` with `remote_build` dependency resolution.
- Poll the deployment lifecycle until the agent version reaches `active`.
- Verify the hosted agent in the Foundry portal.

## Concepts

### Foundry Hosted Agents

A Hosted Agent is a web service that exposes the [Microsoft Foundry Responses API](https://learn.microsoft.com/azure/ai-foundry/agents/overview). When you deploy your agent to Foundry, it calls your `/api/responses` endpoint. Any agent you have already built with `AIAgent` can be turned into a hosted service with two lines:

```csharp
builder.Services.AddFoundryResponses(agent);   // register
app.MapFoundryResponses();                      // map route
```

### Source-code deployment

The [source-code deployment path](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/deploy-hosted-agent-code?tabs=csharp) lets you upload a folder of .NET project sources directly to Foundry - no local Docker build required. You choose a dependency-resolution mode:

| Mode | Behaviour | When to use |
|---|---|---|
| `remote_build` | Foundry runs `dotnet restore` and `dotnet publish` during provisioning | Small uploads, first deployments |
| `bundled` | You ship `dotnet publish` output; Foundry runs it as-is | Reproducible builds, private dependencies |

This module uses `remote_build`. Foundry compiles the source, runs the container, and serves your agent on a managed HTTPS endpoint.

### AgentAdministrationClient

`AgentAdministrationClient` (from `Azure.AI.Projects.Agents`) manages the full lifecycle of hosted agents - create, update, poll status, download, and delete. It is separate from `AIProjectClient`: `AIProjectClient` builds and runs agents locally; `AgentAdministrationClient` deploys them to the cloud.

### FeaturePolicy

Source-code deployment is in preview. Every HTTP request to the management API must include the `Foundry-Features: HostedAgents=V1Preview,CodeAgents=V1Preview` header. You attach a custom `PipelinePolicy` to `AgentAdministrationClientOptions` to inject it automatically:

```csharp
var options = new AgentAdministrationClientOptions();
options.AddPolicy(
    new FeaturePolicy("HostedAgents=V1Preview,CodeAgents=V1Preview"),
    PipelinePosition.PerCall);
```

### Deployment lifecycle

Every source-code deployment follows the same sequence: package → create → poll → active.

| Status | Meaning |
|---|---|
| `creating` | Foundry is restoring and building the source |
| `active` | Ready to receive requests |
| `failed` | Build or startup error - inspect `error.message` for the cause |

### Project SDK

Module 10 uses `Microsoft.NET.Sdk.Web` instead of the standard console SDK so that the Kestrel web server is available. The rest of the agent code is identical to the console modules.

### Local-first development

Because the agent logic runs locally before you deploy, you can test the full HTTP request-response cycle without touching Azure. Run it with `dotnet run` and send requests with `curl` to confirm everything works before deploying to Foundry.

## Steps

### Part 1 - Complete the starter code

#### 1. Open the starter file

- [ ] Open `src/Program.cs` in the editor.

#### 2. Build the AIAgent (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  AIAgent agent = new AIProjectClient(new Uri(endpoint), credential)
      .AsAIAgent(
          model: model,
          name: agentName,
          instructions:
              "You are the Trip Disruption Concierge, a helpful assistant " +
              "for passengers experiencing flight delays or cancellations. " +
              "Help passengers understand their rights and next steps.",
          description:
              "Helps passengers with flight disruption questions and compensation claims.");
  ```

  The `name` and `description` fields are surfaced as agent metadata in the Foundry portal when the hosted agent is deployed.

#### 3. Register the Foundry Responses services (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
  builder.Services.AddFoundryResponses(agent);
  ```

  This registers the agent and wires the Foundry Responses middleware into ASP.NET Core's dependency injection container.

#### 4. Map the endpoint and start the server (TODO 3)

- [ ] Locate `// ── TODO 3` and replace the commented-out block with:

  ```csharp
  app.MapFoundryResponses();
  app.Run();
  ```

  `MapFoundryResponses()` registers the `/api/responses` route that Foundry uses to call your agent. `app.Run()` starts Kestrel.

### Part 2 - Run and verify locally

#### 5. Run the starter

- [ ] In a terminal, run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/10-hosted-agents/src/TripConcierge.HostedAgent.csproj
  ```

- [ ] Confirm the process starts without errors and logs `Now listening on: http://localhost:5000`.

#### 6. Verify the agent endpoint

- [ ] In a second terminal, send a request to the agent metadata endpoint:

  ```bash
  curl -s http://localhost:5000/
  ```

- [ ] Confirm the response includes `"name"` and `"description"` fields matching the agent configuration from TODO 1.

### Part 3 - Deploy to Foundry from source code

> [!NOTE]
> Source-code deployment for Hosted agents is in **preview**. The `AAIP001` experimental-feature warning is suppressed at the top of the deploy program file.

#### 7. Open the deploy starter file

- [ ] Open `deploy-src/Program.cs` in the editor.

#### 8. Create the AgentAdministrationClient (TODO 4)

- [ ] Locate `// ── TODO 4` and replace the commented-out block with:

  ```csharp
  var options = new AgentAdministrationClientOptions();
  options.AddPolicy(
      new FeaturePolicy("HostedAgents=V1Preview,CodeAgents=V1Preview"),
      PipelinePosition.PerCall);

  var agentsClient = new AgentAdministrationClient(
      endpoint: new Uri(endpoint),
      tokenProvider: new DefaultAzureCredential(),
      options: options);
  ```

  `FeaturePolicy` (defined at the bottom of the file) injects the `Foundry-Features` preview header on every outgoing request.

#### 9. Define and deploy the agent from source code (TODO 5)

- [ ] Locate `// ── TODO 5` and replace the commented-out block with:

  ```csharp
  var agentDefinition = new HostedAgentDefinition(cpu: "1", memory: "2Gi")
  {
      Versions = { new ProtocolVersionRecord(ProjectsAgentProtocol.Responses, "1.0.0") },
      CodeConfiguration = new CodeConfiguration(
          runtime: "dotnet_10",
          entryPoint: ["dotnet", "TripConcierge.HostedAgent.dll"],
          dependencyResolution: CodeDependencyResolution.RemoteBuild),
  };

  var metadata = new CreateAgentVersionFromCodeMetadata(agentDefinition);

  Console.WriteLine($"Deploying {agentName} from source code ...");
  ProjectsAgentVersion agentVersion = agentsClient.CreateAgentVersionFromCode(
      agentName: agentName,
      filePath: "./labs/agent-framework-dotnet/10-hosted-agents/solution",
      metadata: metadata);
  Console.WriteLine($"Created version: {agentVersion.Version}  status: {agentVersion.Status}");
  ```

  `CreateAgentVersionFromCode` zips the folder at `filePath`, uploads it, and starts a remote `dotnet restore` + `dotnet publish`. The `entryPoint` matches the DLL name produced by that publish step.

#### 10. Poll for active status (TODO 6)

- [ ] Locate `// ── TODO 6` and replace the commented-out block with:

  ```csharp
  while (agentVersion.Status != AgentVersionStatus.Active &&
         agentVersion.Status != AgentVersionStatus.Failed)
  {
      Thread.Sleep(5_000);
      agentVersion = agentsClient.GetAgentVersion(
          agentName: agentVersion.Name,
          agentVersion: agentVersion.Version);
      Console.WriteLine($"  Status: {agentVersion.Status}");
  }

  if (agentVersion.Status != AgentVersionStatus.Active)
      throw new InvalidOperationException($"Deployment failed - status: {agentVersion.Status}");

  Console.WriteLine($"Agent {agentName} v{agentVersion.Version} is active and ready.");
  ```

- [ ] Remove the `throw new NotImplementedException(...)` line once all three TODOs are complete.

#### 11. Run the deploy program

- [ ] From the **repository root**, run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/10-hosted-agents/deploy-src/TripConcierge.Deploy.csproj
  ```

  > [!TIP]
  > If you get stuck, run the reference implementation instead:
  >
  > ```bash
  > dotnet run --project labs/agent-framework-dotnet/10-hosted-agents/deploy-solution/TripConcierge.Deploy.csproj
  > ```

- [ ] Confirm the output includes `Created version:` followed by status lines, then `Agent ... is active and ready.`

  > [!NOTE]
  > The remote build typically takes 2–5 minutes. Status cycles through `creating` before reaching `active`. If status shows `failed`, check the Foundry portal for the `error.message` on the failed version.

#### 12. Verify in the Foundry portal

- [ ] Open the [Foundry portal](https://ai.azure.com) and navigate to **Agents** in your project.
- [ ] Confirm `trip-disruption-concierge` (or the value of your `HOSTED_AGENT_NAME` variable) appears with **Kind: hosted** and an active version selected.

  <details>
  <summary>📸 Screenshot: Agents list showing the hosted agent</summary>

  ![Foundry portal Agents list showing trip-disruption-concierge as a hosted agent with an active version](../../../docs/assets/screenshots/introduction-foundry-agent-service/lab-09/01-agents-list-hosted-agent.png)

  </details>

## Validation

- The process starts without errors and logs `Now listening on: http://localhost:5000`.
- `GET http://localhost:5000/` returns agent metadata JSON including `name` and `description`.
- The deploy program prints `Created version:` and a status sequence ending with `is active and ready.`
- The Foundry portal shows the agent with **Kind: hosted** and an active version.

## Congratulations 🎉

You packaged the Trip Disruption Concierge as an ASP.NET Core web service, ran it locally, and deployed it to Azure AI Foundry as a source-code hosted agent using `AgentAdministrationClient`. The same agent code that ran in a console now runs as a fully managed HTTPS endpoint in the cloud.

> [!TIP]
> **Next up → [Module 11: Agent Identity & Auth](../11-agent-auth/README.md)**
> Learn how agent applications authenticate to Azure AI Foundry across the full deployment lifecycle - from local development to production Hosted Agents.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Port 5000 already in use | Set `ASPNETCORE_URLS=http://localhost:5001` in your shell before `dotnet run` |
| `401 Unauthorized` from Foundry | Run `az login` to refresh your credentials |
| `NotImplementedException` | A TODO is still incomplete - check all TODO blocks in `src/Program.cs` or `deploy-src/Program.cs` |
| `FOUNDRY_PROJECT_ENDPOINT is not set` | Copy `shared/.env.example` to `.env` at the repository root and fill in your project endpoint |
| Deploy status stuck in `creating` (> 10 min) | Server-side build may have failed; check the version's `error.message` in the Foundry portal |
| Deploy status `failed` | Open the Foundry portal, click the agent version, and read `error.message` - it contains the NuGet restore or publish error |
| `403 Forbidden` during deploy | Your account needs the **Foundry Project Manager** role at project scope to create hosted agents |
| `409 conflict` (agent already exists) | Re-running the deploy program will create a new version of the existing agent automatically |
