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
Console.WriteLine();

// ── TODO 1 ───────────────────────────────────────────────────────────────────
// Create an AIProjectClient using the Foundry project endpoint and
// DefaultAzureCredential for authentication.
//
// var credential = new AzureCliCredential();
// var client = new AIProjectClient(new Uri(endpoint), credential);
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 2 ───────────────────────────────────────────────────────────────────
// Create an AIAgent using client.AsAIAgent().
// Set the model to the `model` variable and give the agent its system instructions.
//
// var agent = client.AsAIAgent(
//     model: model,
//     instructions:
//         "You are the Trip Disruption Concierge. You help airline passengers " +
//         "understand their rights and options when flights are cancelled, delayed, " +
//         "or disrupted. Be concise, empathetic, and actionable. " +
//         "Focus on practical next steps the passenger can take right now.");
//
// ─────────────────────────────────────────────────────────────────────────────

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine("[User] My flight AKL→SYD was cancelled with only 3 hours' notice.");
Console.WriteLine("       What are my rights as a passenger?");
Console.ResetColor();
Console.WriteLine();

// ── TODO 3 ───────────────────────────────────────────────────────────────────
// Run the agent with RunAsync and print result.Text.
//
// var result = await agent.RunAsync(
//     "My flight AKL→SYD was cancelled with only 3 hours' notice. " +
//     "What are my rights as a passenger?");
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {result.Text}");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

Console.WriteLine("─── Streaming ───────────────────────────────────────────────────────────");
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine("[User] Can I demand a full refund, or must I accept the rebooking?");
Console.ResetColor();
Console.WriteLine();

// ── TODO 4 ───────────────────────────────────────────────────────────────────
// Stream a second response token-by-token using RunStreamingAsync.
// Print each chunk as it arrives.
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.Write("[Agent] ");
// await foreach (var chunk in agent.RunStreamingAsync(
//     "Can I demand a full refund, or must I accept the rebooking?"))
// {
//     if (chunk.Text is not null)
//         Console.Write(chunk.Text);
// }
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

throw new NotImplementedException(
    "Complete the TODOs above, then remove this line and the throw statement.");
