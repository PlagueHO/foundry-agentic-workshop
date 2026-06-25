# Contributing to Microsoft Foundry Agentic Workshop

Thank you for your interest in contributing. This document explains how to participate effectively.

## Before you start

**Open an issue before submitting a pull request** for anything beyond trivial fixes (typos, broken links).

Opening an issue first lets maintainers confirm the change is in scope, avoids duplicated effort, and ensures your time is well spent.

## Ways to contribute

- **Bug reports** - incorrect lab steps, broken code, outdated screenshots
- **Content improvements** - clearer wording, better examples, missing validation steps
- **New lab content** - new lab modules that extend the existing progression
- **Infrastructure fixes** - Bicep correctness, security, or reliability improvements
- **Documentation** - guides, quickstarts, architecture docs

## Raising an issue

1. Search [existing issues](https://github.com/PlagueHO/foundry-agentic-workshop/issues) to avoid duplicates.
1. Open a [new issue](https://github.com/PlagueHO/foundry-agentic-workshop/issues/new) and fill in as much detail as possible:
   - What you expected to happen
   - What actually happened
   - The lab number and step (if applicable)
   - Your environment (OS, Python version, Azure region)
1. Wait for a maintainer to acknowledge and label the issue before opening a PR.

## Submitting a pull request

1. Fork the repository and create a branch from `main` with a descriptive name (for example, `fix/lab-04-missing-env-var` or `feat/lab-13-observability`).
1. Make your changes following the conventions below.
1. Verify your changes locally:
   - `pnpm run lint:md` - no Markdown lint errors
   - `az bicep lint --file infra/main.bicep` - no Bicep lint errors (if you changed Bicep)
   - `python -m compileall labs scripts shared` - Python compiles cleanly
1. Reference the issue your PR resolves in the PR description (for example, `Closes #42`).
1. Keep PRs focused - one concern per PR. Large or sweeping changes are harder to review and more likely to be rejected.

## Repository conventions

| Area | Convention |
|------|------------|
| Lab structure | Each lab requires `README.md`, `src/starter.py`, and `solution/` |
| Lab README sections | Objectives → Steps → Validation → Troubleshooting |
| Lab numbering | Preserve the `01`–`12` numbering and progression; do not renumber existing labs |
| Python style | Python 3.13, type hints, single-quoted strings, `main` entry point |
| Bicep | Follow [Azure Verified Modules](https://azure.github.io/Azure-Verified-Modules/) conventions |
| Markdown | GFM, `markdownlint-cli2` clean, no forced line wraps, `1.` for all ordered list items |
| Secrets | Never commit secrets, tokens, keys, or connection strings |
| Environment variables | Add all new variables to `shared/.env.example` |

## Lab content standards

- Steps must be concrete and numbered so an attendee can follow them without ambiguity.
- Validation sections must describe observable outcomes (commands, UI states, or printed output the attendee can verify).
- Use real, working example prompts - no placeholder text such as "enter some text here".
- Verify technical accuracy against [Microsoft Learn](https://learn.microsoft.com/azure/foundry/) before adding or changing steps.

## Code of conduct

This project follows the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). By participating you agree to abide by its terms. Report concerns to [opencode@microsoft.com](mailto:opencode@microsoft.com).

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](./LICENSE) that covers this project.
