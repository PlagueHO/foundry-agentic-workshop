using System.Text;
using Azure.Identity;
using Azure.AI.Projects;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using DotNetEnv;
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Foundry;
using Microsoft.Extensions.AI;

// Load environment variables from .env in the repository root (searches parent directories)
Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var model = Environment.GetEnvironmentVariable("AGENT_MODEL") ?? "chat";

var searchServiceName = Environment.GetEnvironmentVariable("AZURE_SEARCH_SERVICE_NAME")
    ?? throw new InvalidOperationException(
        "AZURE_SEARCH_SERVICE_NAME is not set. Add it to .env in the repository root.");

var searchIndexName = Environment.GetEnvironmentVariable("AZURE_SEARCH_PASSENGER_RIGHTS_INDEX_NAME")
    ?? "passenger-rights";

Console.WriteLine("=== Trip Disruption Concierge — Module 06: Knowledge Bases ===");
Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine($"  Model        : {model}");
Console.WriteLine($"  Search index : {searchServiceName}/{searchIndexName}");
Console.ResetColor();
Console.WriteLine();

var credential = new AzureCliCredential();

// ── Create Azure AI Search client ─────────────────────────────────────────────
var searchClient = new SearchClient(
    new Uri($"https://{searchServiceName}.search.windows.net"),
    searchIndexName,
    credential);

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[RAG] Search client ready.");
Console.ResetColor();
Console.WriteLine();

// ── Create agent with knowledge base context provider ─────────────────────────
// The PassengerRightsContextProvider is attached via AIContextProviders.
// Before each model call it injects retrieved passenger-rights documents
// as additional context, grounding the model's answers in policy text.
AIAgent agent = new AIProjectClient(new Uri(endpoint), credential)
    .AsAIAgent(new ChatClientAgentOptions
    {
        ChatOptions = new()
        {
            ModelId = model,
            Instructions =
                "You are the Trip Disruption Concierge. " +
                "You have access to passenger rights policy documents. " +
                "When answering questions about rights or compensation, use the " +
                "provided context. Cite specific figures and policy rules when possible. " +
                "If the context does not cover the question, say so clearly."
        },
        AIContextProviders = [new PassengerRightsContextProvider(searchClient)]
    });

Console.ForegroundColor = ConsoleColor.DarkGray;
Console.WriteLine("[Agent] Agent ready with knowledge base context provider.");
Console.ResetColor();
Console.WriteLine();

// ── Multi-turn grounded conversation ──────────────────────────────────────────
var session = await agent.CreateSessionAsync();
int turn = 0;

async Task AskAsync(string question)
{
    turn++;
    Console.WriteLine($"─── Turn {turn} {'─',68}");
    Console.WriteLine();

    Console.ForegroundColor = ConsoleColor.Cyan;
    Console.WriteLine($"[User] {question}");
    Console.ResetColor();
    Console.WriteLine();

    Console.ForegroundColor = ConsoleColor.DarkGray;
    Console.Write("[Agent] Thinking (context + model call)...");
    Console.ResetColor();

    var result = await agent.RunAsync(question, session: session);

    Console.ForegroundColor = ConsoleColor.DarkGray;
    Console.WriteLine(" done");
    Console.ResetColor();
    Console.WriteLine();

    Console.ForegroundColor = ConsoleColor.Green;
    Console.WriteLine($"[Agent] {result.Text}");
    Console.ResetColor();
    Console.WriteLine();
}

await AskAsync(
    "My flight AU123 AKL→SYD was cancelled with only 3 hours' notice. " +
    "What compensation am I entitled to under passenger rights rules?");

await AskAsync(
    "Does it matter that the airline says the cancellation was caused by a storm?");

await AskAsync(
    "How do I file a formal claim if the airline refuses to pay?");

Console.WriteLine("Module 06 complete. ✓");

// ── PassengerRightsContextProvider ────────────────────────────────────────────
// This context provider queries the passenger-rights Azure AI Search index
// and injects the top matching documents before every model call.
// Pattern: deferred search — after each turn, the user's query is used to
// pre-fetch context for the *next* turn.  The first turn uses a default seed query.
internal sealed class PassengerRightsContextProvider(SearchClient searchClient)
    : AIContextProvider
{
    private string _cachedContext = string.Empty;

    // ProvideAIContextAsync is called BEFORE the model call.
    // Return the context that was cached after the previous turn.
    // On the first turn the cache is empty, so we seed it with a broad default.
    protected override async ValueTask<AIContext> ProvideAIContextAsync(
        InvokingContext context, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(_cachedContext))
        {
            // First turn: seed with a general query to prime the context.
            _cachedContext = await FetchContextAsync(
                "flight cancellation delay compensation passenger rights",
                cancellationToken);
        }

        return new AIContext { Instructions = _cachedContext };
    }

    // StoreAIContextAsync is called AFTER the model call.
    // Extract the user's question and search for relevant documents
    // so they are ready for the NEXT turn.
    protected override async ValueTask StoreAIContextAsync(
        InvokedContext context, CancellationToken cancellationToken = default)
    {
        var userQuery = context.RequestMessages
            .Where(m => m.Role == ChatRole.User)
            .Select(m => m.Text ?? string.Empty)
            .LastOrDefault() ?? string.Empty;

        if (!string.IsNullOrWhiteSpace(userQuery))
            _cachedContext = await FetchContextAsync(userQuery, cancellationToken);
    }

    private async Task<string> FetchContextAsync(string query, CancellationToken ct)
    {
        Console.ForegroundColor = ConsoleColor.Yellow;
        var shortQuery = query.Length > 60 ? query[..60] + "..." : query;
        Console.WriteLine($"\n[RAG] Searching: \"{shortQuery}\"");
        Console.ResetColor();

        var options = new SearchOptions { Size = 4 };
        var response = await searchClient.SearchAsync<SearchDocument>(query, options, ct);

        var sb = new StringBuilder();
        sb.AppendLine("Passenger rights reference documents:");
        sb.AppendLine();

        int docCount = 0;
        await foreach (var result in response.Value.GetResultsAsync())
        {
            docCount++;
            var doc = result.Document;
            var title = doc.TryGetValue("title", out var t) ? t?.ToString() : null;
            var content = doc.TryGetValue("content", out var c) ? c?.ToString() : null;

            if (title is not null || content is not null)
            {
                if (title is not null)
                    sb.AppendLine($"[{docCount}] {title}");
                if (content is not null)
                    sb.AppendLine(content);
                sb.AppendLine();
            }
        }

        Console.ForegroundColor = ConsoleColor.Yellow;
        Console.WriteLine($"[RAG] {docCount} document(s) retrieved.");
        Console.ResetColor();

        return sb.ToString();
    }
}
