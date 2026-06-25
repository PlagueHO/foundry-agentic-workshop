"""Hosted acl-remedy-advisor-hosted agent entry point (Module 09).

This module builds the ACL Remedy Advisor as an Agent Framework agent and exposes
it over the Foundry hosted-agent contract using ``ResponsesHostServer``. Foundry runs
this container, sends requests to the OpenAI Responses endpoint on port 8088, and
probes ``/readiness`` automatically.

The agent calls the live **Retail Remedy Operations MCP server** from Module 06 over
``RETAIL_REMEDY_OPS_MCP_SERVER_URL`` (the same public dev-tunnel endpoint you used there), and also enables
the Foundry hosted **web search** and **code interpreter** tools - matching the tool set of
the ``acl-remedy-advisor`` Prompt Agent from Module 06.

Because the MCP server is anonymous (no auth), the hosted agent needs no extra permissions
to reach it; it only needs outbound network access to the public tunnel URL. The MCP server
must be running and publicly exposed before you deploy or invoke this agent (see Module 06,
Part 2). The dev-tunnel URL is baked into the deploy as an environment variable, so if the
tunnel changes you must redeploy the agent.

Environment variables (provided by Foundry at runtime, and by your ``.env`` locally):
    FOUNDRY_PROJECT_ENDPOINT        The Foundry project endpoint.
    AZURE_AI_MODEL_DEPLOYMENT_NAME  The chat model deployment name (for example "chat").
    RETAIL_REMEDY_OPS_MCP_SERVER_URL   Public URL of the Retail Remedy Operations MCP server,
                                    ending in ``/mcp`` (from Module 06).
    RETAIL_REMEDY_OPS_MCP_SERVER_LABEL  Tool name for the MCP server (default "retail_remedy_ops").
"""

import os

from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential

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
    'Use the retail operations MCP tools to ground your guidance in real store data:\n'
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
    'Be concise and practical - retail staff need fast, clear answers in a busy\n'
    'store environment.'
)


def build_agent() -> Agent:
    """Create the ACL Remedy Advisor agent wired to the live Module 06 MCP server."""
    mcp_server_url = os.environ.get('RETAIL_REMEDY_OPS_MCP_SERVER_URL', '').strip()
    if not mcp_server_url:
        raise ValueError(
            'RETAIL_REMEDY_OPS_MCP_SERVER_URL is not set. Start the Retail Remedy Operations MCP server '
            '(Module 06, server.py), expose it via a dev tunnel, then set RETAIL_REMEDY_OPS_MCP_SERVER_URL to '
            'the public URL plus /mcp. Example: '
            'RETAIL_REMEDY_OPS_MCP_SERVER_URL=https://abc123-8080.devtunnels.ms/mcp'
        )

    client = FoundryChatClient(
        project_endpoint=os.environ['FOUNDRY_PROJECT_ENDPOINT'],
        model=os.environ['AZURE_AI_MODEL_DEPLOYMENT_NAME'],
        credential=DefaultAzureCredential(),
    )

    # Module 06 tool set: the live retail_remedy_ops MCP server plus the Foundry hosted web
    # search and code interpreter tools (served by the model). The MCP server is anonymous,
    # so the hosted agent only needs outbound access to the public tunnel URL - no RBAC.
    retail_remedy_ops = MCPStreamableHTTPTool(
        name=os.environ.get('RETAIL_REMEDY_OPS_MCP_SERVER_LABEL', 'retail_remedy_ops'),
        url=mcp_server_url,
        load_prompts=False,
        approval_mode='never_require',
    )

    return Agent(
        client=client,
        name='acl-remedy-advisor-hosted',
        instructions=INSTRUCTIONS,
        tools=[
            retail_remedy_ops,
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
