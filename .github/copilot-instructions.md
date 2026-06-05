---
title: Copilot Instructions for Azure AI Foundry Workshop
description: Repository-specific code authoring and review guidance for Copilot interactions.
author: Foundry Agentic Workshop Maintainers
ms.date: 2026-06-06
ms.topic: reference
---

## Purpose

See AGENTS.md for repository layout and commands.

Apply these instructions to generated code, Markdown edits, and PRs.

## Security and Safety Rules

- Never commit secrets, tokens, keys, or connection strings.
- Keep credentials in environment variables and document only placeholder values.
- Treat shared/.env.example as the source of truth for expected environment variable names.
- Avoid destructive infrastructure guidance in docs unless explicitly requested and clearly labeled.

## Workshop Content Rules

- Preserve numbered lab progression from 00 through 08.
- Keep each lab independently understandable and runnable.
- Align content language with Azure AI Foundry terminology and workflows.
- Prefer small, reviewable changes scoped to one lab or concern.

## Python Authoring Rules

- Use Python 3.11+ syntax.
- Prefer explicit, typed functions for reusable helpers.
- Keep scripts simple and executable, with a clear `main` entry point when applicable.
- Prefer single-quoted Python strings unless escaping makes double quotes clearer.
- Keep output messages actionable, especially for setup and troubleshooting scripts.

## Naming and Structure Rules

- Match existing directory and filename patterns exactly when adding labs or assets.
- For new lab assets, mirror existing parallel structure before introducing new patterns.
- Keep shared helper logic in shared/ and lab-specific logic within the owning lab folder.
- Do not move or rename lab folders unless explicitly requested.

## Markdown Authoring Rules

- Keep instructional writing concise, direct, and step-oriented.
- Use stable headings that work with sequential workshop delivery.
- Keep setup, validation, and troubleshooting sections clearly separated in lab docs.
- Avoid adding session-specific dates or temporary event details outside date-scoped sections.

## Avoid Patterns

- Avoid broad refactors that touch multiple labs without a clear need.
- Avoid introducing framework or language changes that break Python-first workshop flow.
- Avoid introducing conflicting terms for the same Foundry concept across docs.
