"""Solution for Lab 04 - chat with the acl-remedy-advisor Prompt Agent."""

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

    # Create a new conversation thread - persists context across turns.
    conversation = openai.conversations.create()
    print(f'Conversation started: {conversation.id}\n')

    print('ACL Remedy Advisor - type your question, or "exit" to quit.\n')

    while True:
        user_input = input('You: ').strip()
        if user_input.lower() in ('exit', 'quit', ''):
            print('Goodbye.')
            break

        response = openai.responses.create(
            conversation=conversation.id,
            extra_body={
                'agent_reference': {
                    'name': agent_name,
                    'type': 'agent_reference',
                },
            },
            input=user_input,
        )

        # Show a web search indicator when the agent calls the search tool.
        for item in response.output:
            if item.type == 'web_search_call':
                print('[web search]')

        print(f'\nAdvisor: {response.output_text}\n')


if __name__ == '__main__':
    run()
