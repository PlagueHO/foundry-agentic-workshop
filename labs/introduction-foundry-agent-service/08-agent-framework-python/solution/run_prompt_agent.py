"""Lab 08 solution - run the Module 07 Prompt Agent with the Microsoft Agent Framework.

This is the completed version of src/starter.py. It connects to the
acl-remedy-advisor Prompt Agent built in Modules 04-07 and runs it from Python
using the Agent Framework's FoundryAgent client, which binds to an agent that
already exists in Foundry - its model, instructions, and tools all live on the
service. You only connect and run.

The first call returns the complete response in one piece; the second streams the
response as it is generated. Both runs appear under the agent's Traces tab in the
Foundry portal, exactly like a playground conversation.

Prerequisites:
  - acl-remedy-advisor exists in your Foundry project. If you did not finish
    Module 07, recreate its end state first:
        python labs/introduction-foundry-agent-service/08-agent-framework-python/solution/create_knowledge_base_agent.py
  - Sign in with the Azure CLI so DefaultAzureCredential can authenticate:
        az login
  - FOUNDRY_PROJECT_ENDPOINT (and optionally AGENT_NAME / AGENT_VERSION) are set
    in your .env file.

Environment variables (.env):
  FOUNDRY_PROJECT_ENDPOINT   Project endpoint, e.g.
                             https://<resource>.services.ai.azure.com/api/projects/<project>
  AGENT_NAME                 Default: acl-remedy-advisor
  AGENT_VERSION              Optional. Leave empty to use the latest published
                             version; set it to pin a specific version.

Usage:
    python labs/introduction-foundry-agent-service/08-agent-framework-python/solution/run_prompt_agent.py
"""

import asyncio
import os

from agent_framework.foundry import FoundryAgent
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# A retail-staff question the acl-remedy-advisor agent is designed to answer.
QUERY = (
    'A customer returned a $1,200 fridge that stopped cooling after 14 months. '
    'The store warranty was 12 months. What remedy should we offer under the '
    'Australian Consumer Law, and why?'
)


async def run() -> None:
    load_dotenv()

    endpoint = os.environ['FOUNDRY_PROJECT_ENDPOINT']
    agent_name = os.environ.get('AGENT_NAME', 'acl-remedy-advisor')
    # Leave AGENT_VERSION empty to use the latest published version of the agent.
    agent_version = os.environ.get('AGENT_VERSION', '').strip() or None

    # DefaultAzureCredential reuses your `az login` session - no keys in code.
    credential = DefaultAzureCredential()

    # Connect to the Prompt Agent that already exists in Foundry. The model,
    # instructions, and tools are configured on the service.
    agent = FoundryAgent(
        project_endpoint=endpoint,
        agent_name=agent_name,
        agent_version=agent_version,
        credential=credential,
    )

    # Single-response run: await the whole answer, then print it.
    result = await agent.run(QUERY)
    print(f'\nAgent:\n{result.text}\n')

    # Streaming run: print each chunk of text as the agent generates it.
    print('Agent (streaming): ', end='', flush=True)
    async for chunk in agent.run(QUERY, stream=True):
        if chunk.text:
            print(chunk.text, end='', flush=True)
    print('\n')

    credential.close()


if __name__ == '__main__':
    asyncio.run(run())
