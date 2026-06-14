"""Invoke the deployed acl-remedy-advisor-hosted-code agent over the Responses API.

Creates a session against the latest active version of the hosted agent, routes the
agent endpoint to that version, then runs a short multi-turn conversation. Sessions only
work with hosted agents and are a preview feature accessed via ``project.beta.agents``.

Usage:
    python labs/introduction-foundry-agent-service/09-hosted-agents/solution/invoke_hosted_agent.py
"""

import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentEndpointConfig,
    AgentEndpointProtocol,
    FixedRatioVersionSelectionRule,
    VersionRefIndicator,
    VersionSelector,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from hosted_agent_support import get_latest_active_agent_version

PROMPTS = [
    'A customer bought a laptop on receipt R-1007 and the screen developed dead pixels '
    'after 14 months. What remedy applies under the Australian Consumer Law?',
    'They still have the original box and charger. Does that change the remedy?',
]


def run() -> None:
    load_dotenv()

    endpoint = os.environ['FOUNDRY_PROJECT_ENDPOINT']
    agent_name = os.environ.get('HOSTED_AGENT_NAME_CODE', 'acl-remedy-advisor-hosted-code')

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as client,
    ):
        agent = get_latest_active_agent_version(client, agent_name)
        print(f'Using hosted agent {agent_name} version {agent.version}.')

        session = client.beta.agents.create_session(
            agent_name=agent_name,
            version_indicator=VersionRefIndicator(agent_version=agent.version),
        )
        print(f'Session created (id: {session.agent_session_id}, status: {session.status}).')

        try:
            # Route 100% of traffic for this agent name to the version we just selected.
            endpoint_config = AgentEndpointConfig(
                version_selector=VersionSelector(
                    version_selection_rules=[
                        FixedRatioVersionSelectionRule(
                            agent_version=agent.version,
                            traffic_percentage=100,
                        ),
                    ],
                ),
                protocols=[AgentEndpointProtocol.RESPONSES],
            )
            client.beta.agents.patch_agent_details(agent_name=agent_name, agent_endpoint=endpoint_config)

            openai_client = client.get_openai_client(agent_name=agent_name)

            previous_response_id: str | None = None
            for prompt in PROMPTS:
                print(f'\n> {prompt}')
                # Only send previous_response_id once a prior turn exists; passing
                # None serializes to JSON null, which the Responses API rejects.
                turn_kwargs: dict[str, object] = {
                    'input': prompt,
                    'extra_body': {'agent_session_id': session.agent_session_id},
                }
                if previous_response_id is not None:
                    turn_kwargs['previous_response_id'] = previous_response_id
                response = openai_client.responses.create(**turn_kwargs)
                previous_response_id = response.id
                print(response.output_text)
        finally:
            client.beta.agents.delete_session(
                agent_name=agent_name,
                session_id=session.agent_session_id,
            )
            print(f'\nSession deleted (id: {session.agent_session_id}).')


if __name__ == '__main__':
    run()
