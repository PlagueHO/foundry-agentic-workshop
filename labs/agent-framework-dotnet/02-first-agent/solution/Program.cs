using System.Diagnostics;
using Azure.Identity;
using Azure.AI.Projects;
using DotNetEnv;
using Microsoft.Agents.AI.Foundry;

// Load environment variables from .env in the repository root (searches parent directories)
Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var model = Environment.GetEnvironmentVariable("AGENT_MODEL") ?? "chat";

Console.WriteLine("=== Trip Disruption Concierge — Module 02: Your First Agent ===");
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"  Model : {model}");
Console.ResetColor();
Console.WriteLine();

// ── Create client and agent ───────────────────────────────────────────────────
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Creating AIProjectClient...");
Console.ResetColor();

var credential = new AzureCliCredential();
var client = new AIProjectClient(new Uri(endpoint), credential);

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Creating AIAgent...");
Console.ResetColor();

var agent = client.AsAIAgent(
    model: model,
    instructions:
        "You are the Trip Disruption Concierge. You help airline passengers " +
        "understand their rights and options when flights are cancelled, delayed, " +
        "or disrupted. Be concise, empathetic, and actionable. " +
        "Focus on practical next steps the passenger can take right now.");

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Agent ready.");
Console.ResetColor();
Console.WriteLine();

// ── Single-turn (non-streaming) ───────────────────────────────────────────────
var query1 =
    "My flight AKL→SYD was cancelled with only 3 hours' notice. " +
    "What are my rights as a passenger?";

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine($"[User] {query1}");
Console.ResetColor();
Console.WriteLine();

var sw = Stopwatch.StartNew();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.Write("[Loop] RunAsync — waiting for response...");
Console.ResetColor();

var result = await agent.RunAsync(query1);

sw.Stop();
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($" done ({sw.ElapsedMilliseconds} ms)");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Green;
Console.WriteLine($"[Agent] {result.Text}");
Console.ResetColor();
Console.WriteLine();

// ── Streaming ─────────────────────────────────────────────────────────────────
Console.WriteLine("─── Streaming ───────────────────────────────────────────────────────────");
Console.WriteLine();

var query2 = "Can I demand a full refund, or must I accept the rebooking?";

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine($"[User] {query2}");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] RunStreamingAsync — streaming tokens as they arrive...");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Green;
Console.Write("[Agent] ");

sw.Restart();
await foreach (var chunk in agent.RunStreamingAsync(query2))
{
    if (chunk.Text is not null)
        Console.Write(chunk.Text);
}
sw.Stop();

Console.ResetColor();
Console.WriteLine();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"[Loop] Streaming complete ({sw.ElapsedMilliseconds} ms)");
Console.ResetColor();
Console.WriteLine();

Console.WriteLine("Module 02 complete. ✓");
