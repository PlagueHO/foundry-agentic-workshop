"""FastAPI host for the Module 13 Custom Engine Agent proxy."""

from __future__ import annotations

import json

from fastapi import FastAPI, Request, Response

from agent import FoundryAgentRunner

app = FastAPI(title='ACL Remedy Advisor Custom Engine Agent')
runner = FoundryAgentRunner()


@app.post('/api/messages')
async def messages(request: Request) -> Response:
    """Handle a Bot Framework Activity and return an Activity response."""
    activity = await request.json()
    text = str(activity.get('text', '')).strip()
    if not text:
        return Response(status_code=204)
    answer = runner.run(text)
    return Response(content=json.dumps(runner.activity_response(activity, answer)), media_type='application/json')
