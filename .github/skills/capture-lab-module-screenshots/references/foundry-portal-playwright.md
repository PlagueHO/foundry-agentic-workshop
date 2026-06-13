# Foundry Portal Browser Automation — Reference

Detailed patterns for driving the Microsoft Foundry portal (`ai.azure.com`) and a
GitHub Codespace VS Code workbench (`*.github.dev`) with the browser tools while
capturing lab screenshots. These notes exist because the Foundry portal is built
on Fluent UI, whose controls frequently defeat ordinary automated clicks.

## Table of contents

- [Why ordinary clicks fail](#why-ordinary-clicks-fail)
- [Preferred interaction pattern](#preferred-interaction-pattern)
- [Locating controls](#locating-controls)
- [Filling forms and dropdowns](#filling-forms-and-dropdowns)
- [Handling flaky dialogs](#handling-flaky-dialogs)
- [Capturing screenshots to local disk](#capturing-screenshots-to-local-disk)
- [Reading agent / run state](#reading-agent--run-state)
- [Authentication gate](#authentication-gate)
- [Known Foundry naming constraints](#known-foundry-naming-constraints)

## Why ordinary clicks fail

`click_element` and other high-level helpers wait for an element to be "visible,
enabled and stable". Many Fluent UI controls report as never stable (animations,
virtualized lists, portals rendered outside the DOM subtree), so the helper times
out even though the control is plainly on screen.

## Preferred interaction pattern

Use `run_playwright_code` and dispatch the click event directly, which bypasses
the stability wait:

```js
await page.getByRole('button', { name: 'Add', exact: true }).dispatchEvent('click');
await page.waitForTimeout(1200);
```

- Add a short `waitForTimeout` after actions that trigger async rendering.
- Prefer `getByRole`, `getByText`, and `getByPlaceholder` locators over brittle
  CSS/XPath.
- Use `{ exact: true }` to avoid strict-mode violations when several elements
  share a name (the portal has page-level tabs *and* dialog tabs called the same
  thing).

## Locating controls

When a role query is ambiguous or returns nothing, inspect what is actually on the
page before guessing:

```js
const tabs = await page.getByRole('tab').allInnerTexts();
const menuItems = await page.getByRole('menuitem').allInnerTexts();
return { tabs, menuItems };
```

If a tab/button still will not resolve by role (dialogs sometimes render their
tabs outside the queried subtree), fall back to a coordinate click read from a
screenshot:

```js
await page.mouse.click(383, 173); // x,y read from the captured screenshot
await page.waitForTimeout(1500);
```

## Filling forms and dropdowns

Use `.fill()` for text inputs and the option role for Fluent comboboxes:

```js
await page.getByPlaceholder('Provide a unique name').fill('retail-remedy-ops');
await page.getByPlaceholder('Provide the remote MCP server endpoint').fill('https://.../mcp');

// Open a Fluent combobox by clicking its current value, then pick an option
await page.getByText('Key-based', { exact: true }).dispatchEvent('click');
await page.waitForTimeout(800);
await page.getByRole('option', { name: 'Unauthenticated' }).dispatchEvent('click');
```

Validation errors surface as `alert` nodes — read them back to confirm a field was
accepted:

```js
const alerts = await page.getByRole('alert').allInnerTexts();
return { alerts };
```

## Handling flaky dialogs

The "Select a tool" / Custom-tool dialogs open and close intermittently and may
return empty tab lists right after opening. Robust recipe:

1. Open the menu/dialog and `waitForTimeout(1200)`.
1. Take a screenshot to a scratch path and **view it** to see real state.
1. Click the target tab/card by coordinate or `getByText`, not only by role.
1. Re-query to confirm the panel changed before proceeding.

Always delete the scratch screenshot (e.g. `.tmp-dialog.png`) when done.

## Capturing screenshots to local disk

The browser runs on the local machine, so Playwright writes to the local
filesystem. Save lab screenshots straight into the module's folder:

```js
await page.screenshot({
  path: 'd:\\source\\GitHub\\PlagueHO\\foundry-agentic-workshop\\docs\\assets\\screenshots\\lab-06\\02-agent-playground.png'
});
```

Use double backslashes in the JS string on Windows. Re-open the exact dialog or
menu the step describes before the shot so the image matches the instructions.

## Reading agent / run state

To confirm a step's effect without a screenshot, read the accessibility snapshot
or specific text:

```js
const tools = await page.locator('text=/Code interpreter|Web search|retail-remedy-ops/').allInnerTexts();
return { tools };
```

The Save button being `disabled` indicates a clean (saved) agent; enabled means
unsaved changes ("dirty"). A version chip like `3 (Today 11:41 AM)` confirms a
save produced a new version.

## Authentication gate

Before automating, confirm the page is past sign-in:

- Foundry portal URL must be under `ai.azure.com/...` and show the workspace, not
  `login.microsoftonline.com` or a "Sign in" panel.
- The Codespace `*.github.dev` page must show the VS Code workbench, not the
  GitHub login or "Resume Codespace" screen.

If either is not ready, stop and ask the user to sign in. Never enter credentials.

## Known Foundry naming constraints

These bit a real lab and are easy to trip over:

- **Portal Custom MCP connection name**: only letters, digits, **dashes, and dots**
  — **no underscores**. Error if violated: *"Connection name must be 1-64
  characters long and can only contain alphanumeric characters, dashes, and dots."*
- **Python SDK MCP `server_label`**: only letters, digits, and **underscores** —
  **no dashes**.
- These rules are mutually exclusive, so the same logical tool legitimately appears
  as `retail-remedy-ops` (portal) and `retail_remedy_ops` (SDK). Do not try to make
  them identical.
- Portal MCP connections **persist at the project level** after you remove the tool
  from an agent. Re-adding reuses the existing connection; creating a fresh one with
  the same name fails with *"Connection name must be unique."*
- MCP tool calls in the playground raise a per-call **Approve / Deny** prompt.
  "Always approve all tools" only marks the agent dirty (needs Save) and still
  re-prompts for each newly seen tool mid-run.
