// app/page.tsx
//
// Main page — renders the CopilotKit chat sidebar.
//
// CopilotSidebar is a prebuilt component that provides a full chat UI:
//   • Sends user messages to the CopilotKit runtime (→ your .NET agent)
//   • Streams agent responses in real time
//   • Displays backend tool calls (get_flight_status) as they execute
//
// defaultOpen shows the sidebar immediately without a user click.
// The `instructions` prop adds a system message visible to the frontend
// (in addition to the agent's own server-side instructions).

import { CopilotSidebar } from '@copilotkit/react-ui'

export default function Page() {
  return (
    <main>
      <CopilotSidebar
        defaultOpen
        instructions="You are the Trip Disruption Concierge for Air New Zealand."
        labels={{
          title: 'Trip Disruption Concierge',
          initial:
            "Hi! I'm your Trip Disruption Concierge. Tell me your flight number and I'll check its status and help you with your options.",
        }}
      />
    </main>
  )
}
