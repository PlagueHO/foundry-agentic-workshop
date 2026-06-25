# 06. Knowledge Bases (AI Search)

**Estimated time:** 25 minutes

![Microsoft Agent Framework overview: an open-source engine for building and orchestrating AI agents, summarised in five pillars — Unified SDK (AIAgent, AgentThread, and AgentTool primitives built on Microsoft.Extensions.AI), Local-first and cloud-agnostic (run agents locally then move the same code to Foundry Agent Service or any cloud containers), Multi-agent orchestration (sequential, concurrent, handoff, group chat, magentic, and workflow patterns), Tools and extensibility (out-of-the-box integrations plus functions, APIs, and MCP servers as tools), and Enterprise-grade foundations (approval flows, content-policy hooks, OpenTelemetry observability, and long-running execution).](../../../docs/assets/diagrams/agent-framework-introduction.png)

> [!IMPORTANT]
> This module builds on [Module 02](../02-first-agent/README.md). The passenger-rights Azure AI Search index must be seeded before you begin. If you have not already done so, run `python scripts/seed-passenger-rights-index.py` from the repository root.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Understand the `AIContextProvider` contract: `ProvideAIContextAsync` and `StoreAIContextAsync`.
- Use `Azure.Search.Documents` to query an Azure AI Search index from .NET.
- Attach the provider to an agent via `ChatClientAgentOptions.AIContextProviders`.
- Observe the agent citing retrieved documents in its responses.

## Concepts

### AIContextProvider

An `AIContextProvider` injects additional context into every agent turn:

| Method | Called | Purpose |
|---|---|---|
| `ProvideAIContextAsync` | _Before_ the model call | Return extra instructions or documents the model should see |
| `StoreAIContextAsync` | _After_ the model call | Persist observations for future turns (optional) |

The returned `AIContext.Instructions` string is prepended to the model's system context for that turn.

Extend `AIContextProvider` by overriding these two methods:

```csharp
internal sealed class PassengerRightsContextProvider(SearchClient searchClient)
    : AIContextProvider
{
    protected override async ValueTask<AIContext> ProvideAIContextAsync(
        InvokingContext context, CancellationToken ct = default)
    {
        // inject pre-fetched documents before the model call
        return new AIContext { Instructions = await FetchContextAsync("...", ct) };
    }

    protected override async ValueTask StoreAIContextAsync(
        InvokedContext context, CancellationToken ct = default)
    {
        // pre-fetch context for the next turn using the user's question
    }
}
```

### SearchClient

`Azure.Search.Documents.SearchClient` connects to a single Azure AI Search index using `DefaultAzureCredential`:

```csharp
var searchClient = new SearchClient(
    new Uri($"https://{serviceName}.search.windows.net"),
    indexName,
    new AzureCliCredential());

var response = await searchClient.SearchAsync<SearchDocument>(query, options, ct);
await foreach (var result in response.Value.GetResultsAsync()) { /* ... */ }
```

### Retrieval pattern

This module uses a **deferred search** approach: after each turn, the provider searches for documents relevant to the user's question and caches the result. On the next turn those cached documents are injected as context before the model call. This ensures the model always has relevant documents without needing to predict the query before the user types it.

For more on context providers in the Microsoft Agent Framework, see the [Microsoft Agent Framework overview](https://learn.microsoft.com/en-us/agent-framework/overview/).

## Steps

### Part 1 — Complete the starter code

#### 1. Open the starter file

- [ ] Open `src/Program.cs` in the editor.

#### 2. Create the Azure AI Search client (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  var searchClient = new SearchClient(
      new Uri($"https://{searchServiceName}.search.windows.net"),
      searchIndexName,
      credential);

  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[RAG] Search client ready.");
  Console.ResetColor();
  Console.WriteLine();
  ```

  `credential` is the `DefaultAzureCredential` already constructed earlier in the file. `searchIndexName` defaults to `passenger-rights` if `AZURE_SEARCH_PASSENGER_RIGHTS_INDEX_NAME` is not set.

#### 3. Create the agent with the context provider (TODO 2)

- [ ] Locate `// ── TODO 2` and replace the commented-out block with:

  ```csharp
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
                  "provided context. Cite specific figures and policy rules when possible."
          },
          AIContextProviders = [new PassengerRightsContextProvider(searchClient)]
      });

  Console.ForegroundColor = ConsoleColor.DarkGray;
  Console.WriteLine("[Agent] Agent ready with knowledge base context provider.");
  Console.ResetColor();
  Console.WriteLine();
  ```

#### 4. Run the agent turns (TODO 3)

- [ ] Locate `// ── TODO 3` and uncomment the session and query block already commented out there.
- [ ] Remove the `throw new NotImplementedException(...)` line immediately below the TODO block.

  > [!NOTE]
  > The `PassengerRightsContextProvider` class is scaffolded below the main program. In the next step you will implement `FetchContextAsync` inside it.

#### 5. Implement the search query (TODO 4)

- [ ] Locate `// ── TODO 4` inside `PassengerRightsContextProvider` and replace the `throw` with:

  ```csharp
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
  ```

### Part 2 — Run and verify

#### 6. Run the starter

- [ ] In a terminal, run:

  ```bash
  dotnet run --project labs/agent-framework-dotnet/06-knowledge-bases/src/TripConcierge.KnowledgeBases.csproj
  ```

- [ ] Confirm yellow `[RAG]` lines appear showing the query sent to Azure AI Search and the document count retrieved.

## Validation

- Each agent response includes numbered citation markers such as `[1]`, `[2]` drawn from retrieved documents.
- Yellow `[RAG]` lines show the query sent to Azure AI Search and the document count retrieved.
- The agent cites compensation figures (e.g. EUR 250/400/600) drawn from the knowledge base, not from training data alone.

## Congratulations 🎉

You grounded the Trip Disruption Concierge in a real Azure AI Search index. The agent now cites specific policy figures from your indexed documents rather than relying purely on training data, making its answers more accurate and verifiable.

> [!TIP]
> **Next up → [Module 07: Memory & Context Providers](../07-memory/README.md)**
> Teach the agent to remember passenger details across turns by implementing a custom context provider that extracts and persists a passenger profile inside the session.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `AZURE_SEARCH_SERVICE_NAME is not set` | Add the value to `.env` in the repository root (output from `azd env get-values`) |
| `AuthenticationFailedException` | Run `az login` to refresh your Azure CLI credentials |
| `AuthorizationFailed` on search | Your account needs `Search Service Contributor` or `Search Index Data Reader` on the search resource |
| Zero documents retrieved | Confirm the `passenger-rights` index is seeded — run `python scripts/seed-passenger-rights-index.py` |
| `NotImplementedException` | A TODO is still incomplete |
