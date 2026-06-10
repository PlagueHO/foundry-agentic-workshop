---
description: "Test lab module 01 (Workshop setup and access verification) end-to-end for a specific attendee using their provisioned onboarding file to configure the environment"
---

## Inputs

* ${input:attendeeUpn}: (Required) The UPN of the attendee to test with (e.g. `lab.attendee.1@MngEnvMCAP199525.onmicrosoft.com`).
* ${input:envName}: (Required) The azd environment name the lab was provisioned into (e.g. `foundry-hol2`).

---

You must test the steps in the #file:labs/introduction-foundry-agent-service/01-setup/README.md for the attendee specified by `${input:attendeeUpn}` in the environment `${input:envName}`.

## Step 1 — Locate the onboarding file

The lab organizer provisioned the environment with `azd provision`. The post-provision hook (#file:scripts/generate-attendee-onboarding.py) wrote a per-attendee onboarding file to:

```bash
.azure/${input:envName}/<upn_local>.md
```

Where `<upn_local>` is the part of the UPN before the `@` symbol. Read that file to obtain the attendee's environment variable values.

## Step 2 — Create the `.env` file

Using the values from the onboarding file, copy `shared/.env.example` to `.env` in the repository root and populate the following variables from the onboarding file's `## Your Environment Variables` section:

* `AZURE_SUBSCRIPTION_ID`
* `AZURE_RESOURCE_GROUP`
* `FOUNDRY_RESOURCE_NAME`
* `FOUNDRY_PROJECT_NAME`
* `FOUNDRY_PROJECT_ENDPOINT`
* `AZURE_OPENAI_ENDPOINT`
* `AZURE_SEARCH_SERVICE_NAME`

Leave organizer-only values (e.g. `AZURE_ATTENDEE_LIST`, `AZURE_SEARCH_ADMIN_KEY`) blank or at their defaults from the example file.

## Step 3 — Validate the lab steps

Follow and validate each step from #file:labs/introduction-foundry-agent-service/01-setup/README.md:

1. Confirm the onboarding file exists at the expected path and contains all required environment variables.
1. Confirm the `.env` file has been correctly populated from the onboarding file values.
1. Confirm `shared/requirements.txt` exists and is non-empty.
1. Run `python -m pip install -r shared/requirements.txt` and confirm it succeeds with no errors.
1. Run `az login` and confirm it succeeds; confirm the active subscription matches `AZURE_SUBSCRIPTION_ID` from the onboarding file.
1. Run `python scripts/health-check.py` and confirm it passes with no errors.
1. Confirm the `FOUNDRY_PROJECT_NAME` from the onboarding file matches the expected project name pattern for the attendee's UPN (local part of UPN, dots/underscores replaced with hyphens, lowercased, capped at 32 characters) or the configured sequential name pattern.

## Step 4 — Validate the Validation criteria

Confirm each item listed in the **Validation** section of the lab README is satisfied:

1. `az login` succeeded and the active subscription matches the workshop subscription.
1. All required `.env` values are populated and non-empty.
1. `python scripts/health-check.py` reported a healthy environment.

Report the result of each step clearly, noting any failures with the exact error output.
