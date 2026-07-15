"""Foundry call used by the Custom Engine Agent message handler."""

from __future__ import annotations

import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


class FoundryAgentRunner:
    """Run the existing Foundry agent for a Bot Framework message."""

    def __init__(self) -> None:
        endpoint = os.environ['FOUNDRY_PROJECT_ENDPOINT']
        self.agent_name = os.environ.get('AGENT_NAME', 'acl-remedy-advisor')
        project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
        self.client = project.get_openai_client(agent_name=self.agent_name)

    def run(self, message: str) -> str:
        """Create a thread, run the configured Foundry agent, and return its text."""
        response = self.client.responses.create(input=message)
        return response.output_text

    @staticmethod
    def activity_response(activity: dict, answer: str) -> dict:
        """Build an Activity-shaped response for local protocol testing."""
        return {
            'type': 'message',
            'text': answer,
            'from': activity.get('recipient', {}),
            'recipient': activity.get('from', {}),
            'conversation': activity.get('conversation', {}),
            'replyToId': activity.get('id'),
        }
