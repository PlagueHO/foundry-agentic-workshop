using System.Text.Json;
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

// ── Create agent ──────────────────────────────────────────────────────────────
AIAgent agent = new AIProjectClient(new Uri(endpoint), credential)
    .AsAIAgent(
        model: model,
        instructions:
            "You are the Trip Disruption Concierge. " +
            "You help passengers with flight disruption claims. " +
            "Remember all details shared earlier in the conversation and refer back to them " +
            "when answering follow-up questions.");

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Agent] Agent ready.");
Console.ResetColor();
Console.WriteLine();

// ── Phase 1: Initial conversation ────────────────────────────────────────────
Console.WriteLine("════════ Phase 1 — Initial session ════════════════════════════════");
Console.WriteLine();

var session = await agent.CreateSessionAsync();

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine("[User] My name is Emma Chen. Flight AU123 AKL→SYD cancelled 3 hrs' notice.");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Green;
Console.WriteLine($"[Agent] {(await agent.RunAsync(
    "My name is Emma Chen. Flight AU123 AKL→SYD was cancelled with only 3 hours' notice. " +
    "What should I do first?",
    session: session)).Text}");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine("[User] What is the standard compensation for a short-notice cancellation?");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Green;
Console.WriteLine($"[Agent] {(await agent.RunAsync(
    "What is the standard compensation for a short-notice cancellation like mine?",
    session: session)).Text}");
Console.ResetColor();
Console.WriteLine();

// ── Phase 2: Serialise the session ───────────────────────────────────────────
Console.WriteLine("════════ Phase 2 — Serialise ═══════════════════════════════════════");
Console.WriteLine();

JsonElement snapshot = await agent.SerializeSessionAsync(session);

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Session] State serialised.");
Console.WriteLine($"[Session] Snapshot size: {snapshot.GetRawText().Length:N0} characters.");
Console.ResetColor();
Console.WriteLine();

// Simulate an app restart by discarding the original session reference.
// In a real application you would store the snapshot JSON to a database.
session = null!;

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Session] Simulating app restart — original session discarded...");
Console.ResetColor();
Console.WriteLine();

// ── Phase 3: Restore and continue ────────────────────────────────────────────
Console.WriteLine("════════ Phase 3 — Restore and continue ═══════════════════════════");
Console.WriteLine();

IAgentSession restoredSession = await agent.DeserializeSessionAsync(snapshot);

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Session] Session restored. Conversation history is intact.");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine("[User] (after restart) What was my flight number again?");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Green;
Console.WriteLine($"[Agent] {(await agent.RunAsync(
    "Sorry, I had to restart the app — can you remind me, what was my flight number?",
    session: restoredSession)).Text}");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine("[User] And what was the next step you recommended?");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Green;
Console.WriteLine($"[Agent] {(await agent.RunAsync(
    "And what was the first thing you told me to do?",
    session: restoredSession)).Text}");
Console.ResetColor();
Console.WriteLine();

Console.WriteLine("Module 08 complete. ✓");
