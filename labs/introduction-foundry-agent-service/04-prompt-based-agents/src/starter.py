"""Starter code for Lab 04 — chat with the acl-remedy-advisor Prompt Agent."""

import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


def run() -> None:
    load_dotenv()

    endpoint = os.environ['FOUNDRY_PROJECT_ENDPOINT']
    agent_name = os.environ['AGENT_NAME']

    # TODO 1 — Create an AIProjectClient connected to your Foundry project
    # and get an OpenAI-compatible client scoped to that project.


    # TODO 2 — Create a new conversation thread so that all turns share
    # the same context, then print the conversation ID.


    print('ACL Remedy Advisor — type your question, or "exit" to quit.\n')

    while True:
        user_input = input('You: ').strip()
        if user_input.lower() in ('exit', 'quit', ''):
            print('Goodbye.')
            break

        # TODO 3 — Send the user's message to the agent and store the response.
        # Route the message to the saved agent by name using agent_reference.


        # TODO 4 — Print '[web search]' for each web search tool call the agent
        # made during this turn, then print the agent's final response text.


if __name__ == '__main__':
    run()
