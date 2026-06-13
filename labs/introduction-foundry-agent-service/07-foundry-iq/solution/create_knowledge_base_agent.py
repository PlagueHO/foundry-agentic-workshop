"""Recreate the Module 07 end state from code: a Foundry IQ knowledge base plus the
grounded acl-remedy-advisor Prompt Agent.

Use this script when you cannot complete Module 07 in the Foundry portal (for
example in a Codespace with network restrictions, or to reset an attendee project
to a known-good state). It reproduces what the UI walkthrough produces:

  1. Two Azure AI Search *knowledge sources* over the pre-seeded indexes
     (retail-products and retail-policies).
  2. A Foundry IQ *knowledge base* that combines both sources (extractive,
     minimal retrieval — no LLM, matching the README's Basic configuration).
  3. A Foundry project *connection* (RemoteTool / ProjectManagedIdentity) that
     targets the knowledge base MCP endpoint.
  4. A new *version* of the acl-remedy-advisor Prompt Agent that attaches the
     knowledge base as an MCP tool alongside Web search, Code Interpreter, and
     the retail-remedy-ops MCP server, with tool-routing instructions.

The script is idempotent in the meaningful sense: knowledge sources, the
knowledge base, and the project connection are create-or-update operations, so
re-running never creates duplicates. Creating an agent version always produces a
new version (exactly like clicking Save in the portal) and converges on the same
desired configuration.

Prerequisites:
  - The retail-products and retail-policies indexes exist and are populated
    (scripts/seed-product-index.py and scripts/seed-document-index.py).
  - Your account (or the AZURE_SEARCH_ADMIN_KEY) has Search Service Contributor
    on the search service to create knowledge sources and the knowledge base.
  - Your account has Foundry Project Manager to create the project connection.
  - The Foundry project's managed identity has Search Index Data Reader on the
    search service (assigned automatically by infra/main.bicep).

Required environment variables (.env):
  FOUNDRY_PROJECT_ENDPOINT   Project endpoint, e.g.
                             https://<resource>.services.ai.azure.com/api/projects/<project>
  AZURE_SEARCH_SERVICE_NAME  Azure AI Search service name (azd output).
  KNOWLEDGE_BASE_NAME        Knowledge base name, e.g.
                             acl-remedy-knowledge-lab-attendee-1
  AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, FOUNDRY_RESOURCE_NAME,
  FOUNDRY_PROJECT_NAME       Used to build the project resource ID for the
                             connection (or set FOUNDRY_PROJECT_RESOURCE_ID).

Optional environment variables:
  AGENT_NAME                 Default: acl-remedy-advisor
  AGENT_MODEL                Default: chat
  AZURE_SEARCH_PRODUCT_INDEX_NAME    Default: retail-products
  AZURE_SEARCH_DOCUMENT_INDEX_NAME   Default: retail-policies
  AZURE_SEARCH_ADMIN_KEY     If set, used instead of DefaultAzureCredential for
                             search control-plane calls.
  KNOWLEDGE_BASE_CONNECTION_NAME     Default: <KNOWLEDGE_BASE_NAME>-mcp
  MCP_SERVER_URL             retail-remedy-ops MCP URL (Module 06). When set, the
                             agent also gets the retail-remedy-ops tool.
  MCP_SERVER_LABEL           Default: retail_remedy_ops
  FOUNDRY_PROJECT_RESOURCE_ID         Override the constructed ARM resource ID.
  FOUNDRY_CONNECTION_API_VERSION      Default: 2025-10-01-preview
  KB_MCP_API_VERSION         Default: 2026-05-01-preview
  SKIP_PROJECT_CONNECTION    Set to 'true' if the connection already exists (for
                             example created in the portal); the script reuses
                             KNOWLEDGE_BASE_CONNECTION_NAME without recreating it.

Usage:
    python labs/introduction-foundry-agent-service/07-foundry-iq/solution/create_knowledge_base_agent.py
"""

import os

import requests
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeInterpreterTool,
    MCPTool,
    PromptAgentDefinition,
    WebSearchTool,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    KnowledgeBase,
    KnowledgeSourceReference,
    SearchIndexKnowledgeSource,
    SearchIndexKnowledgeSourceParameters,
)
from dotenv import load_dotenv

# Semantic configuration names created by the workshop seed scripts.
_PRODUCT_SEMANTIC_CONFIG = 'retail-product-semantic-config'
_POLICY_SEMANTIC_CONFIG = 'retail-policy-semantic-config'

# Knowledge source names as shown in the README walkthrough.
_PRODUCT_SOURCE_NAME = 'retail-products'
_POLICY_SOURCE_NAME = 'retail-policies'

