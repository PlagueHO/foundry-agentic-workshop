"""Create a known-good prompt agent for Module 12 publishing."""

import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool, PromptAgentDefinition, WebSearchTool
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


INSTRUCTIONS = (
    'You are an Australian Consumer Law (ACL) Remedy Advisor for retail staff.\n'
    'Help staff determine whether a customer issue is a major or minor failure and\n'
    'recommend a practical repair, replacement, or refund response.\n\n'
    'Use web search to ground guidance in current ACCC information at accc.gov.au\n'
    'and cite sources with links. State that your response is general guidance, not\n'
    'legal advice, and that no-refund signs are unlawful under the ACL.\n\n'
    'When asked to calculate a refund, depreciation, or pro-rata amount, use code\n'
    'interpreter and show the working. Be concise and practical.'
)


def run() -> None:
    """Create a new agent version using the workshop's standard agent settings."""
    load_dotenv()

    endpoint = os.environ.get('FOUNDRY_PROJECT_ENDPOINT')
    if not endpoint:
        raise RuntimeError('FOUNDRY_PROJECT_ENDPOINT is required.')

    agent_name = os.environ.get('AGENT_NAME', 'acl-remedy-advisor')
    client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    agent = client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=os.environ.get('AGENT_MODEL', 'chat'),
            instructions=INSTRUCTIONS,
            tools=[WebSearchTool(), CodeInterpreterTool()],
        ),
    )

    print(f'Agent created: {agent.name} (id: {agent.id}, version: {agent.version})')
    print('Return to the Foundry portal and follow the publishing steps in README.md.')


if __name__ == '__main__':
    run()
