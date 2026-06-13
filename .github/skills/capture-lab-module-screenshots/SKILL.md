---
name: capture-lab-module-screenshots
description: >-
  **WORKFLOW SKILL** — Live-validate a single workshop lab module in the browser
  and add correct, clarifying screenshots. Requires a specific lab module to be
  named, confirms the required browser pages are already open AND authenticated
  (Microsoft Foundry portal at ai.azure.com, and VS Code + Foundry Toolkit in a
  GitHub Codespace), walks the lab steps literally as an attendee would, captures
  screenshots at the unclear moments, embeds them with the repo's collapsible
  pattern, fixes any factual defects it finds, then runs markdownlint and a
  screenshot-inventory check. WHEN: "add screenshots to lab module", "capture lab
  screenshots", "update lab NN screenshots", "verify lab module is correct",
  "validate the lab steps", "screenshot the lab walkthrough". INVOKES:
  open_browser_page / run_playwright_code (browser automation), read_file,
  replace_string_in_file, run_in_terminal (markdownlint, validation script).
  FOR SINGLE OPERATIONS: capture one screenshot with run_playwright_code and embed
  it manually.
metadata:
  author: foundry-workshop
  version: "1.0"
compatibility:
  - GitHub Copilot
  - VS Code Insiders
  - "Requires browser tools (open_browser_page, run_playwright_code) with at least one shared, authenticated page"
  - "Requires the Microsoft Foundry portal (ai.azure.com) already signed in"
  - "Optionally requires VS Code + Foundry Toolkit in a GitHub Codespace (*.github.dev) when the module uses the toolkit or an MCP tunnel"
argument-hint: >-
  module=<lab path or number, e.g. labs/introduction-foundry-agent-service/06-mcp-tools or 06>
---

# Capture Lab Module Screenshots

Live-validate one workshop lab module and add the screenshots an attendee needs
at the moments that are not immediately obvious — while confirming the written
steps actually work. The screenshots are a by-product of *walking the lab for
real*; that walk is also what guarantees the module is correct.

This skill is deliberately interactive and cautious. The browser pages it drives
belong to the user and are already signed in. **Never** sign in, enter
credentials, or guess URLs. If a required page is missing, on a login screen, or
a step does not behave as written, **STOP AND ASK** rather than improvising.

## Inputs

| Input | Required | How to resolve |
|-------|----------|----------------|
| Target lab module | Yes | A path like `labs/introduction-foundry-agent-service/06-mcp-tools`, or a number like `06`. If absent, ask which module. |
| Screenshot folder | Derived | `docs/assets/screenshots/lab-NN/` where `NN` is the module's two-digit prefix. |
| Required browser pages | Verified | Enumerated from the shared pages — see Step 2. |

## Step 1 — Resolve the target module

Resolve the named module to a concrete README path and screenshot folder.

1. If the user gave a number (e.g. `06`), match it to the folder under
   `labs/introduction-foundry-agent-service/` whose name starts with that prefix.
1. Confirm `labs/.../NN-name/README.md` exists. If not, ask the user to clarify.
1. Derive the screenshot folder `docs/assets/screenshots/lab-NN/`. Create it only
   when the first screenshot is saved.
1. Read the README end-to-end. Note its section order
   (**Objectives → Steps → Validation → Troubleshooting**) and list every step
   plus every screenshot it already references.

State the resolved module, README path, and screenshot folder back to the user
before touching the browser.

## Step 2 — Verify the required pages are open and authenticated

This is a hard gate. Do not start the walkthrough until it passes.

1. Enumerate the shared browser pages (they are listed in the conversation
   context, or call `open_browser_page` to inspect).
1. Determine which apps the module needs:
   - **Foundry portal** (`ai.azure.com`) — needed by almost every module.
   - **VS Code + Foundry Toolkit in a GitHub Codespace** (`*.github.dev`) — needed
     when the module uses the Foundry Toolkit extension, a local MCP server, or a
     forwarded tunnel.
1. For each required app, confirm a page is **open AND authenticated**:
   - Foundry portal: the URL is under `ai.azure.com/...` and the page shows the
     agent/project workspace — **not** a `login.microsoftonline.com` or
     "Sign in" screen.
   - Codespace VS Code: the `*.github.dev` workbench is loaded (not the GitHub
     sign-in or "Resume Codespace" screen).
1. If a required page is missing, on a login screen, or otherwise not ready:
   **STOP AND ASK** the user to open the app and sign in, then continue. Do not
   attempt to authenticate.

Briefly confirm which pages you matched (with their page IDs) before proceeding.

## Step 3 — Walk the lab steps literally

Follow the README as a first-time attendee would — in order, doing exactly what
each step says, with no shortcuts or prior knowledge.

