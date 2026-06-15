import { defineConfig } from 'vitepress'
import { labsSidebarItems } from './labs-sidebar.js'

/**
 * Custom markdown-it core rule that converts GFM task list syntax
 * (- [ ] / - [x]) to interactive HTML checkbox inputs.
 *
 * VitePress does not include a task list plugin by default, so this rule
 * adds proper rendering without requiring an extra npm dependency.
 */
function taskListPlugin(md: { core: { ruler: { after: (afterRule: string, ruleName: string, fn: (state: any) => void) => void } } }): void {
  md.core.ruler.after('inline', 'task_list', (state: any) => {
    for (let i = 2; i < state.tokens.length; i++) {
      const token = state.tokens[i]
      if (
        token.type !== 'inline' ||
        state.tokens[i - 1].type !== 'paragraph_open' ||
        state.tokens[i - 2].type !== 'list_item_open'
      ) continue

      const children: any[] = token.children
      if (!children?.length) continue

      const firstChild = children[0]
      if (firstChild.type !== 'text') continue

      const text: string = firstChild.content
      const unchecked = text.startsWith('[ ] ')
      const checked = text.startsWith('[x] ') || text.startsWith('[X] ')
      if (!unchecked && !checked) continue

      firstChild.content = text.slice(4)

      const cbToken = new state.Token('html_inline', '', 0)
      cbToken.content = checked
        ? '<input type="checkbox" class="task-list-item-checkbox" checked aria-label="Mark step as complete"> '
        : '<input type="checkbox" class="task-list-item-checkbox" aria-label="Mark step as complete"> '
      children.unshift(cbToken)

      state.tokens[i - 2].attrSet('class', 'task-list-item')
    }
  })
}

export default defineConfig({
  title: 'Microsoft Foundry Agentic Workshop',
  description: 'Hands-on labs for building agentic solutions with Microsoft Foundry',
  base: '/foundry-agentic-workshop/',
  outDir: 'dist',
  appearance: 'auto',
  markdown: {
    config: (md: any) => {
      // Add v-pre to all inline code elements so that content such as
      // `${{ github.ref }}` is not interpreted as a Vue template expression
      // during SSR compilation.
      const defaultCodeInline: ((tokens: any[], idx: number, options: any, env: any, self: any) => string) | undefined =
        md.renderer.rules.code_inline
      md.renderer.rules.code_inline = (tokens: any[], idx: number, options: any, env: any, self: any) => {
        tokens[idx].attrSet('v-pre', '')
        if (defaultCodeInline) {
          return defaultCodeInline(tokens, idx, options, env, self)
        }
        const token = tokens[idx]
        return `<code${self.renderAttrs(token)}>${md.utils.escapeHtml(token.content)}</code>`
      }
      taskListPlugin(md)
    },
  },
  themeConfig: {
    lightbox: true,
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Organizer Quickstart', link: '/quickstart-organizer' },
      { text: 'Organizer Quickstart w/ GitHub Copilot', link: '/quickstart-organizer-github-copilot' },
      { text: 'Attendee Quickstart', link: '/quickstart-attendee' },
      { text: 'Facilitator Quickstart', link: '/quickstart-facilitator' },
      { text: 'Proctor Guide', link: '/guide-proctor' },
    ],
    sidebar: [
      {
        text: 'Getting Started',
        items: [
          { text: 'Overview', link: '/' },
          { text: 'Organizer Quickstart', link: '/quickstart-organizer' },
          { text: 'Attendee Quickstart', link: '/quickstart-attendee' },
          { text: 'Facilitator Quickstart', link: '/quickstart-facilitator' },
        ],
      },
      {
        text: 'Role Guides',
        items: [
          { text: 'Organizer Guide', link: '/guide-organizer' },
          { text: 'Attendee Guide', link: '/guide-attendee' },
          { text: 'Facilitator Guide', link: '/guide-facilitator' },
          { text: 'Proctor Guide', link: '/guide-proctor' },
        ],
      },
      {
        text: 'Design',
        items: [
          { text: 'Architecture', link: '/design/architecture' },
          { text: 'Infrastructure', link: '/design/infrastructure' },
          { text: 'CI/CD Pipeline', link: '/design/cicd' },
          { text: 'Testing', link: '/design/testing' },
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
