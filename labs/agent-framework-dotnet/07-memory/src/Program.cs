using Azure.Identity;
using Azure.AI.Projects;
using DotNetEnv;
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Foundry;

// Load environment variables from .env in the repository root (searches parent directories)
Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var model = Environment.GetEnvironmentVariable("AGENT_MODEL") ?? "chat";

Console.WriteLine("=== Trip Disruption Concierge — Module 07: Memory & Context Providers ===");
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"  Model : {model}");
Console.ResetColor();
Console.WriteLine();

var credential = new AzureCliCredential();
var projectClient = new AIProjectClient(new Uri(endpoint), credential);

// ── TODO 1 ───────────────────────────────────────────────────────────────────
// Obtain an IChatClient from the Foundry project client so we can wrap it with
// custom AIContextProviders.
//
// IChatClient chatClient = projectClient
//     .AsAIAgent(new ChatClientAgentOptions { ChatOptions = new() { ModelId = model } })
//     .GetService<IChatClient>()
//     ?? throw new InvalidOperationException("Could not retrieve IChatClient.");
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 2 ───────────────────────────────────────────────────────────────────
// Wrap the IChatClient with an agent that uses PassengerProfileMemory.
// The memory provider will extract passenger details from user messages and
// inject them as instructions before each model call.
//
// AIAgent agent = chatClient.AsAIAgent(new ChatClientAgentOptions
// {
//     ChatOptions = new()
//     {
//         Instructions =
//             "You are the Trip Disruption Concierge. " +
//             "You help passengers who have experienced flight disruptions. " +
//             "Always address the passenger by name if known. " +
//             "Reference their specific flight number when relevant."
//     },
//     AIContextProviders = [new PassengerProfileMemory()]
// });
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Agent] Agent ready with passenger profile memory.");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine("[User] Hi, my name is Emma Chen. My flight AU123 was cancelled.");
Console.ResetColor();
Console.WriteLine();

// ── TODO 3 ───────────────────────────────────────────────────────────────────
// Run a multi-turn session and observe the agent recalling the profile.
//
// var session = await agent.CreateSessionAsync();
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {await agent.RunAsync(
//     "Hi, my name is Emma Chen. My flight AU123 AKL→SYD was cancelled with " +
//     "3 hours' notice. What are my options?",
//     session: session)}");
// Console.ResetColor();
// Console.WriteLine();
//
// Console.ForegroundColor = ConsoleColor.Cyan;
// Console.WriteLine("[User] What compensation is typically available for a cancellation?");
// Console.ResetColor();
// Console.WriteLine();
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {await agent.RunAsync(
//     "What compensation is typically available for a cancellation like mine?",
//     session: session)}");
// Console.ResetColor();
// Console.WriteLine();
//
// Console.ForegroundColor = ConsoleColor.Cyan;
// Console.WriteLine("[User] Can you remind me — what was my flight number?");
// Console.ResetColor();
// Console.WriteLine();
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {await agent.RunAsync(
//     "By the way, can you remind me — what was my flight number?",
//     session: session)}");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

throw new NotImplementedException(
    "Complete the TODOs above, then remove this line and the throw statement.");
