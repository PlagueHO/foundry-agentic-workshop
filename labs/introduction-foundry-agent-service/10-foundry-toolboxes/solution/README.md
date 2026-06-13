# Solution — Module 10: Foundry Toolboxes

This folder contains the reference implementation for Module 10.

## consume_toolbox.py

The primary script for this module. It consumes the `acl-remedy-toolbox`
toolbox from a Python **Microsoft Agent Framework** app through the toolbox's
MCP endpoint.

The script:

1. Builds the toolbox consumer endpoint from `FOUNDRY_PROJECT_ENDPOINT` and
   `TOOLBOX_NAME` as `{endpoint}/toolboxes/{name}/mcp?api-version=v1`.
1. Wraps the endpoint in an `MCPStreamableHTTPTool` backed by an
   `httpx.AsyncClient` that adds the Entra bearer token (scope
   `https://ai.azure.com/.default`) and the `Foundry-Features: Toolboxes=V1Preview`
   header to every request, including the connection handshake.
1. Builds a `FoundryChatClient` and an `Agent` whose instructions tell the model
   to call `tool_search` when a needed tool is not already visible.
1. Sends a built-in Australian Consumer Law scenario for receipt `R-1007` and
   prints the agent's remedy recommendation.
1. Retries the connection a few times with a short backoff to absorb cold-start
   drops on the toolbox endpoint.

Before running:

- Create the `acl-remedy-toolbox` toolbox (Module 10, Part 2) with Web Search,
  the `retail_remedy_ops` MCP server, and Code Interpreter, with Tool Search
  enabled and a default version set.
- Start the MCP server (`server.py`) and expose port 8080 as a public tunnel
  (see Module 06 README, Part 2).
- Sign in with `az login` (the script authenticates with `DefaultAzureCredential`).
- Set `FOUNDRY_PROJECT_ENDPOINT` and `TOOLBOX_NAME` (`acl-remedy-toolbox`) in
  `shared/.env`.

```bash
python labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/consume_toolbox.py
```

## setup_toolbox.py

Code fallback script for attendees whose Foundry portal does not yet expose the
Toolboxes preview UI. It creates the toolbox only — it does not modify any agent.

The script:

1. Creates the `acl-remedy-toolbox` toolbox with **Web Search**, the
   `retail_remedy_ops` MCP server, **Code Interpreter**, and **Tool Search**
   (`toolbox_search_preview`) enabled.
1. Prints the toolbox consumer endpoint URL.

Before running:

- Start the MCP server (`server.py`) and expose port 8080 as a public tunnel
  (see Module 06 README, Part 2).
- Set `MCP_SERVER_URL` in `shared/.env` to the public tunnel URL including the
  `/mcp` suffix.

```bash
python labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/setup_toolbox.py
```

After running, set the new toolbox version as the default in the portal if it is
not already, then run `consume_toolbox.py` to consume it.
