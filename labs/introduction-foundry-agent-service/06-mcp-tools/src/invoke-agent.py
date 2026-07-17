"""Chat with the acl-remedy-advisor Prompt Agent (Module 06 - MCP tools)."""

import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


def run() -> None:
    load_dotenv()

    endpoint = os.environ['FOUNDRY_PROJECT_ENDPOINT']
    agent_name = os.environ['AGENT_NAME']

    client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    openai = client.get_openai_client()

    print('ACL Remedy Advisor (with MCP tools) - type your question, or "exit" to quit.\n')

    # Multi-turn context is maintained via previous_response_id rather than the
    # conversations API, because conversation= and previous_response_id= are mutually
    # exclusive. Approval continuations also use previous_response_id, so the chain is:
    # None → turn1_response → approval_response → turn2_response → …
    previous_response_id: str | None = None

    while True:
        user_input = input('You: ').strip()
        if user_input.lower() in ('exit', 'quit', ''):
            print('Goodbye.')
            break

        # Build the call kwargs; only include previous_response_id once a prior turn exists
        # because passing None serializes to JSON null which the Responses API rejects.
        call_kwargs: dict[str, object] = {
            'extra_body': {
                'agent_reference': {
                    'name': agent_name,
                    'type': 'agent_reference',
                },
            },
            'input': user_input,
        }
        if previous_response_id is not None:
            call_kwargs['previous_response_id'] = previous_response_id

        response = openai.responses.create(**call_kwargs)

        # Handle MCP tool calls, prompting the user to approve or deny each one.
        # The Responses API returns mcp_approval_request items when an MCP tool call
        # requires human-in-the-loop approval. Without sending approval responses the turn
        # never completes and output_text is empty.
        while True:
            approval_inputs = []
            for item in response.output:
                if item.type == 'mcp_approval_request':
                    tool_name = getattr(item, 'name', '<unknown>')
                    tool_args = getattr(item, 'arguments', None)
                    if tool_args:
                        display_args = tool_args if len(tool_args) <= 120 else tool_args[:117] + '...'
                        print(f'\n[MCP tool call] {tool_name}({display_args})')
                    else:
                        print(f'\n[MCP tool call] {tool_name}()')
                    raw = input('  Approve? [Y/n]: ').strip().lower()
                    approved = raw in ('', 'y', 'yes')
                    if not approved:
                        print('  [denied]')
                    approval_inputs.append({
                        'type': 'mcp_approval_response',
                        'approve': approved,
                        'approval_request_id': item.id,
                    })
                elif item.type != 'message':
                    print(f'[tool: {item.type}]')

            if not approval_inputs:
                break

            # Submit approval decisions and continue the turn.
            # extra_body with agent_reference is required so the API resolves the model.
            response = openai.responses.create(
                previous_response_id=response.id,
                extra_body={
                    'agent_reference': {
                        'name': agent_name,
                        'type': 'agent_reference',
                    },
                },
                input=approval_inputs,
            )

        previous_response_id = response.id
        print(f'\nAdvisor: {response.output_text}\n')


if __name__ == '__main__':
    run()
