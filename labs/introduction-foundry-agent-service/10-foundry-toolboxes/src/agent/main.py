"""Hosted acl-remedy-advisor-hosted agent entry point, toolbox edition (Module 10).

This module rebuilds the Module 09 ACL Remedy Advisor as an Agent Framework agent whose
**only** tool is the ``acl-remedy-toolbox`` Foundry Toolbox, then serves it over the Foundry
hosted-agent contract with ``ResponsesHostServer``. Deploying it as a new source-code version
of ``acl-remedy-advisor-hosted-code`` swaps the three separately wired tools from Module 09
(the ``retail_remedy_ops`` MCP server, web search, and code interpreter) for a single toolbox
endpoint that bundles all of them behind Tool Search.

How the toolbox is consumed:
  - The toolbox is exposed as an MCP endpoint secured with Microsoft Entra authentication.
    Every request - including the initial MCP handshake - must carry an Entra bearer token
    (scope ``https://ai.azure.com/.default``) and the preview header
    ``Foundry-Features: Toolboxes=V1Preview``.
  - Both are attached at the httpx-client level so they are present on every request, then the
    toolbox endpoint is wrapped in an ``MCPStreamableHTTPTool`` and given to the ``Agent``.
  - Inside the hosted container, ``DefaultAzureCredential`` resolves to the agent's own
    per-deploy Microsoft Entra identity, which holds the Foundry User role - sufficient to
    authenticate to the toolbox endpoint on the same scope it already uses to call the model.

Environment variables (provided by Foundry at runtime, and by your ``.env`` locally):
    FOUNDRY_PROJECT_ENDPOINT        The Foundry project endpoint (injected by Foundry).
    AZURE_AI_MODEL_DEPLOYMENT_NAME  The chat model deployment name (for example "chat").
    TOOLBOX_NAME                    The toolbox name (default "acl-remedy-toolbox").
"""

import os
from collections.abc import Generator

import httpx
from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential

TOOLBOX_API_SCOPE = 'https://ai.azure.com/.default'
TOOLBOX_FEATURES_HEADER = 'Toolboxes=V1Preview'

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
    'You have access to a toolbox that provides retail operations tools, web search,\n'
    'and code interpreter. When you need a tool that is not already in your tool list,\n'
    'call tool_search with a natural-language description of the capability you need\n'
    'before responding that you cannot help.\n'
    '\n'
    'Use the retail operations tools when a question includes a receipt ID, customer ID,\n'
    'or product ID, or when staff ask about store policy, warranty details, or replacement\n'
    'availability. Use web search to look up ACCC rulings, Australian Consumer Law guidance,\n'
    'or current retail policy information. Use code interpreter to perform calculations such\n'
    'as pro-rata refund amounts.\n'
    '\n'
    'Do not invent purchase, warranty, policy, or stock details - always call tool_search\n'
    'first if the tool you need is not already visible, then use the discovered tool.'
)


class _ToolboxAuth(httpx.Auth):
    """Attach a fresh Microsoft Entra bearer token to every toolbox request."""

    def __init__(self, credential: DefaultAzureCredential) -> None:
        self._credential = credential

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        token = self._credential.get_token(TOOLBOX_API_SCOPE).token
        request.headers['Authorization'] = f'Bearer {token}'
        yield request


def build_agent() -> Agent:
    """Create the ACL Remedy Advisor agent wired to the acl-remedy-toolbox toolbox."""
    endpoint = os.environ['FOUNDRY_PROJECT_ENDPOINT']
    toolbox_name = os.environ.get('TOOLBOX_NAME', 'acl-remedy-toolbox')
    toolbox_url = f'{endpoint.rstrip("/")}/toolboxes/{toolbox_name}/mcp?api-version=v1'

    # One credential serves both the model client and the toolbox bearer token. Inside the
    # hosted container this resolves to the agent's own per-deploy Microsoft Entra identity.
    credential = DefaultAzureCredential()

    client = FoundryChatClient(
        project_endpoint=endpoint,
        model=os.environ['AZURE_AI_MODEL_DEPLOYMENT_NAME'],
        credential=credential,
    )

    # The Foundry-Features header and bearer token must be present on every request, including
    # the initial MCP handshake, so they are set on the httpx client rather than per tool call.
    http_client = httpx.AsyncClient(
        auth=_ToolboxAuth(credential),
        headers={'Foundry-Features': TOOLBOX_FEATURES_HEADER},
        timeout=120.0,
    )
    toolbox = MCPStreamableHTTPTool(
        name='acl_remedy_toolbox',
        url=toolbox_url,
        http_client=http_client,
        load_prompts=False,
        approval_mode='never_require',
    )

    return Agent(
        client=client,
        name='acl-remedy-advisor-hosted',
        instructions=INSTRUCTIONS,
        tools=[toolbox],
        # Foundry hosted agents are stateless at the model layer; conversation state is
        # managed by the Responses host, so the chat client must not persist responses.
        default_options={'store': False},
    )


def main() -> None:
    server = ResponsesHostServer(build_agent())
    server.run()


if __name__ == '__main__':
    main()