# The single MCP tool that Azure AI Search knowledge bases expose to agents.
_KB_RETRIEVE_TOOL = 'knowledge_base_retrieve'

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
    'precisely and show your working.\n'
    '\n'
    'When a staff member provides a receipt ID, order ID, or customer ID — or\n'
    'asks you to look up a purchase, verify an order, or open a support case —\n'
    'use the retail-remedy-ops tools to perform that operational lookup or\n'
    'action. Never invent receipt, order, or case details; always retrieve them\n'
    'with the tools.\n'
    '\n'
    'When answering questions about specific products available in the store —\n'
    'including product names, descriptions, categories, prices, ratings, or\n'
    'stock availability — use the knowledge base to retrieve accurate product\n'
    'information and cite the source in your response.\n'
    '\n'
    'When answering questions about store policies — including return windows,\n'
    'refund eligibility, warranty coverage, loyalty program rules, or\n'
    'store-brand guarantees — use the knowledge base to retrieve the relevant\n'
    'policy and quote it directly.\n'
    '\n'
    'Prefer knowledge base retrieval over your training knowledge for all\n'
    'product and policy questions. The knowledge base reflects the store\'s\n'
    'current catalog and policies, not general retail conventions.\n'
    '\n'
    'To summarise tool routing: use the retail-remedy-ops tools for operational\n'
    'lookups and actions, the knowledge base for product and policy questions,\n'
    'web search for current ACCC and Australian Consumer Law guidance, and code\n'
    'interpreter for refund, depreciation, pro-rata, or price calculations.'
)


def _build_search_credential():
    """Use an admin key when provided, otherwise DefaultAzureCredential (RBAC)."""
    admin_key = os.getenv('AZURE_SEARCH_ADMIN_KEY', '').strip()
    if admin_key:
        return AzureKeyCredential(admin_key)
    return DefaultAzureCredential()


def _project_resource_id() -> str:
    """Return the ARM resource ID for the Foundry project connection step."""
    explicit = os.getenv('FOUNDRY_PROJECT_RESOURCE_ID', '').strip()
    if explicit:
        return explicit

    missing = [
        name
        for name in ('AZURE_SUBSCRIPTION_ID', 'AZURE_RESOURCE_GROUP', 'FOUNDRY_RESOURCE_NAME', 'FOUNDRY_PROJECT_NAME')
        if not os.getenv(name, '').strip()
    ]
    if missing:
        raise ValueError(
            'Cannot build the project resource ID. Set FOUNDRY_PROJECT_RESOURCE_ID, or set these '
            f'variables in your .env file: {", ".join(missing)}.'
        )

    subscription = os.environ['AZURE_SUBSCRIPTION_ID']
    resource_group = os.environ['AZURE_RESOURCE_GROUP']
    account = os.environ['FOUNDRY_RESOURCE_NAME']
    project = os.environ['FOUNDRY_PROJECT_NAME']
    return (
        f'/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/'
        f'Microsoft.CognitiveServices/accounts/{account}/projects/{project}'
    )


def _ensure_knowledge_sources(index_client: SearchIndexClient, product_index: str, policy_index: str) -> list[str]:
    """Create or update the two search-index knowledge sources. Returns their names."""
    sources = [
        SearchIndexKnowledgeSource(
            name=_PRODUCT_SOURCE_NAME,
            description=(
                'Retail product catalog: specifications, compatibility, and feature details for store products.'
            ),
            search_index_parameters=SearchIndexKnowledgeSourceParameters(
                search_index_name=product_index,
                semantic_configuration_name=_PRODUCT_SEMANTIC_CONFIG,
            ),
        ),
        SearchIndexKnowledgeSource(
            name=_POLICY_SOURCE_NAME,
            description=(
                'Store policies: returns, refunds, warranties, loyalty program, and store-brand guarantees.'
            ),
            search_index_parameters=SearchIndexKnowledgeSourceParameters(
                search_index_name=policy_index,
                semantic_configuration_name=_POLICY_SEMANTIC_CONFIG,
            ),
        ),
    ]

    for source in sources:
        index_client.create_or_update_knowledge_source(source)
        print(f'Knowledge source ready: {source.name}')

    return [source.name for source in sources]


def _ensure_knowledge_base(index_client: SearchIndexClient, kb_name: str, source_names: list[str]) -> None:
    """Create or update the knowledge base combining the knowledge sources."""
    knowledge_base = KnowledgeBase(
        name=kb_name,
        description='Retail product catalog and store policy knowledge for the ACL Remedy Advisor agent.',
        knowledge_sources=[KnowledgeSourceReference(name=name) for name in source_names],
        encryption_key=None,
    )
    index_client.create_or_update_knowledge_base(knowledge_base)
    print(f'Knowledge base ready: {kb_name} (sources: {", ".join(source_names)})')


