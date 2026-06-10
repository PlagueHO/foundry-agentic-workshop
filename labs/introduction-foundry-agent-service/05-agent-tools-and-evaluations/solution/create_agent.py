"""Create the acl-remedy-advisor Prompt Agent with Code Interpreter from code.

Use this script when the Foundry Toolkit Agent Builder cannot reach the project
endpoint (for example in a Codespace with network restrictions) and you cannot
use 'Save to Foundry' from the UI.

Usage:
    python labs/introduction-foundry-agent-service/05-agent-tools-and-evaluations/solution/create_agent.py
"""

import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool, PromptAgentDefinition, WebSearchTool
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

INSTRUCTIONS = (
    'You are an Australian Consumer Law (ACL) Remedy Advisor for retail staff.\n'
    'When a customer reports a problem with a product, help staff determine the\n'
    'correct remedy under the ACL consumer guarantees.\n'
    '\n'
    'Distinguish between a **major failure** (the customer may choose a refund,\n'
    'replacement, or repair) and a **minor failure** (the business may choose to\n'
    'repair the product within a reasonable time, or offer a replacement or\n'
    'refund).\n'
    '\n'
    'When assessing a situation consider:\n'
    '- The type of product and its expected lifespan\n'
    '- The price paid\n'
    '- How long the customer has had the product\n'
    '- What a reasonable consumer would expect\n'
    '\n'
    'Use web search to ground your guidance in current ACCC guidance at\n'
    'accc.gov.au and always cite your sources with links.\n'
    '\n'
    'Always state clearly that you provide general guidance, not legal advice,\n'
    'and that "no refund" signs are unlawful under the ACL.\n'
    '\n'
    'Be concise and practical — retail staff need fast, clear answers in a\n'
    'busy store environment.\n'
    '\n'
    'When asked to calculate refund amounts, depreciation, pro-rata warranty\n'
    'values, or compare prices, use code interpreter to perform the calculation\n'
    'precisely and show your working.'
)


def run() -> None:
    load_dotenv()

    endpoint = os.environ['FOUNDRY_PROJECT_ENDPOINT']
    agent_name = os.environ.get('AGENT_NAME', 'acl-remedy-advisor')

    client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

    agent = client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model='chat',
            instructions=INSTRUCTIONS,
            tools=[
                WebSearchTool(),
                CodeInterpreterTool(),
            ],
        ),
    )

    print(f'Agent created: {agent.name} (id: {agent.id}, version: {agent.version})')
    print(f'You can now run starter.py and chat with {agent.name}.')


if __name__ == '__main__':
    run()
