"""Shared helpers for deploying and operating the Module 09 hosted agents.

These helpers are used by both deployment scripts (``deploy_hosted_agent_code.py`` and
``deploy_hosted_agent_container.py``) and the invocation script
(``invoke_hosted_agent.py``) so the lab keeps a single source of truth for polling,
version selection, and agent-identity RBAC.
"""

import os
import time
import uuid

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AgentVersionDetails
from azure.core.credentials import TokenCredential
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import RoleAssignmentCreateParameters

# Foundry User (formerly Azure AI User). Matches foundryRoleCatalog['foundry-user'] in
# infra/main.bicep and ROLE_DEFINITION_IDS in scripts/generate-attendee-onboarding.py.
FOUNDRY_USER_ROLE_DEFINITION_ID = '53ca6127-db72-4b80-b1b0-d745d6d5456d'


def wait_for_agent_version_active(
    client: AIProjectClient,
    agent_name: str,
    agent_version: str,
    *,
    max_attempts: int = 60,
    poll_interval_seconds: int = 10,
) -> None:
    """Poll until the agent version reports ``active``; raise on ``failed`` or timeout."""
    print('Waiting for the hosted agent version to become active...')

    for attempt in range(max_attempts):
        time.sleep(poll_interval_seconds)
        version_details = client.agents.get_version(agent_name=agent_name, agent_version=agent_version)
        status = version_details['status']
        print(f'  Agent version status: {status} (attempt {attempt + 1}/{max_attempts})')

        if status == 'active':
            print('Agent version is now active.')
            return
        if status == 'failed':
            raise RuntimeError(f'Hosted agent version provisioning failed: {dict(version_details)}')

    raise RuntimeError('Timed out waiting for the hosted agent version to become active.')


def get_latest_active_agent_version(client: AIProjectClient, agent_name: str) -> AgentVersionDetails:
    """Return the newest active version of the named hosted agent."""
    for version in client.agents.list_versions(agent_name=agent_name, order='desc'):
        if version.status == 'active':
            return version

    raise RuntimeError(
        f"No active version found for hosted agent '{agent_name}'. "
        'Deploy a version first with deploy_hosted_agent_code.py or deploy_hosted_agent_container.py.'
    )


def ensure_agent_identity_rbac(
    agent: AgentVersionDetails,
    credential: TokenCredential,
    *,
    max_attempts: int = 6,
    retry_interval_seconds: int = 10,
) -> None:
    """Grant the Foundry User role to the hosted agent's per-deploy identity (idempotent).

    Every hosted agent receives its own Microsoft Entra agent identity at deploy time.
    That identity needs the Foundry User role on the Foundry account to call models at
    runtime, and its principal ID only exists after the version is created - so this role
    assignment cannot be pre-provisioned in Bicep.

    Reads ``AZURE_SUBSCRIPTION_ID``, ``AZURE_RESOURCE_GROUP``, and ``FOUNDRY_RESOURCE_NAME``
    from the environment to build the account scope. The constrained Role Based Access
    Control Administrator role provisioned for each attendee in infra/main.bicep allows
    assigning only this role to service principals, so this runs within least privilege.
    """
    principal_id = getattr(getattr(agent, 'instance_identity', None), 'principal_id', None)
    if not principal_id:
        raise RuntimeError(
            'The hosted agent version has no instance-identity principal ID. '
            'Wait for the version to become active before assigning RBAC.'
        )

    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
    resource_group = os.environ['AZURE_RESOURCE_GROUP']
    account_name = os.environ['FOUNDRY_RESOURCE_NAME']

    scope = (
        f'/subscriptions/{subscription_id}/resourceGroups/{resource_group}'
        f'/providers/Microsoft.CognitiveServices/accounts/{account_name}'
    )
    role_definition_id = (
        f'/subscriptions/{subscription_id}/providers/Microsoft.Authorization'
        f'/roleDefinitions/{FOUNDRY_USER_ROLE_DEFINITION_ID}'
    )
    # Deterministic assignment name so re-running the deploy is idempotent.
    role_assignment_name = str(
        uuid.uuid5(uuid.NAMESPACE_URL, f'{scope}|{principal_id}|{role_definition_id}')
    )

    client = AuthorizationManagementClient(credential, subscription_id)
    try:
        client.role_assignments.get(scope, role_assignment_name)
        print(f'Foundry User role already assigned to agent identity {principal_id}.')
        return
    except ResourceNotFoundError:
        pass

    parameters = RoleAssignmentCreateParameters(
        role_definition_id=role_definition_id,
        principal_id=principal_id,
        principal_type='ServicePrincipal',
    )

    # A brand-new agent identity can take a short time to propagate to Microsoft Entra ID,
    # so retry the assignment if the directory has not caught up yet.
    for attempt in range(max_attempts):
        try:
            client.role_assignments.create(scope, role_assignment_name, parameters)
            print(f'Assigned Foundry User role to agent identity {principal_id} at the account scope.')
            return
        except HttpResponseError as error:
            if 'PrincipalNotFound' not in str(error) or attempt == max_attempts - 1:
                raise
            print(
                f'  Agent identity not yet visible in Microsoft Entra ID; retrying in '
                f'{retry_interval_seconds}s (attempt {attempt + 1}/{max_attempts})...'
            )
            time.sleep(retry_interval_seconds)
