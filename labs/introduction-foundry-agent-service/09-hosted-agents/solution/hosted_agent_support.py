"""Shared helpers for deploying and operating the Module 09 hosted agents.

These helpers are used by both deployment scripts (``deploy_hosted_agent_code.py`` and
``deploy_hosted_agent_container.py``) and the invocation script
(``invoke_hosted_agent.py``) so the lab keeps a single source of truth for polling,
version selection, and agent-identity RBAC.
"""

import time

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AgentVersionDetails


def wait_for_agent_version_active(
    client: AIProjectClient,
    agent_name: str,
    agent_version: str,
    *,
    max_attempts: int = 60,
    poll_interval_seconds: int = 10,
) -> None:
    """Poll until the agent version reports ``active``; raise on ``failed`` or timeout."""
    print('Waiting for the hosted agent version to become active...')

    for attempt in range(max_attempts):
        time.sleep(poll_interval_seconds)
        version_details = client.agents.get_version(agent_name=agent_name, agent_version=agent_version)
        status = version_details['status']
        print(f'  Agent version status: {status} (attempt {attempt + 1}/{max_attempts})')

        if status == 'active':
            print('Agent version is now active.')
            return
        if status == 'failed':
            raise RuntimeError(f'Hosted agent version provisioning failed: {dict(version_details)}')

    raise RuntimeError('Timed out waiting for the hosted agent version to become active.')


def get_latest_active_agent_version(client: AIProjectClient, agent_name: str) -> AgentVersionDetails:
    """Return the newest active version of the named hosted agent."""
    for version in client.agents.list_versions(agent_name=agent_name, order='desc'):
        if version.status == 'active':
            return version

    raise RuntimeError(
        f"No active version found for hosted agent '{agent_name}'. "
        'Deploy a version first with deploy_hosted_agent_code.py or deploy_hosted_agent_container.py.'
    )