def _ensure_project_connection(connection_name: str, mcp_endpoint: str) -> None:
    """Create or update the RemoteTool project connection to the knowledge base MCP endpoint."""
    api_version = os.getenv('FOUNDRY_CONNECTION_API_VERSION', '2025-10-01-preview').strip()
    resource_id = _project_resource_id()

    credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(credential, 'https://management.azure.com/.default')

    url = (
        f'https://management.azure.com{resource_id}/connections/{connection_name}'
        f'?api-version={api_version}'
    )
    body = {
        'name': connection_name,
        'properties': {
            'authType': 'ProjectManagedIdentity',
            'category': 'RemoteTool',
            'target': mcp_endpoint,
            'isSharedToAll': True,
            'audience': 'https://search.azure.com/',
            'metadata': {'ApiType': 'Azure'},
        },
    }

    response = requests.put(
        url,
        headers={'Authorization': f'Bearer {token_provider()}'},
        json=body,
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(
            f'Failed to create the project connection (HTTP {response.status_code}): {response.text}\n'
            'If the connection already exists (for example created in the portal), set '
            'SKIP_PROJECT_CONNECTION=true and re-run. You may also need to adjust '
            'FOUNDRY_CONNECTION_API_VERSION or FOUNDRY_PROJECT_RESOURCE_ID for your environment.'
        )
    print(f'Project connection ready: {connection_name}')


def run() -> None:
    load_dotenv()

    endpoint = os.environ['FOUNDRY_PROJECT_ENDPOINT']
    agent_name = os.environ.get('AGENT_NAME', 'acl-remedy-advisor')
    agent_model = os.environ.get('AGENT_MODEL', 'chat')
    kb_name = os.environ.get('KNOWLEDGE_BASE_NAME', '').strip()
    search_service = os.environ.get('AZURE_SEARCH_SERVICE_NAME', '').strip()
    product_index = os.environ.get('AZURE_SEARCH_PRODUCT_INDEX_NAME', 'retail-products').strip()
    policy_index = os.environ.get('AZURE_SEARCH_DOCUMENT_INDEX_NAME', 'retail-policies').strip()

    if not kb_name:
        raise ValueError(
            'KNOWLEDGE_BASE_NAME is not set. Set it to your per-attendee knowledge base name in .env, '
            'for example: KNOWLEDGE_BASE_NAME=acl-remedy-knowledge-lab-attendee-1'
        )
    if not search_service:
        raise ValueError(
            'AZURE_SEARCH_SERVICE_NAME is not set. Set it to your Azure AI Search service name in .env.'
        )

    search_endpoint = f'https://{search_service}.search.windows.net'
    kb_api_version = os.getenv('KB_MCP_API_VERSION', '2026-05-01-preview').strip()
    mcp_endpoint = f'{search_endpoint}/knowledgebases/{kb_name}/mcp?api-version={kb_api_version}'
    connection_name = os.getenv('KNOWLEDGE_BASE_CONNECTION_NAME', f'{kb_name}-mcp').strip()

    # 1 + 2. Knowledge sources and knowledge base (Azure AI Search control plane).
    index_client = SearchIndexClient(endpoint=search_endpoint, credential=_build_search_credential())
    source_names = _ensure_knowledge_sources(index_client, product_index, policy_index)
    _ensure_knowledge_base(index_client, kb_name, source_names)

    # 3. Project connection that the agent uses to reach the knowledge base MCP endpoint.
    if os.getenv('SKIP_PROJECT_CONNECTION', '').strip().lower() == 'true':
        print(f'Skipping project connection creation; reusing existing connection: {connection_name}')
    else:
        _ensure_project_connection(connection_name, mcp_endpoint)

    # 4. Agent version with the knowledge base plus the existing tools.
    tools = [
        WebSearchTool(),
        CodeInterpreterTool(),
        MCPTool(
            server_label='knowledge_base',
            server_url=mcp_endpoint,
            require_approval='never',
            allowed_tools=[_KB_RETRIEVE_TOOL],
            project_connection_id=connection_name,
        ),
    ]

    mcp_server_url = os.environ.get('MCP_SERVER_URL', '').strip()
    mcp_server_label = os.environ.get('MCP_SERVER_LABEL', 'retail_remedy_ops')
    if mcp_server_url:
        tools.append(
            MCPTool(
                server_label=mcp_server_label,
                server_url=mcp_server_url,
                require_approval='never',
            )
        )
        print(f'Including retail-remedy-ops MCP tool: {mcp_server_label} at {mcp_server_url}')
    else:
        print(
            'MCP_SERVER_URL is not set — creating the agent without the retail-remedy-ops tool. '
            'Set MCP_SERVER_URL (Module 06) and re-run to include it.'
        )

    client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    agent = client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=agent_model,
            instructions=INSTRUCTIONS,
            tools=tools,
        ),
    )

    print(f'Agent created: {agent.name} (id: {agent.id}, version: {agent.version})')
    print(f'Knowledge base attached via connection: {connection_name}')
    print(f'You can now open {agent.name} in the Foundry playground and test grounded retrieval.')


if __name__ == '__main__':
    run()
