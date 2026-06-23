# Solution — Module 06: MCP tools

This folder contains the reference implementation for Module 06.

## create_agent_with_mcp.py

Code fallback script for attendees who cannot add the MCP tool through the
Agent Builder UI (for example when port forwarding is not available from the
UI context).

Before running, set `RETAIL_REMEDY_OPS_MCP_SERVER_URL` in `shared/.env` to the full tunnel URL
including the `/mcp` path suffix.

```bash
python labs/introduction-foundry-agent-service/06-mcp-tools/solution/create_agent_with_mcp.py
```

The script creates a new version of `acl-remedy-advisor` with Web search,
Code Interpreter, and the Retail Remedy Operations MCP tool attached, and
updated instructions that guide the agent on when to call each tool.
