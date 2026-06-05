---
title: Agent Operating Guide
description: Operating guidance for AI agents in the Azure AI Foundry workshop repo.
author: Foundry Agentic Workshop Maintainers
ms.date: 2026-06-06
ms.topic: how-to
---

## Scope

This repository hosts an instructor-led Azure AI Foundry workshop with numbered labs, Terraform, and shared Python utilities.

## Repository Layout

| Path | Purpose |
|------|---------|
| .github/ | Workflow and Copilot repo configuration |
| docs/ | Instructor and facilitator material |
| infra/ | Terraform infrastructure and deploy wrappers |
| labs/00-setup ... labs/08-agent-id-and-publishing | Sequential workshop modules |
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
cd infra && terraform init
```

```bash
cd infra && terraform fmt -recursive
```

```bash
cd infra && terraform validate
```

```bash
cd infra && terraform plan -out=tfplan
```

```bash
cd infra && terraform apply tfplan
```

```bash
cd infra && terraform destroy
```

## Change Checklist

* Keep lab numbering and progression intact across files and folders.
* Preserve runnable Python starter and solution structure for each lab.
* **Run `terraform fmt -recursive` in infra/ after Terraform edits.**
* Do not commit secrets, tokens, keys, or connection strings.
* Keep `.env.example` templates synchronized with environment variable usage.

## CI Expectations

The GitHub workflow runs setup validation only for `.github/workflows/copilot-setup-steps.yml` changes, including Terraform and Azure Developer CLI installation.

Treat local lint and validation commands as required quality gates before opening a PR.

## Repository Conventions

| Area | Convention |
|------|------------|
| Lab structure | Each lab includes README.md, src/starter.py, and solution/ |
| Python style | Type hints where practical, small focused functions, direct script entry points |
| Strings in Python | Prefer single quotes for literals |
| Infra | Terraform source in infra/ with wrapper scripts for deploy and teardown |
| Shared config | Keep shared/.env.example as the canonical environment template |
