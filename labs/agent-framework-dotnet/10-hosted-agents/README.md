# 10. Hosted Agents

**Estimated time:** 20 minutes

![Microsoft Agent Framework local-first, cloud-agnostic diagram: an agent is built and run locally in development, then the same code moves to Foundry Agent Service or any cloud container without changes. The local-first model lets you see every turn in your terminal before deploying.](../../../docs/assets/diagrams/agent-framework-local-first-cloud-agnostic.png)

> [!IMPORTANT]
> This module builds on [Module 02](../02-first-agent/README.md). The `AIAgent` you build here is the same as in Module 02, but wrapped in an ASP.NET Core host instead of a console app.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Add the `Microsoft.Agents.AI.Foundry.Hosting` package.
- Register agent services with `builder.Services.AddFoundryResponses(agent)`.
- Map the Foundry Responses endpoint with `app.MapFoundryResponses()`.
- Run the agent locally and confirm it responds to HTTP requests.
- Understand how this is the host that Foundry deploys when you use the Hosted Agent feature.

## Concepts

### Foundry Hosted Agents

A Hosted Agent is a web service that exposes the [Azure AI Foundry Responses API](https://learn.microsoft.com/azure/ai-foundry/agents/overview). When you deploy your agent to Foundry, it calls your `/api/responses` endpoint. Any agent you have already built with `AIAgent` can be turned into a hosted service with two lines:

```csharp
builder.Services.AddFoundryResponses(agent);   // register
app.MapFoundryResponses();                      // map route
```

### Project SDK

Module 10 uses `Microsoft.NET.Sdk.Web` instead of the standard console SDK so that the Kestrel web server is available. The rest of the agent code is identical to the console modules.

### Local-first development

Because the agent logic runs locally before you deploy, you can test the full HTTP request-response cycle without touching Azure. Run it with `dotnet run` and send requests with `curl` to confirm everything works before deploying to Foundry.

## Steps

### Part 1 — Complete the starter code

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

### Part 2 — Run and verify locally

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

## Validation

- The process starts without errors and logs `Now listening on: http://localhost:5000`.
- `GET http://localhost:5000/` returns agent metadata JSON including `name` and `description`.
- The service can be deployed as a Foundry Hosted Agent using the pattern from [Module 09 (Python)](../../introduction-foundry-agent-service/09-hosted-agents/README.md) as a reference.

## Congratulations 🎉

You packaged the Trip Disruption Concierge as an ASP.NET Core web service that exposes the standard Foundry Responses API. The same agent code that ran in a console now runs as an HTTP endpoint — ready to be deployed to Azure AI Foundry as a Hosted Agent.

> [!TIP]
> **Next up → [Module 11: Agent Identity & Auth](../11-agent-auth/README.md)**
> Learn how agent applications authenticate to Azure AI Foundry across the full deployment lifecycle — from local development to production Hosted Agents.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Port 5000 already in use | Set `ASPNETCORE_URLS=http://localhost:5001` in your shell before `dotnet run` |
| `401 Unauthorized` from Foundry | Run `az login` to refresh your credentials |
| `NotImplementedException` | A TODO is still incomplete |
