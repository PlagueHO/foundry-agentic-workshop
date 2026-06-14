"""Hosted acl-remedy-advisor-hosted agent entry point (Module 09).

This module builds the ACL Remedy Advisor as an Agent Framework agent and exposes
it over the Foundry hosted-agent contract using ``ResponsesHostServer``. Foundry runs
this container, sends requests to the OpenAI Responses endpoint on port 8088, and
probes ``/readiness`` automatically.

The six retail tools are bundled in-process (see ``retail_tools.py``) — no MCP server to
run or dev tunnel to expose. The agent also enables the Foundry hosted **web search** and
**code interpreter** tools, matching the tool set of the ``acl-remedy-advisor`` Prompt Agent
from Modules 05-06.

Unlike the Module 07 Prompt Agent, this hosted agent does not call the Foundry IQ knowledge
base. A hosted agent runs as its own Microsoft Entra identity, which cannot be granted
data-plane access to the RBAC-only Azure AI Search service in this preview — so product and
policy lookups are bundled in-process (``get_product_profile`` and ``search_store_policy``)
instead.

Environment variables (provided by Foundry at runtime, and by your ``.env`` locally):
    FOUNDRY_PROJECT_ENDPOINT        The Foundry project endpoint.
    AZURE_AI_MODEL_DEPLOYMENT_NAME  The chat model deployment name (for example "chat").
"""

import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential

from retail_tools import RETAIL_TOOLS

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
    'Use the bundled retail tools to ground your guidance in real store data:\n'
    '- lookup_purchase: fetch a purchase record by receipt ID.\n'
    '- get_product_profile: fetch product category, expected lifespan, and warranty.\n'
    '- search_store_policy: retrieve the relevant ACL store policy excerpt.\n'
    '- find_replacement_options: list comparable in-stock replacements.\n'
    '- draft_remedy_summary: compile a structured staff-facing remedy summary.\n'
    '- create_remedy_case: log an approved remedy outcome (simulated).\n'
    '\n'
    'When assessing a situation consider the type of product and its expected\n'
    'lifespan, the price paid, how long the customer has had the product, and what\n'
    'a reasonable consumer would expect.\n'
    '\n'
    'Use web search to ground your guidance in current ACCC guidance at\n'
    'accc.gov.au and always cite your sources with links.\n'
    '\n'
    'When asked to calculate refund amounts, depreciation, pro-rata warranty\n'
    'values, or compare prices, use code interpreter to perform the calculation\n'
    'precisely and show your working.\n'
    '\n'
    'Always state clearly that you provide general guidance, not legal advice, and\n'
    'that "no refund" signs are unlawful under the ACL.\n'
    '\n'
    'Be concise and practical — retail staff need fast, clear answers in a busy\n'
    'store environment.'
)


def build_agent() -> Agent:
    """Create the ACL Remedy Advisor agent with the bundled retail tools."""
    client = FoundryChatClient(
        project_endpoint=os.environ['FOUNDRY_PROJECT_ENDPOINT'],
        model=os.environ['AZURE_AI_MODEL_DEPLOYMENT_NAME'],
        credential=DefaultAzureCredential(),
    )

    return Agent(
        client=client,
        name='acl-remedy-advisor-hosted',
        instructions=INSTRUCTIONS,
        # Modules 05-06 tool set: the six in-process retail tools plus the Foundry hosted
        # web search and code interpreter tools (served by the model). The Module 07 Foundry
        # IQ knowledge base is replaced by the in-process product and policy lookups above.
        tools=[
            *RETAIL_TOOLS,
            client.get_web_search_tool(),
            client.get_code_interpreter_tool(),
        ],
        # Foundry hosted agents are stateless at the model layer; conversation state is
        # managed by the Responses host, so the chat client must not persist responses.
        default_options={'store': False},
    )


def main() -> None:
    server = ResponsesHostServer(build_agent())
    server.run()


if __name__ == '__main__':
    main()
