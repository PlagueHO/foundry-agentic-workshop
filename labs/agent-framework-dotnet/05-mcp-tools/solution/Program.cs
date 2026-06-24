using System.Diagnostics;
using Azure.Identity;
using Azure.AI.Projects;
using DotNetEnv;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using ModelContextProtocol.Client;

Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var model = Environment.GetEnvironmentVariable("AGENT_MODEL") ?? "chat";
var mcpUrl = Environment.GetEnvironmentVariable("FLIGHT_OPS_MCP_SERVER_URL")
    ?? "http://localhost:3001/mcp";

Console.WriteLine("=== Trip Disruption Concierge — Module 05: MCP Tools ===");
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"  Model      : {model}");
Console.WriteLine($"  MCP server : {mcpUrl}");
Console.ResetColor();
Console.WriteLine();

// ── Connect to flight-ops MCP server ─────────────────────────────────────────
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Connecting to flight-ops MCP server...");
Console.ResetColor();

await using var mcpClient = await McpClient.CreateAsync(
    new HttpClientTransport(new() { Endpoint = new Uri(mcpUrl), Name = "flight-ops" }));
IList<McpClientTool> mcpTools = await mcpClient.ListToolsAsync();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"[Loop] MCP tools discovered: {string.Join(", ", mcpTools.Select(t => t.Name))}");
Console.ResetColor();

// ── Create agent with MCP toolset ────────────────────────────────────────────
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Creating agent with MCP tools...");
Console.ResetColor();

var credential = new AzureCliCredential();
var client = new AIProjectClient(new Uri(endpoint), credential);

var agent = client
    .AsAIAgent(
        model: model,
        instructions:
            "You are the Trip Disruption Concierge. You have access to the " +
            "flight operations system via MCP tools. When passengers ask about " +
            "flight status or rebooking, call the appropriate tool to get live " +
            "data before responding. Always use the exact booking reference and " +
            "flight number the passenger provides.",
        tools: [.. mcpTools.Cast<AITool>()]);

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Agent ready — MCP tools available from flight-ops server.");
Console.ResetColor();
Console.WriteLine();

// ── Create session (preserves conversation history across turns) ──────────────
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Creating session...");
Console.ResetColor();

var session = await agent.CreateSessionAsync();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Session ready.");
Console.ResetColor();
Console.WriteLine();

// ── Run — agent calls MCP tools automatically ─────────────────────────────────
var query =
    "My flight AU123 has been disrupted. Can you check its current status " +
    "and find me the best rebooking option? My booking reference is BK98765, " +
    "travelling AKL to SYD.";

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine($"[User] {query}");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] RunAsync — agent will call MCP tools as needed...");
Console.ResetColor();
Console.WriteLine();

var sw = Stopwatch.StartNew();
var result = await agent.RunAsync(query, session: session);
sw.Stop();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"[Loop] RunAsync complete ({sw.ElapsedMilliseconds} ms)");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Green;
Console.WriteLine($"[Agent] {result.Text}");
Console.ResetColor();
Console.WriteLine();

// ── Second turn — file a compensation claim ────────────────────────────────────
var query2 =
    "Please go ahead and file a compensation claim for the cancellation.";

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine($"[User] {query2}");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] RunAsync starting...");
Console.ResetColor();
Console.WriteLine();

sw.Restart();
var result2 = await agent.RunAsync(query2, session: session);
sw.Stop();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"[Loop] RunAsync complete ({sw.ElapsedMilliseconds} ms)");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Green;
Console.WriteLine($"[Agent] {result2.Text}");
Console.ResetColor();
Console.WriteLine();

Console.WriteLine("Module 05 complete. ✓");
