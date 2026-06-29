"""Lab 08 starter - run the Module 07 Prompt Agent with the Microsoft Agent Framework.

Fill in each numbered TODO with the matching code snippet from the lab README.
When every TODO is complete, this script connects to the acl-remedy-advisor
Prompt Agent you built in Modules 04-07 and runs it from Python - first as a
single response, then as a streamed response.

Prerequisites:
  - acl-remedy-advisor exists in your Foundry project. If you did not finish
    Module 07, recreate its end state from the solution folder first:
        python labs/introduction-foundry-agent-service/08-agent-framework-python/solution/create_knowledge_base_agent.py
  - Sign in with the Azure CLI so DefaultAzureCredential can authenticate:
        az login
  - FOUNDRY_PROJECT_ENDPOINT (and optionally AGENT_NAME / AGENT_VERSION) are set
    in your .env file.

Usage:
    python labs/introduction-foundry-agent-service/08-agent-framework-python/src/starter.py
"""

import asyncio
import os

from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# TODO 1: Import the FoundryAgent client from the Agent Framework Foundry package.
from agent_framework.foundry import FoundryAgent


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

    # TODO 2: Connect to the existing Prompt Agent by name.
    # Build a FoundryAgent from endpoint, agent_name, agent_version, and credential.
    agent = FoundryAgent(
        project_endpoint=endpoint,
        agent_name=agent_name,
        agent_version=agent_version,
        credential=credential,
    )

    # TODO 3: Run the agent once and print the full response.
    result = await agent.run(QUERY)
    print(f'\nAgent:\n{result.text}\n')

    # TODO 4: Run the agent again and stream the response as it is generated.
    print('Agent (streaming): ', end='', flush=True)
    async for chunk in agent.run(QUERY, stream=True):
        if chunk.text:
            print(chunk.text, end='', flush=True)
    print('\n')

    credential.close()


if __name__ == '__main__':
    asyncio.run(run())
