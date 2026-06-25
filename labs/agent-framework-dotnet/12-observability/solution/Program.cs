using System.Diagnostics;
using Azure.Identity;
using Azure.AI.Projects;
using Azure.Monitor.OpenTelemetry.Exporter;
using DotNetEnv;
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

Console.WriteLine("=== Trip Disruption Concierge — Module 12: Observability & Tracing ===");
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"  Model : {model}");
Console.ResetColor();
Console.WriteLine();

// ── Configure OpenTelemetry ───────────────────────────────────────────────────
// `using var` ensures the provider is flushed when the program exits.
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Telemetry] Configuring trace provider...");
Console.ResetColor();

var traceBuilder = Sdk.CreateTracerProviderBuilder()
    .AddSource("Microsoft.Agents.*")         // Agent Framework spans
    .AddSource("TripConcierge.*")            // Any custom spans you add later
    .AddOtlpExporter(opts =>
    {
        opts.Endpoint = new Uri(otlpEndpoint);
        opts.Protocol = OtlpExportProtocol.Grpc;
    });

if (!string.IsNullOrEmpty(appInsightsConnStr))
{
    traceBuilder.AddAzureMonitorTraceExporter(opts =>
        opts.ConnectionString = appInsightsConnStr);

    Console.ForegroundColor = ConsoleColor.DarkGray;
    Console.WriteLine("[Telemetry] Azure Monitor (Application Insights) exporter active.");
    Console.ResetColor();
}

using var tracerProvider = traceBuilder.Build();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"[Telemetry] OTLP traces → {otlpEndpoint}");
Console.WriteLine("[Telemetry] Aspire Dashboard → http://localhost:18888");
Console.ResetColor();
Console.WriteLine();

// ── Create agent with OTel instrumentation ────────────────────────────────────
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Creating agent with OpenTelemetry instrumentation...");
Console.ResetColor();

var credential = new AzureCliCredential();
var client = new AIProjectClient(new Uri(endpoint), credential);

var agent = client
    .AsAIAgent(
        model: model,
        instructions:
            "You are the Trip Disruption Concierge. " +
            "Help passengers with flight disruptions concisely.")
    .WithOpenTelemetry();  // Enables AF's built-in instrumentation

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Agent ready — every RunAsync call will produce a trace span.");
Console.ResetColor();
Console.WriteLine();
Console.WriteLine("Open http://localhost:18888 in a browser to see traces.");
Console.WriteLine();

// ── Run queries — each produces a trace ───────────────────────────────────────
var queries = new[]
{
    "My flight AKL→SYD was cancelled with only 3 hours' notice. What are my rights?",
    "My ticket cost AUD 420 and I had 3 hours' notice. How much compensation can I claim?",
};

int queryNumber = 0;

foreach (var query in queries)
{
    queryNumber++;
    Console.WriteLine($"─── Query {queryNumber} {'─',68}");
    Console.WriteLine();

    Console.ForegroundColor = ConsoleColor.Cyan;
    Console.WriteLine($"[User] {query}");
    Console.ResetColor();
    Console.WriteLine();

    Console.ForegroundColor = ConsoleColor.DarkGray;
    Console.Write($"[Loop] RunAsync (trace {queryNumber})...");
    Console.ResetColor();

    var sw = Stopwatch.StartNew();
    var result = await agent.RunAsync(query);
    sw.Stop();

    Console.ForegroundColor = ConsoleColor.DarkGray;
    Console.WriteLine($" done ({sw.ElapsedMilliseconds} ms)");
    Console.ResetColor();
    Console.WriteLine();

    Console.ForegroundColor = ConsoleColor.Green;
    Console.WriteLine($"[Agent] {result.Text}");
    Console.ResetColor();
    Console.WriteLine();
}

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Telemetry] Flushing traces...");
Console.ResetColor();

// tracerProvider disposes here via `using var` — flushes all pending spans.
Console.WriteLine();
Console.WriteLine("Refresh the Aspire Dashboard Traces view to see the spans.");
Console.WriteLine();
Console.WriteLine("Module 12 complete. ✓");
