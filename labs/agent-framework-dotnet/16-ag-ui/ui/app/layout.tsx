// app/layout.tsx
//
// Root layout — wraps the entire application with the CopilotKit provider.
//
// <CopilotKit runtimeUrl="/api/copilotkit"> connects every component in the
// tree to the CopilotKit runtime proxy defined in app/api/copilotkit/route.ts.
// The provider is a React client component rendered inside this server layout.

import type { Metadata } from 'next'
import { CopilotKit } from '@copilotkit/react-core'
import '@copilotkit/react-ui/styles.css'
import './globals.css'

export const metadata: Metadata = {
  title: 'Trip Disruption Concierge',
  description: 'Module 16 — AG-UI with Microsoft Agent Framework and CopilotKit',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>
        {/* runtimeUrl points to the Next.js API route that proxies to the .NET server */}
        <CopilotKit runtimeUrl="/api/copilotkit">
          {children}
        </CopilotKit>
      </body>
    </html>
  )
}