For each step:

1. Perform the described action in the correct browser page.
1. Observe the **actual** result and compare it to what the README claims.
1. Decide:
   - **Works as written** → continue; note whether a screenshot would help here.
   - **Wrong, unclear, or fails** → **STOP AND ASK**. Report exactly what the step
     says, what actually happened, and your proposed correction. Do not silently
     deviate from the written steps to force a pass.

For the mechanics of driving the Foundry portal's Fluent UI reliably (it resists
ordinary clicks), see [references/foundry-portal-playwright.md](references/foundry-portal-playwright.md).
The short version: prefer `run_playwright_code` with `.dispatchEvent('click')` and
`getByRole(...)` locators over `click_element`, and fall back to coordinate clicks
for flaky dialogs.

## Step 4 — Capture the clarifying screenshots

Capture screenshots only where the written step is **not immediately obvious** —
a non-trivial dialog, a control that is hard to find, a multi-field form, an
approval prompt, or a confirming end state. Skip the trivially obvious.

- Save each screenshot to the module's folder
  `docs/assets/screenshots/lab-NN/` using the established naming:
  `NN-descriptive-kebab.png`, numbered in the order they appear in the lab.
- Save to the **local disk path** via Playwright, because the browser runs on the
  local machine:

  ```js
  await page.screenshot({ path: 'd:\\source\\GitHub\\PlagueHO\\foundry-agentic-workshop\\docs\\assets\\screenshots\\lab-NN\\NN-name.png' });
  ```

- Frame each shot on the relevant control or result. Re-open menus/dialogs as
  needed so the screenshot shows the exact state the step describes.
- A temporary scratch screenshot (e.g. `.tmp-dialog.png` at the repo root) is fine
  while you find the right framing — **delete it before finishing**.

## Step 5 — Embed the screenshots in the README

Match the repo's existing screenshot convention exactly — a collapsible block so
the lab stays scannable:

```markdown
  <details>
  <summary>📸 Screenshot: <short caption></summary>

  ![Descriptive alt text that states what the image shows](../../../docs/assets/screenshots/lab-NN/NN-name.png)

  </details>
```

- The relative path from a lab README to the screenshots is `../../../docs/assets/screenshots/lab-NN/`.
- Write meaningful **alt text** that conveys the purpose of the image (per the
  repo's accessibility rules) — not "screenshot" or a bare filename.
- Place each block immediately after the step it illustrates.
- Preserve the **Objectives → Steps → Validation → Troubleshooting** order and the
  module's existing step numbering. If you add a step, renumber contiguously.

## Step 6 — Fix correctness defects (scoped)

If the walkthrough exposed factual errors (wrong field values, an inaccurate
version claim, a missing approval step, an outdated label), fix them — but keep
edits **minimal and scoped to this module**. Confirm any non-trivial wording or
behavioral change with the user before applying it, consistent with Step 3's
STOP-AND-ASK rule.

Do not refactor neighbouring labs or introduce new patterns. Mirror the existing
structure.

## Step 7 — Validate

1. Run the screenshot-inventory + lint check:

   **PowerShell** (Windows):

   ```powershell
   & ".github/skills/capture-lab-module-screenshots/scripts/Test-LabModule.ps1" -ReadmePath "labs/introduction-foundry-agent-service/NN-name/README.md"
   ```

   **Shell** (macOS/Linux):

   ```bash
   ".github/skills/capture-lab-module-screenshots/scripts/test-lab-module.sh" --readme "labs/introduction-foundry-agent-service/NN-name/README.md"
   ```

   The script confirms every image the README references exists on disk and runs
   markdownlint on the README. Fix anything it flags.

1. If the script is unavailable, run the lint directly:

   ```bash
   pnpm exec markdownlint-cli2 "labs/introduction-foundry-agent-service/NN-name/README.md"
   ```

## Step 8 — Record findings and present the result

1. If you discovered a durable fact (a portal quirk, a naming constraint, a
   behavior that contradicted the docs), add a short note to repository memory so
   future runs benefit.
1. Present to the user:
   - The module walked and whether every step worked as written.
   - Screenshots added (names + what each shows).
   - Any correctness defects fixed.
   - Lint / inventory status.
1. Ask whether to adjust captions, capture additional moments, or revise wording.

## Guardrails

- **Authentication is the user's job.** If a page needs sign-in, stop and ask.
- **Do not fake a passing walkthrough.** A step that does not work is a finding,
  not something to engineer around.
- **Ask before clicking anything you cannot reliably drive** — if a control will
  not respond to Playwright, ask the user to click it.
- **Keep edits scoped** to the named module; preserve lab numbering and section
  order.
- **Never commit secrets** or hardcode tunnel URLs/credentials into the README.
