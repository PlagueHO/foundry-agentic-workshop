using Azure.Identity;
using Azure.AI.Projects;
using Azure.Search.Documents;
using DotNetEnv;
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Foundry;

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

Console.WriteLine("=== Trip Disruption Concierge - Module 06: Knowledge Bases ===");
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
var searchClient = new SearchClient(
    new Uri($"https://{searchServiceName}.search.windows.net"),
    searchIndexName,
    credential);
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
// ─────────────────────────────────────────────────────────────────────────────

throw new NotImplementedException(
    "Complete the TODOs above, then remove this line and the throw statement.");

