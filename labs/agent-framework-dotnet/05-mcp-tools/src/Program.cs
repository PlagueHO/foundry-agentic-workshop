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

Console.WriteLine("=== Trip Disruption Concierge — Module 05: MCP Tools ===");
Console.WriteLine();

// ── TODO 1 ───────────────────────────────────────────────────────────────────
// Read the MCP server URL from the environment.
// Default to localhost if not set (local demo server).
//
// var mcpUrl = Environment.GetEnvironmentVariable("FLIGHT_OPS_MCP_SERVER_URL")
//     ?? "http://localhost:3001/mcp";
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine($"[Loop] MCP server URL: {mcpUrl}");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 2 ───────────────────────────────────────────────────────────────────
// Connect to the flight-ops MCP server and discover its tools.
//
// await using var mcpClient = await McpClient.CreateAsync(
//     new HttpClientTransport(new() { Endpoint = new Uri(mcpUrl), Name = "flight-ops" }));
// IList<McpClientTool> mcpTools = await mcpClient.ListToolsAsync();
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine($"[Loop] MCP tools discovered: {string.Join(", ", mcpTools.Select(t => t.Name))}");
// Console.ResetColor();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 3 ───────────────────────────────────────────────────────────────────
// Create the agent, passing the MCP tools via the tools: parameter.
//
// var credential = new AzureCliCredential();
// var client = new AIProjectClient(new Uri(endpoint), credential);
// var agent = client
//     .AsAIAgent(
//         model: model,
//         instructions:
//             "You are the Trip Disruption Concierge. You have access to the " +
//             "flight operations system. When passengers ask about flight status " +
//             "or rebooking, call the appropriate MCP tool to get live data " +
//             "before responding.",
//         tools: [.. mcpTools.Cast<AITool>()]);
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Loop] Agent ready — MCP tools loaded from server.");
// Console.ResetColor();
// Console.WriteLine();
//// var session = await agent.CreateSessionAsync();
//// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 4 ───────────────────────────────────────────────────────────────────
// Run the agent. It should call get_flight_status then get_rebooking_options.
//
// var query =
//     "My flight AU123 is disrupted. Can you check the current status and " +
//     "find me the best rebooking option? My booking reference is BK98765.";
//
// Console.ForegroundColor = ConsoleColor.Cyan;
// Console.WriteLine($"[User] {query}");
// Console.ResetColor();
// Console.WriteLine();
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Loop] RunAsync — agent will call MCP tools as needed...");
// Console.ResetColor();
// Console.WriteLine();
//
// var result = await agent.RunAsync(query, session: session);
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {result.Text}");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

throw new NotImplementedException(
    "Complete the TODOs above, then remove this line and the throw statement.");
