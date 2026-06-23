---
description: 'Structure, style, and formatting rules for lab module README files in labs/'
applyTo: 'labs/**/*.md'
---

# Lab Module README Rules

Apply these rules when creating or editing any `README.md` inside `labs/`.

## Lab Content Rules

- Write Steps as concrete, imperative instructions an attendee can follow without ambiguity.
- Write Validation as observable outcomes the attendee can verify (commands, UI states, printed output).
- **Verify technical accuracy against Microsoft Learn (`learn.microsoft.com/azure/ai-foundry/`) before adding or changing steps.**
- Keep tone encouraging and approachable; attendees range from beginner to expert.
- Use real, working example prompts in lab steps; avoid placeholder text such as "enter some text here".
- Use `- [ ]` task-list checkboxes for every attendee action so progress can be tracked.
- Separate consecutive `> [!...]` callout blocks with `<!-- markdownlint-disable-next-line MD028 -->`.
- Do **not** add a `## See also` section to any lab module README — cross-references belong inline or in callouts.

## Lab Module README Structure

Both the `introduction-foundry-agent-service` and `agent-framework-dotnet` lab modules follow the same section order and style conventions.

### Section order

```text
# NN. Title
**Estimated time:** N minutes
![diagram](path)
> [!IMPORTANT]  ← prerequisite callout (omit for module 01)
<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]        ← "tick the checkbox" reminder
## Objectives
## Concepts
## Steps
## Validation
## Congratulations 🎉
## Troubleshooting
```

### Title format

Use `# NN. Title` — two-digit zero-padded number, period, space, title. No "Module" prefix.

```markdown
# 04. Function Tools
```

### Prerequisite callout

Use a `> [!IMPORTANT]` block immediately after the diagram. Reference prerequisite modules with bare `[Module NN](relative/path)` link text — include no title in the link text.

```markdown
> [!IMPORTANT]
> This module builds on [Module 02](../02-first-agent/README.md). The `AIAgent` pattern from Module 02 is used here with an added tool.
```

### Steps structure

Group related steps into named parts using `### Part N — Description`. Number individual steps with `#### N. Step title`. Each attendee action is a `- [ ]` item. Embed code blocks directly under the step item (indented 2 spaces), not in a separate sub-item.

````markdown
### Part 1 — Complete the starter code

#### 1. Open the starter file

- [ ] Open `src/Program.cs` in the editor.

#### 2. Create the project client (TODO 1)

- [ ] Locate `// ── TODO 1` and replace the commented-out block with:

  ```csharp
  var credential = new DefaultAzureCredential();
  ```
````

### Screenshots

Embed screenshots in a collapsible block immediately after the step item that triggers them:

```markdown
- [ ] Click **Save**.

  <details>
  <summary>📸 Screenshot: Save button location</summary>

  ![Save button highlighted in the toolbar](../../../docs/assets/screenshots/...)

  </details>
```

### Congratulations section

End with a short paragraph summarising what the attendee achieved, followed immediately by a `> [!TIP]` next-up link. Use `Module NN: Title` format in the tip link text.

```markdown
## Congratulations 🎉

You added a function tool to your agent ...

> [!TIP]
> **Next up → [Module 05: MCP Tools](../05-mcp-tools/README.md)**
> Replace the function tool with a remote MCP server.
```

### Troubleshooting section

Use a two-column `| Symptom | Fix |` table. Always include a row for `NotImplementedException` when the module has TODOs.

```markdown
## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `AuthenticationFailedException` | Run `az login` or confirm your managed identity has the correct role |
| `NotImplementedException` | A TODO is still incomplete — check the starter code |
```
