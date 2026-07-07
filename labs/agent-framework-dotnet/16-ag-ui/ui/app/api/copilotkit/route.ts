// app/api/copilotkit/route.ts
//
// This Next.js API route acts as the CopilotKit runtime proxy.
//
// Architecture:
//   Browser  →  POST /api/copilotkit  (this file, server-side)
//                      ↓
//              CopilotRuntime + HttpAgent
//                      ↓
//              http://localhost:8888  (your .NET AG-UI server)
//
// The CopilotRuntime handles agent discovery, session routing, and
// middleware. HttpAgent delegates every run call to your .NET server,
// which streams AG-UI SSE events back through this proxy to the browser.

import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from '@copilotkit/runtime'
import { HttpAgent } from '@ag-ui/client'
import { NextRequest } from 'next/server'

// Read the AG-UI server URL from .env.local.
// Default to localhost:8888 — the port used in the module run instructions.
const serverUrl = process.env.AGUI_SERVER_URL ?? 'http://localhost:8888'

// Register the .NET AG-UI server as the default agent.
// HttpAgent connects to any AG-UI-compatible endpoint.
// ExperimentalEmptyAdapter signals that the model lives on the agent server,
// not in a separate model service managed by CopilotKit.
const runtime = new CopilotRuntime({
  agents: {
    default: new HttpAgent({ url: serverUrl }),
  },
})

export const POST = async (req: NextRequest): Promise<Response> => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter: new ExperimentalEmptyAdapter(),
    endpoint: '/api/copilotkit',
  })
  return handleRequest(req)
}
