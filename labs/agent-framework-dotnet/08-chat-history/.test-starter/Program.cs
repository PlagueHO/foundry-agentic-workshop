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

Console.WriteLine("=== Trip Disruption Concierge — Module 08: Session Persistence ===");
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"  Model : {model}");
Console.ResetColor();
Console.WriteLine();

var credential = new AzureCliCredential();

AIAgent agent = new AIProjectClient(new Uri(endpoint), credential)
    .AsAIAgent(
        model: model,
        instructions:
            "You are the Trip Disruption Concierge. " +
            "You help passengers with flight disruption claims. " +
            "Remember details shared earlier in the conversation.");

var session = await agent.CreateSessionAsync();

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine("[User] My flight AU123 AKL→SYD was cancelled — 3 hours' notice.");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Green;
Console.WriteLine($"[Agent] {await agent.RunAsync(
    "My name is Emma Chen. Flight AU123 AKL→SYD was cancelled with only 3 hours' notice. " +
    "What should I do first?",
    session: session)}");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine("[User] What is the standard compensation for a short-notice cancellation?");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Green;
Console.WriteLine($"[Agent] {await agent.RunAsync(
    "What is the standard compensation for a short-notice cancellation like mine?",
    session: session)}");
Console.ResetColor();
Console.WriteLine();

var snapshot = await agent.SerializeSessionAsync(session);
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Session] State serialised. Simulating app restart...");
Console.ResetColor();
Console.WriteLine();

var restoredSession = await agent.DeserializeSessionAsync(snapshot);

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Session] Session restored. Continuing conversation...");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine("[User] (after restart) What was my flight number again?");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Green;
Console.WriteLine($"[Agent] {await agent.RunAsync(
    "Sorry, what was my flight number again?",
    session: restoredSession)}");
Console.ResetColor();
Console.WriteLine();
