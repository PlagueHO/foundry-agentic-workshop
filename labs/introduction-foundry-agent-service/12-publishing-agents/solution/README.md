# Module 12 solution

Use `create_agent.py` when you skipped the earlier prompt-agent modules and need a
known-good `acl-remedy-advisor` version before following the portal publishing
steps. The script creates a new version with the Web Search and Code Interpreter
tools, matching the agent configuration used in Module 05.

```powershell
uv run python labs/introduction-foundry-agent-service/12-publishing-agents/solution/create_agent.py
```

The script reads `FOUNDRY_PROJECT_ENDPOINT` and optional `AGENT_NAME` from the
environment or the repository `.env` file. It does not publish the agent; use
the Foundry portal steps in the main README to choose metadata and publish it.

Reference implementation for facilitators/proctors.
