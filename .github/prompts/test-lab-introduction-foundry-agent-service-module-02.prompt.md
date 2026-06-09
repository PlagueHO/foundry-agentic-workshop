---
description: "Test lab module 02 (Foundry portal walkthrough) end-to-end for a specific attendee by opening ai.azure.com in a browser and verifying every step and validation criterion"
---

## Inputs

* ${input:attendeeUpn}: (Required) The UPN of the attendee to test with (e.g. `lab.attendee.1@MngEnvMCAP199525.onmicrosoft.com`).
* ${input:envName}: (Required) The azd environment name the lab was provisioned into (e.g. `foundry-hol2`).

---

You must test the steps in the #file:labs/introduction-foundry-agent-service/02-foundry-portal-walkthrough/README.md for the attendee specified by `${input:attendeeUpn}` in the environment `${input:envName}`.

Use the browser tools to open and navigate the portal. **Do not skip any navigation step.** After every navigation action, capture a screenshot and read the page content to verify the expected UI elements are present before proceeding to the next step.

## Step 1 — Locate the onboarding file

The lab organizer provisioned the environment with `azd provision`. The post-provision hook (#file:scripts/generate-attendee-onboarding.py) wrote a per-attendee onboarding file to:

```
.azure/${input:envName}/<upn_local>.md
```

Where `<upn_local>` is the part of the UPN before the `@` symbol. Read that file to obtain:

* `FOUNDRY_PROJECT_NAME` — the attendee's assigned project name.
* `FOUNDRY_PROJECT_ENDPOINT` — the expected project endpoint URL.

## Step 2 — Open the portal and sign in

1. Open the browser and navigate to `https://ai.azure.com`.
1. Take a screenshot and read the page to confirm it loaded.
1. If a login dialog or sign-in prompt is shown, **pause and instruct the user** to complete sign-in with the workshop account for `${input:attendeeUpn}`, then wait for confirmation before continuing.
1. After sign-in, take a screenshot and read the page to confirm the portal loaded and a project list or home page is displayed.

## Step 3 — Select the attendee's project

1. Locate the attendee's project in the project list. The project name is the `FOUNDRY_PROJECT_NAME` value from the onboarding file (for example, **lab-attendee-1**).
1. Click on that project to open it.
1. Take a screenshot and read the page to confirm the portal navigated into the project and the project name appears in the breadcrumb or page heading.
1. **Verify:** The project name in the breadcrumb matches `FOUNDRY_PROJECT_NAME` from the onboarding file. Fail if it does not.

## Step 4 — Verify the Home tab

1. Confirm the **Home** tab is currently selected (it is the default after project selection).
1. Take a screenshot and read the page.
1. **Verify:** A **Project endpoint** value is visible near the top of the page. Fail if no endpoint is displayed.
1. **Verify:** The displayed endpoint matches `FOUNDRY_PROJECT_ENDPOINT` from the onboarding file. Fail if it does not match.
1. **Verify:** Three quick-start cards — **Create agents**, **Explore playgrounds**, and **Find models** — are present on the page. Fail if any are missing.

## Step 5 — Verify the Discover tab

1. Click **Discover** in the top navigation bar.
1. Take a screenshot and read the page to confirm the Discover tab loaded.
1. **Verify:** The left sidebar contains the following sections: **Overview**, **Models**, **Agents**, **Tools**, and **Solution templates**. Fail if any are absent.

### 5a — Browse the model catalog

1. Click **Models** in the left sidebar.
1. Take a screenshot and read the page.
1. **Verify:** The model catalog page is shown with a list of model cards. Fail if no models are listed.
1. **Verify:** An **Availability** filter is present and its default value indicates **Available in my project** (or equivalent). Fail if the filter is absent.
1. Click **All models** (or the equivalent control to clear the availability filter) to view the full model catalog.
1. Take a screenshot and read the page.
1. **Verify:** The catalog now shows a significantly larger number of models and includes entries from multiple providers (for example, OpenAI, Anthropic, Microsoft, Meta, Mistral). Fail if the count did not increase or no provider variety is visible.
1. Click any model card to open its detail view.
1. Take a screenshot and read the page.
1. **Verify:** The model detail view shows at minimum a description and at least one of: supported inference tasks, context window size, or pricing information. Fail if none are present.
1. Navigate back to the model catalog (use the browser back button or breadcrumb).
1. Locate and click **Compare models** (top right of the catalog).
1. Take a screenshot and read the page.
1. **Verify:** A model comparison view or a dialog to select models for comparison is displayed. Fail if neither appears.

## Step 6 — Verify the Build tab

1. Click **Build** in the top navigation bar.
1. Take a screenshot and read the page to confirm the Build tab loaded.
1. **Verify:** The left sidebar contains all of the following sections: **Agents**, **Models**, **Fine-tune**, **Tools**, **Knowledge**, **Memory**, **Data**, **Evaluations**, and **Guardrails**. Fail if any are absent.

## Step 7 — Verify the Operate tab

1. Click **Operate** in the top navigation bar.
1. Take a screenshot and read the page to confirm the Operate tab loaded.
1. **Verify:** An **Overview** dashboard is shown. Fail if not.
1. **Verify:** The dashboard contains at least two of the following metrics: **Running agents**, **Estimated cost**, **Agent success rate**, **Token usage**. Fail if fewer than two are present.
1. **Verify:** The left sidebar contains at least the following sections: **Assets**, **Compliance**, **Quota**, **Admin**. Fail if any are absent.

## Step 8 — Validate the Validation criteria

Confirm each item listed in the **Validation** section of the lab README is satisfied:

1. The **Project endpoint** is visible on the Home tab and matches the value in the onboarding file.
1. Navigating to **Discover > Models** with **Available in my project** filter active shows the deployed models for this project.
1. The **Agents**, **Knowledge**, and **Evaluations** sections are visible on the Build tab.
1. The Operate tab Overview dashboard is accessible and displays agent health and cost metrics.

## Reporting

Report the result of every verification step clearly:

* **PASS** — element found and value matched as expected.
* **FAIL** — element missing, value mismatched, or navigation failed; include the exact page text or error that caused the failure.
* **BLOCKED** — step could not be reached due to a prior failure; list the blocking step.

If any step results in **FAIL**, continue testing remaining independent steps and summarise all failures at the end.
