"""Starter: deploy the acl-remedy-advisor-hosted-code agent from source code (Part 2).

Fill in the numbered TODOs to deploy the agent bundle in ``src/agent/`` as a hosted agent.
The completed reference implementation lives in
``solution/deploy_hosted_agent_code.py`` - try to finish this file before peeking.

Usage:
    uv run python labs/introduction-foundry-agent-service/09-hosted-agents/src/starter.py
"""

import hashlib
import io
import os
import sys
import zipfile
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeConfiguration,
    CodeDependencyResolution,
    HostedAgentDefinition,
    ProtocolVersionRecord,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# The shared polling helper lives with the solution scripts so the lab keeps a single
# source of truth. Add that folder to the import path so this starter can reuse it.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'solution'))

from hosted_agent_support import wait_for_agent_version_active  # noqa: E402, F401

# The agent bundle lives next to this file under agent/. Everything in that folder is
# zipped flat so Foundry's remote build finds main.py and requirements.txt at the root.
AGENT_DIR = Path(__file__).resolve().parent / 'agent'

CPU = '1'
MEMORY = '2Gi'
RUNTIME = 'python_3_13'


def build_code_zip(agent_dir: Path) -> tuple[bytes, str]:
    """Zip the agent bundle flat and return ``(zip_bytes, sha256_hexdigest)``."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(agent_dir.rglob('*')):
            if path.is_dir() or '__pycache__' in path.parts or path.suffix == '.pyc':
                continue
            archive.write(path, path.relative_to(agent_dir).as_posix())
    zip_bytes = buffer.getvalue()
    return zip_bytes, hashlib.sha256(zip_bytes).hexdigest()


def run() -> None:
    load_dotenv()

    endpoint = os.environ['FOUNDRY_PROJECT_ENDPOINT']
    agent_name = os.environ.get('HOSTED_AGENT_NAME_CODE', 'acl-remedy-advisor-hosted-code')
    model_deployment = os.environ.get('AGENT_MODEL', 'chat')
    mcp_server_url = os.environ.get('RETAIL_REMEDY_OPS_MCP_SERVER_URL', '').strip()
    mcp_server_label = os.environ.get('RETAIL_REMEDY_OPS_MCP_SERVER_LABEL', 'retail_remedy_ops')

    if not mcp_server_url:
        raise ValueError(
            'RETAIL_REMEDY_OPS_MCP_SERVER_URL is not set. Start the Retail Remedy Operations MCP server '
            '(Module 06, server.py), expose it via a dev tunnel, then set RETAIL_REMEDY_OPS_MCP_SERVER_URL to '
            'the public URL plus /mcp in your .env file. Example: '
            'RETAIL_REMEDY_OPS_MCP_SERVER_URL=https://abc123-8080.devtunnels.ms/mcp'
        )

    zip_bytes, zip_sha256 = build_code_zip(AGENT_DIR)
    print(f'Built code archive from {AGENT_DIR} ({len(zip_bytes)} bytes, sha256={zip_sha256}).')

    credential = DefaultAzureCredential()
    with AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as client:
        # TODO 1: Prepare the code stream and build a HostedAgentDefinition describing the agent.
        #   - Wrap zip_bytes in an io.BytesIO and set its .name attribute to '{agent_name}.zip'.
        #   - Build a HostedAgentDefinition with:
        #       cpu=CPU, memory=MEMORY,
        #       environment_variables={
        #           'AZURE_AI_MODEL_DEPLOYMENT_NAME': model_deployment,
        #           'RETAIL_REMEDY_OPS_MCP_SERVER_URL': mcp_server_url,
        #           'RETAIL_REMEDY_OPS_MCP_SERVER_LABEL': mcp_server_label,
        #       },
        #       code_configuration=CodeConfiguration(
        #           runtime=RUNTIME,
        #           entry_point=['python', 'main.py'],
        #           dependency_resolution=CodeDependencyResolution.REMOTE_BUILD,
        #       ),
        #       protocol_versions=[ProtocolVersionRecord(protocol='responses', version='2.0.0')].
        code_stream = ...  # noqa: F841
        definition = ...  # noqa: F841

        # TODO 2: Create the agent version from code.
        #   created = client.agents.create_version_from_code(
        #       agent_name=agent_name,
        #       definition=definition,
        #       code=code_stream,
        #       code_zip_sha256=zip_sha256,
        #       description='ACL Remedy Advisor hosted agent deployed from source code.',
        #   )

        # TODO 3: Poll until the version is active. The helper imported at the top of
        #   this file (from solution/hosted_agent_support.py) does this:
        #       wait_for_agent_version_active(client, agent_name, created.version)
        raise NotImplementedError('Complete TODO 1-3 to deploy the hosted agent.')


if __name__ == '__main__':
    run()
