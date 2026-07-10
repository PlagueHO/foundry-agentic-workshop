"""Create the acl-remedy-advisor Prompt Agent with MCP tools from code.

Use this script when the Foundry Toolkit Agent Builder cannot reach the
project endpoint or the MCP server URL (for example in a Codespace with
network restrictions) and you cannot add the MCP tool through the UI.

Prerequisites:
  - MCP server running and publicly accessible via a dev tunnel or port
    forwarding (see Module 06 README, Part 2).
  - RETAIL_REMEDY_OPS_MCP_SERVER_URL set in your .env file to the public tunnel URL plus /mcp,
    for example: https://abc123-8080.devtunnels.ms/mcp

Usage:
    uv run python labs/introduction-foundry-agent-service/06-mcp-tools/solution/create_agent_with_mcp.py
"""

import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool, MCPTool, PromptAgentDefinition, WebSearchTool
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
    'Be concise and practical - retail staff need fast, clear answers in a\n'
    'busy store environment.\n'
    '\n'
    'When asked to calculate refund amounts, depreciation, pro-rata warranty\n'
    'values, or compare prices, use code interpreter to perform the calculation\n'
    'precisely and show your working.\n'
    '\n'
    'Use the retail operations MCP tools when a question includes a receipt ID,\n'
    'customer ID, or product ID, or when staff ask about store policy, warranty\n'
    'details, or replacement availability. Call lookup_purchase first to retrieve\n'
    'the purchase record, then get_product_profile for lifespan and warranty data,\n'
    'search_store_policy for relevant policy excerpts, and find_replacement_options\n'
    'if the customer may want a replacement. Use draft_remedy_summary to produce a\n'
    'structured summary for the staff member. Use create_remedy_case to log the\n'
    'outcome if the staff member confirms the remedy. Do not invent purchase,\n'
    'warranty, policy, or stock details - call the MCP tools instead.'
)


def run() -> None:
    load_dotenv()

    endpoint = os.environ['FOUNDRY_PROJECT_ENDPOINT']
    agent_name = os.environ.get('AGENT_NAME', 'acl-remedy-advisor')
    mcp_server_url = os.environ.get('RETAIL_REMEDY_OPS_MCP_SERVER_URL', '').strip()
    mcp_server_label = os.environ.get('RETAIL_REMEDY_OPS_MCP_SERVER_LABEL', 'retail_remedy_ops')

    if not mcp_server_url:
        raise ValueError(
            'RETAIL_REMEDY_OPS_MCP_SERVER_URL is not set. Start the MCP server (server.py), expose it via a dev '
            'tunnel or port forward, then set RETAIL_REMEDY_OPS_MCP_SERVER_URL to the public URL plus /mcp in your '
            '.env file. Example: RETAIL_REMEDY_OPS_MCP_SERVER_URL=https://abc123-8080.devtunnels.ms/mcp'
        )

    client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

    agent = client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model='chat',
            instructions=INSTRUCTIONS,
            tools=[
                WebSearchTool(),
                CodeInterpreterTool(),
                MCPTool(
                    server_label=mcp_server_label,
                    server_url=mcp_server_url,
                    require_approval='never',
                ),
            ],
        ),
    )

    print(f'Agent created: {agent.name} (id: {agent.id}, version: {agent.version})')
    print(f'MCP server connected: {mcp_server_label} at {mcp_server_url}')
    print(f'You can now run starter.py and chat with {agent.name}.')


if __name__ == '__main__':
    run()
