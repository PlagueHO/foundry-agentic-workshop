# Lab Validation and Testing Guide

This guide defines the standard validation workflow to run after making changes to workshop labs and related guides.

It uses the prompt files in `.github/prompts` as the source of truth for end-to-end verification.

## Purpose

Use this guide whenever you change:

1. Any lab content in `labs/introduction-foundry-agent-service/**`.
1. Attendee guidance in `docs/guide-attendee.md`.
1. Organizer guidance in `docs/guide-organizer.md`.
1. Setup or onboarding scripts used by those flows.

The objective is to confirm the written steps still work in a real provisioned environment.

## Prompt-based test suite

The repository currently provides these validation prompts:

| Prompt file | Scope | Expected inputs |
|---|---|---|
| `.github/prompts/test-lab-introduction-foundry-agent-service-module-01.prompt.md` | End-to-end validation of Lab 01 setup flow | `attendeeUpn`, `envName` |
| `.github/prompts/test-attendee-guide.prompt.md` | End-to-end validation of attendee guide | `attendeeUpn`, `envName` |
| `.github/prompts/test-organizer-guide.prompt.md` | End-to-end validation of organizer provisioning and outputs | Built-in values in prompt |

## Preconditions

Before running validations:

1. Ensure Azure CLI authentication is active (`az login`).
1. Ensure `azd` authentication is active (`azd auth login`, if required by your environment).
1. Ensure the target workshop environment has been provisioned (for example `foundry-hol2`).
1. Ensure onboarding files exist under `.azure/<envName>/` for the attendees being tested.

## Validation workflow after lab changes

Run the following workflow in order after any lab or guide change.

### 1. Validate Lab 01 setup flow

Run `.github/prompts/test-lab-introduction-foundry-agent-service-module-01.prompt.md` with:

1. `attendeeUpn`: a valid attendee UPN in the provisioned environment.
1. `envName`: the environment name used for provisioning.

Pass criteria:

1. Onboarding file resolves correctly.
1. `.env` is populated from onboarding values.
1. Dependency installation succeeds.
1. `az login` and subscription checks succeed.
1. `uv run python scripts/health-check.py` passes.
1. Validation section checks in Lab 01 pass.

### 2. Validate attendee guide

Run `.github/prompts/test-attendee-guide.prompt.md` with the same attendee and environment.

Pass criteria:

1. Required onboarding variables are present.
1. `.env` mapping is correct.
1. `uv run python scripts/health-check.py` passes.
1. Project naming expectation is satisfied.

### 3. Validate organizer guide

Run `.github/prompts/test-organizer-guide.prompt.md`.

Pass criteria:

1. Provisioning path in organizer guide completes for the configured attendee list.
1. RBAC assignments are present and correct.
1. AI Search data has been populated.
1. Output artifacts are present and correct in `.azure/<envName>/`, including:
   1. CSV output from `scripts/prepare-attendee-roles.py`.
   1. Per-attendee onboarding markdown files from `scripts/generate-attendee-onboarding.py`.

## Evidence to capture in PRs

When a change affects labs or guides, include a short validation summary in the pull request:

1. Prompt(s) executed.
1. Input values used (`attendeeUpn`, `envName` where applicable).
1. Pass or fail result per prompt.
1. Exact command output for any failure.
1. Any follow-up fix commit references.

## When to add or update prompts

If you modify a lab beyond module 01, add a corresponding test prompt under `.github/prompts` so future changes can be validated the same way.

Use this naming pattern:

1. `test-lab-introduction-foundry-agent-service-module-<NN>.prompt.md`

Keep prompt structure consistent with existing prompts:

1. Inputs section.
1. Onboarding file discovery step.
1. `.env` generation step.
1. Step-by-step validation against the target lab README.
1. Explicit pass criteria matching the README Validation section.

## Minimum quality gate for lab-affecting changes

Do not consider a lab-affecting change complete until:

1. The relevant prompt-based validations pass.
1. Any related markdown lint checks pass.
1. Any related Python lint or test checks pass for touched code paths.

This keeps workshop instructions reliable for attendees, facilitators, proctors, and organizers.
