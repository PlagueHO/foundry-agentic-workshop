# Module 08 solution - run the Prompt Agent with Agent Framework

Reference implementation for facilitators and proctors.

This folder contains two scripts:

## [run_prompt_agent.py](run_prompt_agent.py)

The completed version of [src/starter.py](../src/starter.py). It connects to the
`acl-remedy-advisor` Prompt Agent from Modules 04-07 using the Agent Framework's
`FoundryAgent` client and runs it from Python - first as a single response, then
as a streamed response. `DefaultAzureCredential` reuses the attendee's `az login`
session, so no keys appear in code.

```bash
python labs/introduction-foundry-agent-service/08-agent-framework-python/solution/run_prompt_agent.py
```

Both runs appear under the agent's **Traces** tab in the Foundry portal, exactly
like a playground conversation.

### Environment variables

Required: `FOUNDRY_PROJECT_ENDPOINT`.

Optional: `AGENT_NAME` (default `acl-remedy-advisor`), `AGENT_VERSION` (leave
empty to use the latest published version, or set it to pin a specific version).

## [create_knowledge_base_agent.py](create_knowledge_base_agent.py)

A copy of the Module 07 solution script, included here so an attendee who did not
finish Module 07 can reach the same end state before running the Agent Framework
code. It recreates the Foundry IQ knowledge base and the grounded
`acl-remedy-advisor` Prompt Agent from code.

```bash
python labs/introduction-foundry-agent-service/08-agent-framework-python/solution/create_knowledge_base_agent.py
```

See the Module 07 solution README for the full description of prerequisites,
idempotency behaviour, and the complete environment-variable reference. This copy
is identical except for the usage path in its docstring.
