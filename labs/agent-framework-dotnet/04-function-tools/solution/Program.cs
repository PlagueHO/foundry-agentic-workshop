using System.ComponentModel;
using System.Diagnostics;
using Azure.Identity;
using Azure.AI.Projects;
using DotNetEnv;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;

Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var model = Environment.GetEnvironmentVariable("AGENT_MODEL") ?? "chat";

Console.WriteLine("=== Trip Disruption Concierge — Module 04: Function Tools ===");
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"  Model : {model}");
Console.ResetColor();
Console.WriteLine();

// ── Define the function tool ──────────────────────────────────────────────────
// The lambda is registered as an AI tool. When the agent decides to call it,
// the framework invokes the lambda in-process and feeds the return value back
// to the model as a tool result.
var calculateCompensation = AIFunctionFactory.Create(
    (
        [Description("Hours of delay, or hours of notice given before cancellation")]
        int delayOrNoticeHours,
        [Description("Original one-way ticket price in Australian dollars")]
        decimal ticketPriceAud
    ) =>
    {
        Console.ForegroundColor = ConsoleColor.Yellow;
        Console.WriteLine(
            $"[Tool] → calculate_compensation(" +
            $"delayHours={delayOrNoticeHours}, ticketPrice={ticketPriceAud:C2})");
        Console.ResetColor();

        // Tiered compensation policy
        decimal compensation = delayOrNoticeHours switch
        {
            < 3 => 0m,
            < 5 => ticketPriceAud * 0.25m,
            _ => ticketPriceAud * 0.50m,
        };

        Console.ForegroundColor = ConsoleColor.Yellow;
        Console.WriteLine($"[Tool] ← compensation = {compensation:C2}");
        Console.ResetColor();
        Console.WriteLine();

        return $"Compensation entitlement: {compensation:C2} " +
               $"(rule: <3h = nil, 3\u20135h = 25%, 5h+ = 50% of ticket price)";
    },
    "calculate_compensation",
    "Calculates the passenger compensation entitlement based on delay duration " +
    "and ticket price using the standard airline disruption policy.");

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Tool registered: calculate_compensation");
Console.ResetColor();
Console.WriteLine();

// ── Create agent with tool ────────────────────────────────────────────────────
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Creating agent with function tool...");
Console.ResetColor();

var credential = new AzureCliCredential();
var client = new AIProjectClient(new Uri(endpoint), credential);

var agent = client
    .AsAIAgent(
        model: model,
        instructions:
            "You are the Trip Disruption Concierge. When a passenger asks " +
            "about compensation, always call the calculate_compensation tool " +
            "with the actual delay hours and ticket price before answering. " +
            "State the calculated amount clearly in your response.",
        tools: [calculateCompensation]);

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] Agent ready — tool will execute locally when called.");
Console.ResetColor();
Console.WriteLine();

// ── Run — tool call visible in console ───────────────────────────────────────
var query =
    "My flight AU123 AKL→SYD was cancelled with only 3 hours' notice. " +
    "My ticket cost AUD 420. How much compensation am I entitled to?";

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine($"[User] {query}");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] RunAsync starting — agent will decide when to call tools...");
Console.ResetColor();
Console.WriteLine();

var sw = Stopwatch.StartNew();
var result = await agent.RunAsync(query);
sw.Stop();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"[Loop] RunAsync complete ({sw.ElapsedMilliseconds} ms)");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Green;
Console.WriteLine($"[Agent] {result.Text}");
Console.ResetColor();
Console.WriteLine();

// ── Second turn — tool called again with different values ─────────────────────
var query2 =
    "What if my ticket had cost AUD 650 and the delay was 6 hours?";

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine($"[User] {query2}");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Loop] RunAsync starting...");
Console.ResetColor();
Console.WriteLine();

sw.Restart();
var result2 = await agent.RunAsync(query2);
sw.Stop();

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"[Loop] RunAsync complete ({sw.ElapsedMilliseconds} ms)");
Console.ResetColor();
Console.WriteLine();

Console.ForegroundColor = ConsoleColor.Green;
Console.WriteLine($"[Agent] {result2.Text}");
Console.ResetColor();
Console.WriteLine();

Console.WriteLine("Module 04 complete. ✓");
