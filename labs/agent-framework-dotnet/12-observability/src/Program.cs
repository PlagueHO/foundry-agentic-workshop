using Azure.Identity;
using Azure.AI.Projects;
using DotNetEnv;
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Foundry;
using OpenTelemetry;
using OpenTelemetry.Exporter;
using OpenTelemetry.Trace;

Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var model = Environment.GetEnvironmentVariable("AGENT_MODEL") ?? "chat";
var otlpEndpoint = Environment.GetEnvironmentVariable("OTEL_EXPORTER_OTLP_ENDPOINT")
    ?? "http://localhost:4317";
var appInsightsConnStr = Environment.GetEnvironmentVariable("APPLICATIONINSIGHTS_CONNECTION_STRING");

Console.WriteLine("=== Trip Disruption Concierge - Module 12: Observability & Tracing ===");
Console.WriteLine();

// ── TODO 1 ───────────────────────────────────────────────────────────────────
// Configure an OpenTelemetry trace provider that exports to the Aspire Dashboard
// via OTLP. Optionally add the Azure Monitor exporter for App Insights.
//
// The `using var` ensures the provider is flushed and disposed at program end.
//
// var traceBuilder = Sdk.CreateTracerProviderBuilder()
//     .AddSource("Microsoft.Agents.*")
//     .AddOtlpExporter(opts =>
//     {
//         opts.Endpoint = new Uri(otlpEndpoint);
//         opts.Protocol = OtlpExportProtocol.Grpc;
//     });
//
// if (!string.IsNullOrEmpty(appInsightsConnStr))
// {
//     traceBuilder.AddAzureMonitorTraceExporter(opts =>
//         opts.ConnectionString = appInsightsConnStr);
//     Console.ForegroundColor = ConsoleColor.DarkGray;
//     Console.WriteLine("[Telemetry] Azure Monitor exporter configured.");
//     Console.ResetColor();
// }
//
// using var tracerProvider = traceBuilder.Build();
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine($"[Telemetry] OTLP traces → {otlpEndpoint}");
// Console.WriteLine("[Telemetry] Dashboard  → http://localhost:18888");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 2 ───────────────────────────────────────────────────────────────────
// Create the agent and enable built-in OTel instrumentation via the
// AIAgentBuilder fluent pattern's UseOpenTelemetry().
//
// var credential = new AzureCliCredential();
// var client = new AIProjectClient(new Uri(endpoint), credential);
// var agent = client
//     .AsAIAgent(
//         model: model,
//         instructions:
//             "You are the Trip Disruption Concierge. " +
//             "Help passengers with flight disruptions concisely.")
//     .AsBuilder()
//     .UseOpenTelemetry()
//     .Build();
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Loop] Agent created with OpenTelemetry instrumentation.");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 3 ───────────────────────────────────────────────────────────────────
// Run two queries. Each will produce a trace in the Aspire Dashboard.
// Open http://localhost:18888 in a browser and refresh the Traces view.
//
// foreach (var query in new[]
// {
//     "My flight AKL→SYD was cancelled. What are my rights?",
//     "My ticket cost AUD 420 and I had 3 hours' notice. How much compensation?",
// })
// {
//     Console.ForegroundColor = ConsoleColor.Cyan;
//     Console.WriteLine($"[User] {query}");
//     Console.ResetColor();
//     Console.WriteLine();
//
//     var result = await agent.RunAsync(query);
//
//     Console.ForegroundColor = ConsoleColor.Green;
//     Console.WriteLine($"[Agent] {result.Text}");
//     Console.ResetColor();
//     Console.WriteLine();
// }
//
// ─────────────────────────────────────────────────────────────────────────────

throw new NotImplementedException(
    "Complete the TODOs above, then remove this line and the throw statement.");
