"""Starter FastAPI host for a Microsoft 365 Custom Engine Agent."""

from __future__ import annotations

from fastapi import FastAPI

from agent import FoundryAgentRunner

app = FastAPI(title='ACL Remedy Advisor Custom Engine Agent')
runner = FoundryAgentRunner()


@app.post('/api/messages')
async def messages(activity: dict) -> dict:
    """TODO: pass the authenticated Activity through CloudAdapter and AgentApplication."""
    text = activity.get('text', '').strip()
    response = runner.run(text)
    return {'type': 'message', 'text': response}
