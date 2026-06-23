# Solution — Module 10: Foundry Toolboxes

This folder contains the reference implementation for Module 10.

## setup_toolbox.py

Creates the `acl-remedy-toolbox` toolbox from code. Use it when the Foundry portal
does not yet expose the Toolboxes preview UI in your region, or when you skipped the
portal toolbox creation step in Part 2. It creates the toolbox only — it does not
modify any agent.

The script:

1. Creates the `acl-remedy-toolbox` toolbox with **Web Search**, the
   `retail_remedy_ops` MCP server, **Code Interpreter**, and **Tool Search**
   (`toolbox_search_preview`) enabled, each with a unique tool name.
1. Prints the toolbox consumer endpoint URL.

Before running:

- Start the MCP server (`server.py`) and expose port 8080 as a public tunnel, or
  use the shared Azure Container Apps server (see Module 06 README, Part 2).
- Set `RETAIL_REMEDY_OPS_MCP_SERVER_URL` in `shared/.env` to the public URL including the `/mcp` suffix.

```bash
python labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/setup_toolbox.py
```

After running, set the new toolbox version as the default in the portal if it is
not already, then deploy the hosted agent with `deploy_hosted_agent_code.py`.

## deploy_hosted_agent_code.py

The primary deployment script for Part 3. It zips the agent bundle in
[`../src/agent/`](../src/agent) and uploads it to Foundry, which builds the container
image remotely and runs it as a **new version of the `acl-remedy-advisor-hosted-code`
hosted agent** from Module 09. The new version answers entirely through the
`acl-remedy-toolbox` Foundry Toolbox.

The script:

1. Zips `src/agent/` flat (so `main.py` and `requirements.txt` are at the archive root)
   and computes its SHA-256 hash.
1. Creates a new agent version from code with a 1 vCPU / 2 GiB hosted definition, a remote
   Python 3.13 build, the **Responses** protocol, and the `AZURE_AI_MODEL_DEPLOYMENT_NAME`
   and `TOOLBOX_NAME` environment variables baked in.
1. Polls until the version reports `active`, then grants the agent's own per-deploy
   Microsoft Entra identity the **Foundry User** role (via `hosted_agent_support.py`) so it
   can call the model and authenticate to the toolbox MCP endpoint.

Before running:

- Create the `acl-remedy-toolbox` toolbox (Part 2, or `setup_toolbox.py`) with Tool Search
  enabled and a default version set.
- Sign in with `az login` (the script authenticates with `DefaultAzureCredential`).
- Set `FOUNDRY_PROJECT_ENDPOINT`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`,
  `FOUNDRY_RESOURCE_NAME`, and `TOOLBOX_NAME` (`acl-remedy-toolbox`) in `shared/.env`.
  `HOSTED_AGENT_NAME_CODE` defaults to `acl-remedy-advisor-hosted-code` and `AGENT_MODEL`
  defaults to `chat`.

```bash
python labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/deploy_hosted_agent_code.py
```

## invoke_hosted_agent.py

Invokes the deployed `acl-remedy-advisor-hosted-code` agent over the Responses API.

The script:

1. Selects the latest active version of the hosted agent.
1. Creates a session and routes 100% of the agent endpoint traffic to that version.
1. Runs a two-turn Australian Consumer Law conversation for receipt `R-1007` — the agent
   uses Tool Search to discover and call the retail tools, web search, and code interpreter
   behind the single toolbox endpoint — then deletes the session.

```bash
python labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/invoke_hosted_agent.py
```

## hosted_agent_support.py

Shared helpers used by `deploy_hosted_agent_code.py` and `invoke_hosted_agent.py` (and the
`src/starter.py` deploy exercise): poll a version until it is `active`, select the latest
active version, and grant the **Foundry User** role to the agent's per-deploy identity. These
mirror the Module 09 helpers so this module stays independently runnable.
