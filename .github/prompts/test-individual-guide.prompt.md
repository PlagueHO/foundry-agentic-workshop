---
description: "Test the individual guide end-to-end: provision as a solo learner, validate .env, health-check, confirm blob upload is skipped, and confirm portal deploys normally"
argument-hint: "azureLocation=... resourceGroup=... environmentName=..."
---

## Inputs

* ${input:azureLocation}: (Required) Azure region to deploy to (e.g., `AustraliaEast`).
* ${input:resourceGroup}: (Required) Azure resource group name (e.g., `rg-foundry-lab`).
* ${input:environmentName}: (Required) azd environment name (e.g., `my-foundry-lab`).

---

You must test the steps in the #file:docs/guide-individual.md using the inputs above.

I have already authenticated to `az` and `azd`. The provisioning will take some time.

## Step 1 - Set up the azd environment

Follow the setup steps from the guide:

1. Create the azd environment.

   ```bash
   azd env new ${input:environmentName}
   ```

1. Set the required variables.

   ```bash
   azd env set AZURE_LOCATION ${input:azureLocation}
   azd env set AZURE_RESOURCE_GROUP ${input:resourceGroup}
   azd env set AZURE_INDIVIDUAL_MODE true
   ```

1. Confirm the values were written correctly with `azd env get-values`.

## Step 2 - Provision

Run `azd provision` and wait for it to complete. Capture the full output.

Confirm all three hooks ran and report their exit codes:

* Pre-provision: `scripts/prepare-attendee-roles.py`
* Post-provision: `scripts/generate-attendee-onboarding.py`
* Post-provision: `scripts/deploy-attendee-portal.py`

## Step 3 - Validate the pre-provision hook output

Inspect the output from `scripts/prepare-attendee-roles.py` (#file:scripts/prepare-attendee-roles.py) and confirm:

1. The hook detected individual mode and did **not** require `AZURE_ATTENDEE_LIST`.
1. A single resolved-attendee entry was synthesised and emitted to `AZURE_ATTENDEE_LIST_RESOLVED`.
1. The `projectName` in the resolved entry matches the expected UPN-derived pattern: the local part of the signed-in UPN (text before `@`), with `.` and `_` replaced by `-`, lowercased, and truncated to 32 characters.
1. The `objectId` in the resolved entry is non-empty (sourced from `AZURE_PRINCIPAL_ID`).
1. A resolution audit CSV was written to `.azure/${input:environmentName}/`.

## Step 4 - Validate the post-provision onboarding hook output

Inspect the output from `scripts/generate-attendee-onboarding.py` (#file:scripts/generate-attendee-onboarding.py) and confirm:

1. `.env` was written to the repository root and contains the following keys with non-empty values:
   * `AZURE_SUBSCRIPTION_ID`
   * `AZURE_RESOURCE_GROUP`
   * `FOUNDRY_RESOURCE_NAME`
   * `FOUNDRY_PROJECT_NAME`
   * `FOUNDRY_PROJECT_ENDPOINT`
   * `AZURE_OPENAI_ENDPOINT`
1. `FOUNDRY_PROJECT_NAME` in `.env` matches the derived project name verified in Step 3.
1. An onboarding index (`index.json`) was written to `.azure/${input:environmentName}/`.
1. Blob storage upload was **skipped** (confirm from hook output that no upload log lines appear).

## Step 5 - Validate the portal deploy hook ran

Inspect the output from `scripts/deploy-attendee-portal.py` (#file:scripts/deploy-attendee-portal.py) and confirm:

1. The portal image was built and pushed to the container registry.
1. The Container App was updated with the new image.
1. EasyAuth was configured on the Container App.

## Step 6 - Run the health check

Run `python scripts/health-check.py` and confirm it passes with no errors. Report any failures with the exact error output.

## Step 7 - Report results

Produce a summary table of all validation items:

| Step | Check | Result |
|------|-------|--------|
| Pre-provision | Individual mode detected, no attendee list required | |
| Pre-provision | Resolved entry synthesised with correct projectName | |
| Pre-provision | Resolved entry objectId is non-empty | |
| Pre-provision | Resolution audit CSV written | |
| Post-provision | `.env` written to repo root with required keys | |
| Post-provision | `FOUNDRY_PROJECT_NAME` matches UPN derivation | |
| Post-provision | `index.json` written to `.azure/${input:environmentName}/` | |
| Post-provision | Blob storage upload skipped | |
| Portal hook | Portal image built, pushed, and Container App updated | |
| Health check | `python scripts/health-check.py` passes | |

Mark each result as ✅ Pass, ❌ Fail, or ⚠️ Warning. For any failure, include the exact error output below the table.
