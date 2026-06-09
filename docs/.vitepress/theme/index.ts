import DefaultTheme from 'vitepress/theme'
import { h, defineComponent, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vitepress'
import type { Theme } from 'vitepress'
import './custom.css'

const TASK_KEY_PREFIX = 'foundry-task:'

/**
 * Reads saved checkbox state from localStorage and attaches change listeners
 * so that attendees' progress is persisted across page refreshes.
 *
 * Uses a `data-task-bound` attribute to avoid double-binding on hot reload.
 */
function initTaskCheckboxes(): void {
  if (typeof window === 'undefined') return
  const path = window.location.pathname
  const checkboxes = document.querySelectorAll<HTMLInputElement>(
    '.task-list-item-checkbox:not([data-task-bound])',
  )
  checkboxes.forEach((cb, idx) => {
    cb.setAttribute('data-task-bound', '1')
    const key = `${TASK_KEY_PREFIX}${path}:${idx}`
    if (localStorage.getItem(key) === '1') cb.checked = true
    cb.addEventListener('change', () =>
      localStorage.setItem(key, cb.checked ? '1' : '0'),
    )
  })
}

const Layout = defineComponent({
  name: 'TaskCheckboxLayout',
  setup() {
    const route = useRoute()
    onMounted(initTaskCheckboxes)
    watch(
      () => route.path,
      () => nextTick(initTaskCheckboxes),
    )
    return () => h(DefaultTheme.Layout!)
  },
})

export default {
  extends: DefaultTheme,
  Layout,
} satisfies Theme
