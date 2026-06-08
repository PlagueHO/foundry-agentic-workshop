---
title: Agent Operating Guide
description: Operating guidance for AI agents in the Microsoft Foundry workshop repo.
author: Foundry Agentic Workshop Maintainers
ms.date: 2026-06-06
ms.topic: how-to
---

## Scope

This repository hosts an facilitator-led Microsoft Foundry workshop with numbered labs, Bicep infrastructure, and shared Python utilities.

## Repository Layout

| Path | Purpose |
|------|---------|
| .github/ | Workflow and Copilot repo configuration |
| docs/ | Role-based workshop guides and delivery material |
| infra/ | Bicep infrastructure and deploy wrappers |
| labs/00-setup ... labs/11-publishing-agents | Sequential workshop modules |
| scripts/ | Operational helper scripts |
| shared/ | Shared Python dependencies, environment template, data, and utilities |

## Build, Lint, and Test Commands

Run from the repository root unless noted.

```bash
python -m pip install -r shared/requirements.txt
```

```bash
python scripts/health-check.py
```

```bash
python -m compileall labs scripts shared
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

## Change Checklist

* Keep lab numbering and progression intact across files and folders.
* Preserve runnable Python starter and solution structure for each lab.
* Run `az bicep build --file infra/main.bicep` and `az bicep lint --file infra/main.bicep` after Bicep edits.
* Do not commit secrets, tokens, keys, or connection strings.
* Keep `.env.example` templates synchronized with environment variable usage.

## CI Expectations

The GitHub workflow runs setup validation only for `.github/workflows/copilot-setup-steps.yml` changes, including Azure Bicep and Azure Developer CLI validation.

Treat local lint and validation commands as required quality gates before opening a PR.

## Repository Conventions

| Area | Convention |
|------|------------|
| Lab structure | Each lab includes README.md, src/starter.py, and solution/ |
| Python style | Type hints where practical, small focused functions, direct script entry points |
| Strings in Python | Prefer single quotes for literals |
| Infra | Bicep source in infra/ with azd-driven deploy and teardown |
| Shared config | Keep shared/.env.example as the canonical environment template |
