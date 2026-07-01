# 12. Observability & Tracing

**Estimated time:** 25 minutes

![Microsoft Agent Framework overview: an open-source engine for building and orchestrating AI agents, summarised in five pillars - Unified SDK (AIAgent, AgentThread, and AgentTool primitives built on Microsoft.Extensions.AI), Local-first and cloud-agnostic (run agents locally then move the same code to Foundry Agent Service or any cloud containers), Multi-agent orchestration (sequential, concurrent, handoff, group chat, magentic, and workflow patterns), Tools and extensibility (out-of-the-box integrations plus functions, APIs, and MCP servers as tools), and Enterprise-grade foundations (approval flows, content-policy hooks, OpenTelemetry observability, and long-running execution).](../../../docs/assets/diagrams/agent-framework-introduction.png)

> [!IMPORTANT]
> This module requires **Docker** to run the Aspire Dashboard container. Confirm Docker is running before you start. See the [Attendee Guide](../../../docs/guide-attendee.md) for Docker installation instructions.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Set up an OTLP trace exporter in a .NET console application.
- Enable the Microsoft Agent Framework's built-in OpenTelemetry instrumentation.
- Run the Aspire Dashboard as a standalone Docker container.
- Observe agent runs, tool calls, and model interactions as trace spans.

## Concepts

### OpenTelemetry and the OTLP exporter

**[OpenTelemetry](https://opentelemetry.io/)** is the industry standard for collecting distributed traces, metrics, and logs. The .NET SDK ships a built-in tracer provider and the `OpenTelemetry.Exporter.OpenTelemetryProtocol` package sends telemetry to any OTLP-compatible backend.

For the Microsoft Agent Framework, you add the tracer provider and enable agent instrumentation:

```csharp
using var tracerProvider = Sdk.CreateTracerProviderBuilder()
    .AddOtlpExporter()
    .Build();

var agent = client
    .AsAIAgent(model: model, instructions: "...")
    .AsBuilder()
    .UseOpenTelemetry()
    .Build();
```

Each agent run, tool call, and model response becomes a span in the trace.

### Aspire Dashboard

The **[.NET Aspire Dashboard](https://learn.microsoft.com/dotnet/aspire/fundamentals/dashboard/standalone)** is a standalone OpenTelemetry viewer that runs in Docker. You do not need a full Aspire application to use it - any OTLP source works:

```bash
docker run --rm -it -p 18888:18888 -p 4317:18889 \
  mcr.microsoft.com/dotnet/aspire-dashboard:latest
```

Open `http://localhost:18888` in a browser to see traces, logs, and metrics.

### What you will see

After running the module, the Aspire Dashboard Traces view shows one trace per `RunAsync` call. Each trace contains spans for:

- The overall agent run.
- Each model call (LLM inference).
- Each tool call, if function tools are attached.

## Steps

### Part 1 - Start the Aspire Dashboard

#### 1. Start the dashboard container

- [ ] In a terminal, run:

  ```bash
  docker run --rm -it -p 18888:18888 -p 4317:18889 \
    mcr.microsoft.com/dotnet/aspire-dashboard:latest
  ```

- [ ] Open `http://localhost:18888` in a browser and confirm the dashboard loads.

  > [!NOTE]
  > Keep this terminal open. The dashboard must be running before you start the agent, or traces will fail to export.

### Part 2 - Complete the starter code

#### 2. Open the starter file

- [ ] Open `src/Program.cs` in the editor.

#### 3. Configure the OTLP trace provider (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  using var tracerProvider = Sdk.CreateTracerProviderBuilder()
      .AddOtlpExporter(otlp =>
      {
          otlp.Endpoint = new Uri(
              Environment.GetEnvironmentVariable("OTEL_EXPORTER_OTLP_ENDPOINT")
              ?? "http://localhost:4317");
      })
      .Build();

  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Telemetry] OTLP traces → http://localhost:4317");
  Console.ResetColor();
  Console.WriteLine();
  ```

#### 4. Enable OpenTelemetry on the agent (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
  var credential = new DefaultAzureCredential();
  var agent = new AIProjectClient(new Uri(endpoint), credential)
      .AsAIAgent(
          model: model,
          instructions:
              "You are the Trip Disruption Concierge. Be concise and practical.")
      .AsBuilder()
      .UseOpenTelemetry()
      .Build();
  ```

  `.AsBuilder().UseOpenTelemetry().Build()` registers the framework's built-in instrumentation, which emits a span for every agent run, model call, and tool invocation.

#### 5. Run a few queries to generate traces (TODO 3)

- [ ] Locate `// ── TODO 3` and replace the commented-out block with the queries already commented out there.

### Part 3 - Run and verify

#### 6. Run the starter

- [ ] In a second terminal (keep the dashboard running), run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/12-observability/src/TripConcierge.Observability.csproj
  ```

#### 7. Inspect traces in the dashboard

- [ ] Refresh the Aspire Dashboard Traces view at `http://localhost:18888`.
- [ ] Confirm at least one trace appears, corresponding to each `RunAsync` call.
- [ ] Click a trace to expand its spans and see the model call and any tool calls.

## Validation

- At least one trace appears in the Aspire Dashboard after running the module.
- Trace spans include model calls and (if function tools are active) tool invocations.
- The terminal confirms `[Telemetry] OTLP traces → http://localhost:4317`.

## Congratulations 🎉

You instrumented the Trip Disruption Concierge with OpenTelemetry and explored its traces in the Aspire Dashboard. Every agent run, model call, and tool invocation is now a traceable span - giving you the observability you need to debug and optimise agent behaviour in production.

You have completed all twelve modules of the **Introduction to Microsoft Agent Framework (.NET)** lab. You built a fully featured multi-agent travel assistant, adding capabilities module by module: single-turn responses, multi-turn sessions, function tools, MCP tools, knowledge bases, memory, session persistence, multi-agent orchestration, hosted deployment, authentication, and observability.

## Troubleshooting

| Symptom | Fix |
|---|---|
| No traces in Aspire Dashboard | Confirm Docker container is running and port 4317 is mapped correctly |
| `OTLP exporter failed` | Check `OTEL_EXPORTER_OTLP_ENDPOINT` in `.env`; default is `http://localhost:4317` |
| App Insights traces missing | Set `APPLICATIONINSIGHTS_CONNECTION_STRING` in `.env` |
| `NotImplementedException` | A TODO is still incomplete |
