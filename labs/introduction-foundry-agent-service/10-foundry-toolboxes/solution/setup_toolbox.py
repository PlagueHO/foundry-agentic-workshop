"""Create the acl-remedy-toolbox toolbox version from code.

Use this script when the Foundry portal does not yet expose the Toolboxes UI in
your region, or when you skipped the portal toolbox creation step in Module 10,
Part 1. It builds the same toolbox that consume_toolbox.py consumes with the
Microsoft Agent Framework.

The script:
  1. Creates the acl-remedy-toolbox toolbox version with Web Search, the Retail
     Remedy Operations MCP server, Code Interpreter, and Tool Search enabled.
  2. Prints the toolbox consumer endpoint URL.

Prerequisites:
  - MCP server running and publicly accessible via a dev tunnel or port
    forwarding (see Module 06 README, Part 2).
  - MCP_SERVER_URL set in your .env file to the public tunnel URL plus /mcp.
    Example: MCP_SERVER_URL=https://abc123-8080.devtunnels.ms/mcp

Usage:
    python labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/setup_toolbox.py
"""

import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeInterpreterTool,
    MCPTool,
    ToolboxSearchPreviewTool,
    WebSearchTool,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

TOOLBOX_DESCRIPTION = (
    'Retail Remedy operations tools, web search, and code interpreter for ACCC and ACL guidance'
)
WEB_SEARCH_DESCRIPTION = (
    'Search the web for ACCC rulings, Australian Consumer Law guidance, '
    'and current retail policy information.'
)
MCP_DESCRIPTION = (
    'Retail Remedy Operations tools for looking up purchases, product profiles, '
    'store policies, replacement options, and creating remedy cases.'
)


def run() -> None:
    load_dotenv()

    endpoint = os.environ['FOUNDRY_PROJECT_ENDPOINT']
    toolbox_name = os.environ.get('TOOLBOX_NAME', 'acl-remedy-toolbox')
    mcp_server_url = os.environ.get('MCP_SERVER_URL', '').strip()

    if not mcp_server_url:
        raise ValueError(
            'MCP_SERVER_URL is not set. Start the MCP server (server.py), expose it via a dev '
            'tunnel or port forward, then set MCP_SERVER_URL to the public URL plus /mcp in your '
            '.env file. Example: MCP_SERVER_URL=https://abc123-8080.devtunnels.ms/mcp'
        )

    client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

    # Create the toolbox version with Web Search, the MCP server, Code Interpreter, and Tool Search.
    print(f'Creating toolbox: {toolbox_name} ...')
    toolbox_version = client.beta.toolboxes.create_version(
        name=toolbox_name,
        description=TOOLBOX_DESCRIPTION,
        tools=[
            WebSearchTool(description=WEB_SEARCH_DESCRIPTION),
            MCPTool(
                server_label='retail_remedy_ops',
                server_url=mcp_server_url,
                require_approval='never',
                description=MCP_DESCRIPTION,
            ),
            CodeInterpreterTool(),
            ToolboxSearchPreviewTool(),
        ],
    )
    print(f'Toolbox created: {toolbox_version.name} (version: {toolbox_version.version})')

    # Derive the consumer endpoint URL used by consume_toolbox.py.
    toolbox_endpoint = (
        f'{endpoint.rstrip("/")}/toolboxes/{toolbox_name}/mcp?api-version=v1'
    )
    print(f'Toolbox consumer endpoint: {toolbox_endpoint}')
    print()
    print('Next steps:')
    print('  - Set this toolbox version as the default in the Foundry portal if it is not already.')
    print('  - Run consume_toolbox.py to query the toolbox with the Microsoft Agent Framework.')


if __name__ == '__main__':
    run()
