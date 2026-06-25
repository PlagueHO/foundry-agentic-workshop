# Module 07 solution — Foundry IQ knowledge base

Reference implementation for facilitators and proctors.

[create_knowledge_base_agent.py](create_knowledge_base_agent.py) reproduces the
Module 07 end state from code, for when the portal walkthrough is not an option
(for example a Codespace with network restrictions) or to reset an attendee
project to a known-good state. It performs the same work as the UI:

1. Creates the `retail-products` and `retail-policies` **knowledge sources** over
   the pre-seeded Azure AI Search indexes.
1. Creates the **knowledge base** (`KNOWLEDGE_BASE_NAME`) that combines both
   sources using extractive, minimal retrieval — matching the README's **Basic
   configuration** (no LLM, Minimal reasoning, Extractive data).
1. Creates the Foundry project **connection** (RemoteTool / ProjectManagedIdentity)
   that targets the knowledge base MCP endpoint.
1. Creates a new **version** of the `acl-remedy-advisor` Prompt Agent that
   attaches the knowledge base as an MCP tool alongside Web search, Code
   Interpreter, and (when `RETAIL_REMEDY_OPS_MCP_SERVER_URL` is set) the `retail-remedy-ops` MCP
   server, with the tool-routing instructions from Part 5.

## Idempotency

Knowledge sources, the knowledge base, and the project connection are
create-or-update operations, so re-running never creates duplicates. Creating an
agent version always produces a new version — exactly like clicking **Save** in
the portal — and converges on the same desired configuration.

## Prerequisites

- The `retail-products` and `retail-policies` indexes exist and are populated
  (`scripts/seed-product-index.py` and `scripts/seed-document-index.py`).
- Your account (or `AZURE_SEARCH_ADMIN_KEY`) has **Search Service Contributor**
  on the search service.
- Your account has the **Foundry Project Manager** role.
- The Foundry project's managed identity has **Search Index Data Reader** on the
  search service (assigned automatically by `infra/main.bicep`).

## Run

```bash
python labs/introduction-foundry-agent-service/07-foundry-iq/solution/create_knowledge_base_agent.py
```

## Environment variables

Required: `FOUNDRY_PROJECT_ENDPOINT`, `AZURE_SEARCH_SERVICE_NAME`,
`KNOWLEDGE_BASE_NAME`, and (for the connection) `AZURE_SUBSCRIPTION_ID`,
`AZURE_RESOURCE_GROUP`, `FOUNDRY_RESOURCE_NAME`, `FOUNDRY_PROJECT_NAME` — or set
`FOUNDRY_PROJECT_RESOURCE_ID` directly.

Optional: `AGENT_NAME`, `AGENT_MODEL`, `AZURE_SEARCH_PRODUCT_INDEX_NAME`,
`AZURE_SEARCH_DOCUMENT_INDEX_NAME`, `AZURE_SEARCH_ADMIN_KEY`,
`KNOWLEDGE_BASE_CONNECTION_NAME`, `RETAIL_REMEDY_OPS_MCP_SERVER_URL`, `RETAIL_REMEDY_OPS_MCP_SERVER_LABEL`,
`FOUNDRY_CONNECTION_API_VERSION`, `KB_MCP_API_VERSION`, `SKIP_PROJECT_CONNECTION`.

See the script docstring for the full description of each variable. If the
project connection already exists (for example created in the portal), set
`SKIP_PROJECT_CONNECTION=true` to reuse it.
