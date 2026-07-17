# Solution - Module 09: Hosted agents

This folder contains the reference implementation for deploying the ACL Remedy Advisor
agent to Microsoft Foundry hosted agents as two separate deployments -
`acl-remedy-advisor-hosted-container` (Part 1) and `acl-remedy-advisor-hosted-code`
(Part 2). Run scripts from the repository root after activating the workshop virtual
environment and populating `shared/.env` from `shared/.env.example`.

## hosted_agent_support.py

Shared helpers used by every script in this folder: `wait_for_agent_version_active` polls a
new version until it is active, and `get_latest_active_agent_version` selects the newest
active version.

## deploy_hosted_agent_code.py

**Part 2 (primary).** Zips the agent bundle in `src/agent/` and deploys it from source
code. Foundry builds the container image remotely, so no local Docker is required.

```bash
python labs/introduction-foundry-agent-service/09-hosted-agents/solution/deploy_hosted_agent_code.py
```

## deploy_hosted_agent_container.py

**Part 1 (optional).** Builds the image with Docker, pushes it to the shared workshop Azure
Container Registry under a project-specific tag (`acl-remedy-advisor-hosted-container:<project>`),
then deploys the `acl-remedy-advisor-hosted-container` agent from that image. Requires Docker
and the Azure CLI.

```bash
python labs/introduction-foundry-agent-service/09-hosted-agents/solution/deploy_hosted_agent_container.py
```

## invoke_hosted_agent.py

Creates a session against the latest active version of `acl-remedy-advisor-hosted-code`,
routes the agent endpoint to it, and runs a short multi-turn conversation over the
Responses API.

```bash
python labs/introduction-foundry-agent-service/09-hosted-agents/solution/invoke_hosted_agent.py
```

## Notes

- Hosted agents have implicit access to model inference and session storage within their
  own project. Assign roles only for external resources.
- Hosted agents are a preview feature, so the scripts pass `allow_preview=True` to `AIProjectClient`.
