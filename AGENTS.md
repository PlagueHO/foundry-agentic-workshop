---
title: Agent Operating Guide
description: Operating guidance for AI agents in the Microsoft Foundry workshop repo.
author: Foundry Agentic Workshop Maintainers
ms.date: 2026-06-06
ms.topic: how-to
---

## Scope

This repository hosts a facilitator-led Microsoft Foundry workshop with numbered labs, Bicep infrastructure, and shared Python utilities.

## Repository Layout

| Path | Purpose |
|------|---------|
| .github/workflows/ | CI/CD pipeline definitions |
| .github/instructions/ | Copilot code-authoring instruction files |
| docs/ | VitePress workshop guide site (guides, quickstarts, architecture) |
| docs/assets/ | Banners, diagrams, icons, and screenshots |
| infra/ | Bicep infrastructure and azd deploy wrappers |
| labs/introduction-foundry-agent-service/ | All 12 numbered lab modules (01–12) |
| labs/introduction-foundry-agent-service/NN-name/ | Each lab: README.md, src/starter.py, solution/ |
| scripts/ | Operational helpers: health-check, attendee provisioning, data seeding |
| shared/ | .env.example, data/, schemas/ |
| tests/smoke/ | PowerShell smoke tests (Smoke.Tests.ps1) |
| tools/ | Python data-generator tooling |

## Build, Lint, and Test Commands

Run from the repository root unless noted.

```bash
uv sync
```

```bash
uv run python scripts/health-check.py
```

```bash
uv run python -m compileall labs scripts shared
```

```bash
az bicep build --file infra/main.bicep
```

```bash
az bicep lint --file infra/main.bicep
```

```bash
azd provision
```

```bash
azd env get-values
```

```bash
azd down --force --purge
```

```bash
pnpm run docs:generate-labs
```

```bash
pnpm run docs:build
```

```bash
pnpm run lint:md
```

```bash
pnpm run lint:md:fix
```

## Change Checklist

* Keep lab numbering and progression intact across files and folders.
* **New labs must include** `README.md`, `src/starter.py`, and `solution/` directory.
* Preserve runnable Python starter and solution structure for each lab.
* **Run** `az bicep build --file infra/main.bicep` **and** `az bicep lint --file infra/main.bicep` **after Bicep edits.**
* **Run** `pnpm run lint:md` **after editing any** `.md` **file.**
* Do not commit secrets, tokens, keys, or connection strings.
* Keep `shared/.env.example` synchronized with all environment variable usage.

## CI Expectations

The `continuous-integration` workflow triggers on changes to `docs/**`, `labs/**`, `scripts/**`, `shared/**`, and `infra/**`. It runs:

* **markdown-lint** - `pnpm run lint:md:ci`; blocks merge on any failure.
* **docs-build** - `pnpm run docs:build`; blocks merge on build errors.
* **lint-and-publish-bicep** - `az bicep lint` on all Bicep files; blocks merge.
* **validate-infrastructure** - validates Bicep parameters and deploy config.

Treat local lint and validation commands as required quality gates before opening a PR.

## Repository Conventions

| Area | Convention |
|------|------------|
| Lab structure | Each lab: README.md, src/starter.py, solution/ |
| Lab README sections | Objectives → Steps → Validation → Troubleshooting |
| Python style | Type hints where practical, small focused functions, `main` entry point |
| Strings in Python | Prefer single quotes for literals |
| Infra | Bicep source in infra/ with azd-driven deploy and teardown |
| Shared config | `shared/.env.example` is the canonical environment template |
| Docs | VitePress site; lab pages auto-generated via `pnpm run docs:generate-labs` |
| Markdown lint | `markdownlint-cli2`; run `pnpm run lint:md` before committing `.md` files |
