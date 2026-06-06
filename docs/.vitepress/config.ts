import { defineConfig } from 'vitepress'
import { labsSidebarItems } from './labs-sidebar.js'

export default defineConfig({
  title: 'Microsoft Foundry Agentic Workshop',
  description: 'Hands-on labs for building agentic solutions with Microsoft Foundry',
  base: '/foundry-agentic-workshop/',
  outDir: 'dist',
  appearance: 'auto',
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Organizer Quickstart', link: '/quickstart-organizer' },
      { text: 'Learner Quickstart', link: '/quickstart-learner' },
      { text: 'Instructor Guide', link: '/instructor-guide' },
      { text: 'Facilitator Notes', link: '/facilitator-notes' },
    ],
    sidebar: [
      {
        text: 'Getting Started',
        items: [
          { text: 'Overview', link: '/' },
          { text: 'Organizer Quickstart', link: '/quickstart-organizer' },
          { text: 'Learner Quickstart', link: '/quickstart-learner' },
        ],
      },
      {
        text: 'Workshop Delivery',
        items: [
          { text: 'Instructor Guide', link: '/instructor-guide' },
          { text: 'Facilitator Notes', link: '/facilitator-notes' },
          { text: 'Architecture Diagram', link: '/architecture-diagram' },
        ],
      },
      {
        text: 'Labs',
        items: labsSidebarItems,
      },
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/PlagueHO/foundry-agentic-workshop' },
    ],
    footer: {
      message: 'Released under the MIT License.',
    },
  },
})
