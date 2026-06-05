# Copilot Instructions for Azure AI Foundry Workshop

- Keep all labs runnable with Python and `.env.example` templates.
- Never commit secrets, tokens, keys, or connection strings.
- Keep workshop content aligned to Azure AI Foundry terminology and workflows.
- Prefer small, reviewable changes that preserve numbered lab progression.

## Markdown linting

All `.md` files are linted with [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2).

### Running locally

```bash
# Check for issues
npm run lint:md

# Auto-fix issues
npm run lint:md:fix
```

### VS Code integration

Install the [markdownlint extension](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint) (`DavidAnson.vscode-markdownlint`) to see lint errors inline as you edit.

### Key rules

Configuration lives in `.markdownlint.json` and `.markdownlint-cli2.jsonc`. Notable settings:

- **MD013** (line length): disabled — no line length limit.
- **MD024** (duplicate headings): siblings only — duplicate headings allowed if not siblings.
- **MD029** (ordered list style): `one` — all list items use `1.`.
- **MD033** (inline HTML): only `br` and `kbd` are permitted.
- **MD041** (first line heading): disabled — files need not start with a heading.

### CI

The `lint-markdown` workflow runs automatically on push and pull requests that touch `.md` files. Fix all issues before merging.
