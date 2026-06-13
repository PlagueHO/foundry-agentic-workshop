"""Consume the acl-remedy-toolbox from code using the Microsoft Agent Framework.

This capstone builds on Module 08, where you first used the **Microsoft Agent
Framework**. Here you reuse the same ``FoundryChatClient`` and ``Agent`` patterns,
but point the agent at the toolbox's MCP endpoint and let the model use Tool Search
to discover and call the toolbox tools (web search, the Retail Remedy Operations MCP
server, and code interpreter).

Why code instead of the portal? A Foundry Prompt Agent cannot attach the toolbox MCP
endpoint with the required custom header, so the toolbox is consumed from an Agent
Framework agent that controls its own HTTP headers and Microsoft Entra authentication.

How it works:
  1. Build an httpx client that adds a fresh Microsoft Entra bearer token and the
     ``Foundry-Features: Toolboxes=V1Preview`` header to every request. Both are
     required on the initial MCP handshake, not just on tool calls.
  2. Wrap the toolbox MCP endpoint in an ``MCPStreamableHTTPTool`` and give it to an
     Agent backed by ``FoundryChatClient``.
  3. Ask a question. With Tool Search enabled the agent first calls ``tool_search`` to
     find the right toolbox tool, then ``call_tool`` to run it.

Prerequisites:
  - The acl-remedy-toolbox exists in your project with Web Search, the Retail Remedy
    Operations MCP server, and Tool Search enabled (Module 10, Part 2).
  - The Retail Remedy Operations MCP server is running and reachable from the toolbox
    (see Module 06 README, Part 2).
  - FOUNDRY_PROJECT_ENDPOINT set in your .env file to the project endpoint, for example:
    https://aif-foundry-hol.services.ai.azure.com/api/projects/lab-attendee-1

Usage:
    python labs/introduction-foundry-agent-service/10-foundry-toolboxes/solution/consume_toolbox.py
"""

import asyncio
import os
from collections.abc import Generator

import httpx
from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.exceptions import ToolException
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

MODEL = 'chat'
TOOLBOX_API_SCOPE = 'https://ai.azure.com/.default'
TOOLBOX_FEATURES_HEADER = 'Toolboxes=V1Preview'

CONNECT_ATTEMPTS = 3
CONNECT_BACKOFF_SECONDS = 3.0

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
    'Be concise and practical — retail staff need fast, clear answers in a\n'
    'busy store environment.\n'
    '\n'
    'When asked to calculate refund amounts, depreciation, pro-rata warranty\n'
    'values, or compare prices, use code interpreter to perform the calculation\n'
    'precisely and show your working.\n'
    '\n'
    'You have access to a toolbox that provides retail operations tools and web search.\n'
    'When you need a tool that is not already in your tool list, call tool_search with a\n'
    'natural-language description of the capability you need before responding that you\n'
    'cannot help.\n'
    '\n'
    'Use the retail operations tools when a question includes a receipt ID, customer ID,\n'
    'or product ID, or when staff ask about store policy, warranty details, or replacement\n'
    'availability. Use web search to look up ACCC rulings, Australian Consumer Law guidance,\n'
    'or current retail policy information. Use code interpreter to perform calculations such\n'
    'as pro-rata refund amounts.\n'
    '\n'
    'Do not invent purchase, warranty, policy, or stock details — always call tool_search\n'
    'first if the tool you need is not already visible, then use the discovered tool.'
)

QUERY = (
    'A customer is at the counter with receipt R-1007. Their ProBook 14 laptop '
    'battery stopped holding charge about 14 months after purchase. The standard '
    'warranty was 12 months. What remedy should we offer and why?'
)


class _ToolboxAuth(httpx.Auth):
    """Attach a fresh Microsoft Entra bearer token to every toolbox request."""

    def __init__(self, credential: DefaultAzureCredential) -> None:
        self._credential = credential

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        token = self._credential.get_token(TOOLBOX_API_SCOPE).token
        request.headers['Authorization'] = f'Bearer {token}'
        yield request


def _build_toolbox(credential: DefaultAzureCredential, toolbox_url: str) -> MCPStreamableHTTPTool:
    """Create an MCP tool for the toolbox with connection-level auth and the preview header.

    The Foundry-Features header and bearer token must be present on every request,
    including the initial MCP handshake, so they are set on the httpx client itself
    rather than per tool call.
    """
    http_client = httpx.AsyncClient(
        auth=_ToolboxAuth(credential),
        headers={'Foundry-Features': TOOLBOX_FEATURES_HEADER},
        timeout=120.0,
    )
    return MCPStreamableHTTPTool(
        name='acl_remedy_toolbox',
        url=toolbox_url,
        http_client=http_client,
        load_prompts=False,
        approval_mode='never_require',
    )


async def _ask(
    credential: DefaultAzureCredential,
    client: FoundryChatClient,
    toolbox_url: str,
    agent_name: str,
    query: str,
):
    """Connect to the toolbox and run a single query, returning the agent response."""
    toolbox = _build_toolbox(credential, toolbox_url)
    async with Agent(
        client=client,
        name=agent_name,
        instructions=INSTRUCTIONS,
        tools=[toolbox],
    ) as agent:
        return await agent.run(query)


async def _ask_with_retry(
    credential: DefaultAzureCredential,
    client: FoundryChatClient,
    toolbox_url: str,
    agent_name: str,
    query: str,
):
    """Run the query, retrying the initial toolbox connection on transient failures.

    The toolbox MCP endpoint can intermittently cancel the first handshake when it is
    cold. A small number of retries makes the lab reliable without hiding real errors.
    """
    last_error: ToolException | None = None
    for attempt in range(1, CONNECT_ATTEMPTS + 1):
        try:
            return await _ask(credential, client, toolbox_url, agent_name, query)
        except ToolException as exc:
            last_error = exc
            if attempt < CONNECT_ATTEMPTS:
                print(
                    f'Toolbox connection attempt {attempt} of {CONNECT_ATTEMPTS} failed; '
                    f'retrying in {CONNECT_BACKOFF_SECONDS:.0f}s ...'
                )
                await asyncio.sleep(CONNECT_BACKOFF_SECONDS)
    raise RuntimeError(
        'Could not connect to the toolbox after '
        f'{CONNECT_ATTEMPTS} attempts. Confirm the toolbox exists, the Retail Remedy '
        'Operations MCP server is running and reachable, and FOUNDRY_PROJECT_ENDPOINT '
        'is correct.'
    ) from last_error


async def run() -> None:
    load_dotenv()

    endpoint = os.environ['FOUNDRY_PROJECT_ENDPOINT']
    agent_name = os.environ.get('AGENT_NAME', 'acl-remedy-advisor')
    toolbox_name = os.environ.get('TOOLBOX_NAME', 'acl-remedy-toolbox')
    toolbox_url = f'{endpoint.rstrip("/")}/toolboxes/{toolbox_name}/mcp?api-version=v1'

    credential = DefaultAzureCredential()
    client = FoundryChatClient(project_endpoint=endpoint, model=MODEL, credential=credential)

    print(f'Connecting to toolbox: {toolbox_url}')
    result = await _ask_with_retry(credential, client, toolbox_url, agent_name, QUERY)

    print('\n===== AGENT RESPONSE =====\n')
    print(result.text)


if __name__ == '__main__':
    asyncio.run(run())
