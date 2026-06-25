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

// ── TODO 1 ───────────────────────────────────────────────────────────────────
// Create an Azure AI Search client.
// Point it at the passenger-rights index using DefaultAzureCredential.
//
// var searchClient = new SearchClient(
//     new Uri($"https://{searchServiceName}.search.windows.net"),
//     searchIndexName,
//     credential);
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[RAG] Search client ready.");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

// ── TODO 2 ───────────────────────────────────────────────────────────────────
// Create the agent.
// Use AIProjectClient.AsAIAgent(ChatClientAgentOptions) and pass a
// PassengerRightsContextProvider in the AIContextProviders list.
//
// AIAgent agent = new AIProjectClient(new Uri(endpoint), credential)
//     .AsAIAgent(new ChatClientAgentOptions
//     {
//         ChatOptions = new()
//         {
//             ModelId = model,
//             Instructions =
//                 "You are the Trip Disruption Concierge. " +
//                 "You have access to passenger rights policy documents. " +
//                 "When answering questions about rights or compensation, use the " +
//                 "provided context. Cite specific figures and policy rules when possible."
//         },
//         AIContextProviders = [new PassengerRightsContextProvider(searchClient)]
//     });
//
// Console.ForegroundColor = ConsoleColor.DarkGray;
// Console.WriteLine("[Agent] Agent ready with knowledge base context provider.");
// Console.ResetColor();
// Console.WriteLine();
//
// ─────────────────────────────────────────────────────────────────────────────

Console.ForegroundColor = ConsoleColor.Cyan;
Console.WriteLine("[User] My flight AU123 AKL→SYD was cancelled with 3 hours' notice.");
Console.WriteLine("       What compensation am I entitled to?");
Console.ResetColor();
Console.WriteLine();

// ── TODO 3 ───────────────────────────────────────────────────────────────────
// Create a session and run three questions that exercise the knowledge base.
//
// var session = await agent.CreateSessionAsync();
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {await agent.RunAsync(
//     "My flight AU123 AKL→SYD was cancelled with 3 hours' notice. " +
//     "What compensation am I entitled to under passenger rights rules?",
//     session: session)}");
// Console.ResetColor();
// Console.WriteLine();
//
// Console.ForegroundColor = ConsoleColor.Cyan;
// Console.WriteLine("[User] Does it matter that the cancellation was caused by a storm?");
// Console.ResetColor();
// Console.WriteLine();
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {await agent.RunAsync(
//     "Does it matter that the cancellation was caused by a storm?",
//     session: session)}");
// Console.ResetColor();
// Console.WriteLine();
//
// Console.ForegroundColor = ConsoleColor.Cyan;
// Console.WriteLine("[User] How do I file a formal claim if the airline refuses to pay?");
// Console.ResetColor();
// Console.WriteLine();
//
// Console.ForegroundColor = ConsoleColor.Green;
// Console.WriteLine($"[Agent] {await agent.RunAsync(
//     "How do I file a formal claim if the airline refuses to pay?",
//     session: session)}");
// Console.ResetColor();
// Console.WriteLine();
//
// Console.WriteLine("Module 06 complete. ✓");
//
// ─────────────────────────────────────────────────────────────────────────────

throw new NotImplementedException(
    "Complete the TODOs above, then remove this line and the throw statement.");

// ── PassengerRightsContextProvider ────────────────────────────────────────────
// Injects passenger-rights documents retrieved from Azure AI Search into every
// agent turn. Uses the deferred-search pattern: after each turn the user's
// question pre-fetches context for the *next* turn. First turn seeds with a
// broad default query so the model always has relevant documents from turn 1.
internal sealed class PassengerRightsContextProvider(SearchClient searchClient)
    : AIContextProvider
{
    private string _cachedContext = string.Empty;

    // ProvideAIContextAsync is called BEFORE the model call.
    // Return documents cached after the previous turn.
    // On turn 1 the cache is empty — seed it with a broad default query.
    protected override async ValueTask<AIContext> ProvideAIContextAsync(
        InvokingContext context, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(_cachedContext))
        {
            _cachedContext = await FetchContextAsync(
                "flight cancellation delay compensation passenger rights",
                cancellationToken);
        }

        return new AIContext { Instructions = _cachedContext };
    }

    // StoreAIContextAsync is called AFTER the model call.
    // Extract the user's question and pre-fetch context for the next turn.
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

    // ── TODO 4 ───────────────────────────────────────────────────────────────────
    // Query the Azure AI Search index for documents relevant to `query` and return
    // them as a formatted string. Replace the throw with the implementation from
    // the README (Step 5).
    //
    // ─────────────────────────────────────────────────────────────────────────────
    private Task<string> FetchContextAsync(string query, CancellationToken ct)
    {
        _ = searchClient; // will be used after TODO 4 is implemented
        throw new NotImplementedException(
            "Complete TODO 4: implement FetchContextAsync — see README Step 5.");
    }
}
