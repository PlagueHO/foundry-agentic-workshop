"""Deploy the acl-remedy-advisor-hosted-container agent as a container image (Part 1).

This is the lower-level deployment path. It builds the agent image with Docker, pushes it
to the shared workshop Azure Container Registry under a project-specific tag, then creates
a container-based hosted agent version. Requires Docker and the Azure CLI.

Most attendees should use the source-code path (deploy_hosted_agent_code.py); this path
shows what Foundry does under the hood and is useful when you want full control of the
image. The image is tagged per project so attendees sharing one registry never collide.

Usage:
    uv run python labs/introduction-foundry-agent-service/09-hosted-agents/solution/deploy_hosted_agent_container.py
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    ContainerConfiguration,
    HostedAgentDefinition,
    ProtocolVersionRecord,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from hosted_agent_support import wait_for_agent_version_active

AGENT_DIR = Path(__file__).resolve().parent.parent / 'src' / 'agent'

CPU = '1'
MEMORY = '2Gi'
IMAGE_REPOSITORY = 'acl-remedy-advisor-hosted-container'


def project_image_tag(endpoint: str) -> str:
    """Derive a unique, registry-safe image tag from the project endpoint."""
    project_name = endpoint.rstrip('/').split('/api/projects/')[-1].split('/')[0]
    slug = re.sub(r'[^a-z0-9-]', '-', project_name.lower()).strip('-')
    return slug or 'default'


def run_command(command: list[str]) -> None:
    """Run a shell command, echoing it first and raising on a non-zero exit code.

    Resolves the executable on PATH so platform-specific shims (such as the
    ``az.cmd`` wrapper on Windows) are found by ``subprocess``.
    """
    print(f'$ {" ".join(command)}')
    executable = shutil.which(command[0])
    if executable is None:
        raise FileNotFoundError(
            f'Required command {command[0]!r} was not found on PATH. '
            'Confirm it is installed and your shell PATH is current.'
        )
    subprocess.run([executable, *command[1:]], check=True)


def run() -> None:
    load_dotenv()

    endpoint = os.environ['FOUNDRY_PROJECT_ENDPOINT']
    agent_name = os.environ.get('HOSTED_AGENT_NAME_CONTAINER', 'acl-remedy-advisor-hosted-container')
    model_deployment = os.environ.get('AGENT_MODEL', 'chat')
    registry_name = os.environ['AZURE_CONTAINER_REGISTRY_NAME']
    registry_endpoint = os.environ['AZURE_CONTAINER_REGISTRY_ENDPOINT']
    mcp_server_url = os.environ.get('RETAIL_REMEDY_OPS_MCP_SERVER_URL', '').strip()
    mcp_server_label = os.environ.get('RETAIL_REMEDY_OPS_MCP_SERVER_LABEL', 'retail_remedy_ops')

    if not mcp_server_url:
        raise ValueError(
            'RETAIL_REMEDY_OPS_MCP_SERVER_URL is not set. Start the Retail Remedy Operations MCP server '
            '(Module 06, server.py), expose it via a dev tunnel, then set RETAIL_REMEDY_OPS_MCP_SERVER_URL to '
            'the public URL plus /mcp in your .env file. Example: '
            'RETAIL_REMEDY_OPS_MCP_SERVER_URL=https://abc123-8080.devtunnels.ms/mcp'
        )

    image = f'{registry_endpoint}/{IMAGE_REPOSITORY}:{project_image_tag(endpoint)}'

    # Foundry hosted agents only run linux/amd64 images, so build for that platform
    # explicitly even when building on an Arm machine. --provenance=false forces a single
    # image manifest instead of a buildx OCI image index with an attestation manifest, which
    # the hosted agent platform cannot pull (it reports a misleading image_pull_failed error).
    run_command(['docker', 'build', '--platform', 'linux/amd64', '--provenance=false', '-t', image, str(AGENT_DIR)])
    run_command(['az', 'acr', 'login', '--name', registry_name])
    run_command(['docker', 'push', image])

    credential = DefaultAzureCredential()
    with AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as client:
        created = client.agents.create_version(
            agent_name=agent_name,
            definition=HostedAgentDefinition(
                cpu=CPU,
                memory=MEMORY,
                environment_variables={
                    'AZURE_AI_MODEL_DEPLOYMENT_NAME': model_deployment,
                    'RETAIL_REMEDY_OPS_MCP_SERVER_URL': mcp_server_url,
                    'RETAIL_REMEDY_OPS_MCP_SERVER_LABEL': mcp_server_label,
                },
                container_configuration=ContainerConfiguration(image=image),
                protocol_versions=[ProtocolVersionRecord(protocol='responses', version='2.0.0')],
            ),
            metadata={'enableVnextExperience': 'true'},
        )
        print(f'Created hosted agent {agent_name} version {created.version} from image {image}.')

        wait_for_agent_version_active(client, agent_name, created.version)

    print(f'Hosted agent {agent_name} is active. Run invoke_hosted_agent.py to chat with it.')


if __name__ == '__main__':
    run()
