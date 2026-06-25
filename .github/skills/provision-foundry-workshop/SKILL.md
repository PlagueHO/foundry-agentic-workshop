---
name: provision-foundry-workshop
description: >-
  **WORKFLOW SKILL** - Provision a shared Microsoft Foundry workshop environment
  for multiple attendees. Collects five parameters interactively when not supplied,
  validates the attendee roster, runs azd provision, and verifies RBAC assignments,
  AI Search population, audit CSVs, and per-attendee onboarding files.
  WHEN: "provision workshop", "set up the foundry workshop", "deploy foundry lab",
  "prepare the workshop environment", "run workshop setup", "provision foundry
  workshop". INVOKES: vscode_askQuestions, run_in_terminal (azd, az).
  FOR SINGLE OPERATIONS: Follow docs/guide-organizer.md directly.
metadata:
  author: foundry-workshop
  version: "1.0"
compatibility:
  - GitHub Copilot
  - GitHub Copilot CLI
  - VS Code Insiders
argument-hint: >-
  Optionally supply: env=<name> location=<azure-region> rg=<resource-group>
  default-role=<role-key> attendees=<json-array>
---

# Provision Foundry Workshop

End-to-end provisioning of a shared Microsoft Foundry workshop environment.
Implements the full setup described in `docs/guide-organizer.md`.

## Parameters

| Parameter | azd variable | Required | Default | Description |
|-----------|-------------|----------|---------|-------------|
| `env` | `AZURE_ENV_NAME` | Yes | - | azd environment name, e.g. `my-workshop` |
| `location` | `AZURE_LOCATION` | Yes | - | Azure region slug, e.g. `australiaeast` |
| `rg` | `AZURE_RESOURCE_GROUP` | Yes | - | Target resource group name |
| `default-role` | `AZURE_ATTENDEE_DEFAULT_ROLE` | No | `foundry-user` | Default role for attendees without an explicit `role` field |
| `attendees` | `AZURE_ATTENDEE_LIST` | Yes | - | JSON array of attendee objects - see format below |

### Attendee entry format

```json
{ "upn": "user@tenant.com", "role": "<optional-role-key>" }
```

Valid role keys: `foundry-user` · `foundry-project-manager` · `foundry-account-owner` · `foundry-owner` · `facilitator` · `proctor` · `organizer`

Omit `role` to use the `default-role`. Entries with role `facilitator`, `proctor`,
or `organizer` always receive Foundry Owner at account scope.

## Step 1 - Collect parameters

Extract each parameter from the invocation text. If any required parameter is absent,
call `vscode_askQuestions` once with all missing parameters as separate questions.

When asking for the attendee list, display this example to guide the user:

```json
[
  {"upn": "alice@contoso.com"},
  {"upn": "bob@contoso.com"},
  {"upn": "facilitator@contoso.com", "role": "facilitator"},
  {"upn": "proctor@contoso.com", "role": "proctor"},
  {"upn": "organizer@contoso.com", "role": "organizer"}
]
```

## Step 2 - Validate attendee list

Parse and validate before touching azd. Fail fast with a clear error if any
check fails, and ask the user to correct the list before proceeding.

1. Must parse as valid JSON array.
1. Every entry must have a `upn` field containing `@`.
1. Any explicit `role` value must be one of the valid role keys listed above.
1. No duplicate `upn` values.

Display the validated roster as a table (UPN | effective role | project scope)
and ask the user to confirm before continuing.

## Step 3 - Configure azd environment

```bash
azd env new <env>
azd env set AZURE_LOCATION <location>
azd env set AZURE_RESOURCE_GROUP <rg>
azd env set AZURE_ATTENDEE_DEFAULT_ROLE <default-role>
azd env set AZURE_ATTENDEE_LIST '<attendees-as-single-line-json>'
```

If `azd env new` fails because the environment already exists, run
`azd env select <env>` instead. Serialize the attendee array to a single-line
JSON string before passing it to `azd env set`.

Confirm the active environment with `azd env list` before proceeding.

## Step 4 - Provision

```bash
azd provision
```

The pre-provision hook (`scripts/prepare-attendee-roles.py`) resolves each UPN
to a Microsoft Entra object ID, computes project names, and writes a resolution
audit CSV to `.azure/<env>/`.

Bicep deploys all Azure resources with RBAC role assignments embedded.

The post-provision hook (`scripts/generate-attendee-onboarding.py`) writes
per-attendee onboarding markdown files, a provisioning summary CSV, and seeds
the AI Search indexes - all under `.azure/<env>/`.

Provisioning takes several minutes. Do not interrupt. Wait for full completion
before running Step 5.

## Step 5 - Validate

Run all four checks. Report each result individually and surface any failures.

### 5a. UPN resolution audit

```powershell
Get-ChildItem ".azure/<env>/attendee-resolution-*.csv" |
  Sort-Object LastWriteTime -Descending | Select-Object -First 1 |
  ForEach-Object { Import-Csv $_.FullName | Format-Table }
```

Confirm every row has `resolved=True`. For any row with `resolved=False`,
display the `message` column and advise the user to check the UPN or
Entra guest invitation.

### 5b. RBAC provisioning summary

```powershell
Get-ChildItem ".azure/<env>/attendee-provisioning-*.csv" |
  Sort-Object LastWriteTime -Descending | Select-Object -First 1 |
  ForEach-Object { Import-Csv $_.FullName | Format-Table }
```

Confirm every row has `status=succeeded`. Flag any `status=failed` rows.

### 5c. Per-attendee onboarding files

```powershell
Get-ChildItem ".azure/<env>/*.md" | Select-Object Name
```

Confirm a `.md` file exists for each resolved attendee.

### 5d. AI Search index health

```bash
python scripts/health-check.py
```

Confirm no AI Search errors appear in the output. If indexes are reported
empty, wait 60 seconds and retry - the seeding step may still be running.

## Step 6 - Report

Summarise the provisioning outcome:

* Environment name and resource group
* Count of attendees provisioned vs. failed
* Location of per-attendee onboarding files: `.azure/<env>/`
* IMPORTANT: Remind organizer to deliver each attendee's `.md` file to the facilitator for distribution before the workshop - see `docs/quickstart-facilitator.md`
