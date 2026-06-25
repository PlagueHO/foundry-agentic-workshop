---
description: "Test lab module 11 (Agent operations and Agent ID) end-to-end entirely in the browser as a first-time Foundry user, verifying every step and capturing clarifying screenshots. Requires a provisioned lab environment with at least one prior agent run, and an authenticated browser session signed in as the lab attendee. Opens the ai.azure.com and portal.azure.com portals using open_browser_page and persists screenshots to docs/assets/screenshots/introduction-foundry-agent-service/lab-11 for documentation improvement."
---

## Inputs

- ${input:attendeeUpn}: (Required) The UPN of the attendee to test with (e.g. `lab.attendee.1@MngEnvMCAP199525.onmicrosoft.com`).
- ${input:envName}: (Required) The azd environment name the lab was provisioned into (e.g. `foundry-hol8`).

---

You must test the steps in the #file:labs/introduction-foundry-agent-service/11-agent-ops-and-agent-id/README.md entirely in the browser. The attendee is `${input:attendeeUpn}` in the provisioned environment `${input:envName}`.

This module is a guided observability and identity tour. It locates the **Entra Agent Identity** and **agent identity blueprint** for an agent, inspects per-agent **Traces** and **Monitor** tabs for both the `acl-remedy-advisor` prompt agent and a hosted agent from [Module 09](../../labs/introduction-foundry-agent-service/09-hosted-agents/README.md), tours the **Operate** control plane, opens the **Agents** view in Azure Monitor (Application Insights), and reviews where continuous evaluation and red team scans are configured.

This test is **browser-only**. Use `open_browser_page` (and the related browser tools) to drive `https://ai.azure.com` and `https://portal.azure.com`. Do not run any terminal commands, Python scripts, Azure CLI commands, or MCP servers - this module has none. The only setup the environment needs is a provisioned project with **at least one prior agent run** so telemetry exists.

> **Approach every step as a person who has never used Microsoft Foundry before.** Do not rely on prior knowledge of where controls live. Follow the README literally, find each control as a first-time attendee would, and note anywhere the written instruction was not enough to locate or understand the control without guessing.
>
> **Important:** Any Azure sign-in dialogs that appear during the test must be completed by the user. Pause and prompt the user whenever a sign-in dialog is encountered. Do not attempt to enter credentials automatically.

## Screenshots - capture and persist

Screenshots from this test may be reused to improve the Module 11 documentation, so persist them to disk in the lab's screenshot folder.

1. Save every screenshot to `docs/assets/screenshots/introduction-foundry-agent-service/lab-11/` using the naming `NN-descriptive-kebab.png`, numbered in the order the steps appear (for example `01-details-tab-agent-identity.png`).
1. Because the browser runs on the local machine, save to the **local disk path** via `run_playwright_code`. Create the folder on first save if it does not exist:

   ```js
   await page.screenshot({ path: 'docs/assets/screenshots/introduction-foundry-agent-service/lab-11/NN-descriptive-kebab.png' });
   ```

1. Frame each shot on the relevant control, dialog, or result the step describes. Re-open menus or panels as needed so the screenshot shows the exact state.
1. Capture a screenshot at every step marked **📸 Capture** below. These are the moments a first-time attendee is most likely to get lost.

## Clarification recommendations

As you walk the lab as a first-time user, watch for anything that would make the process inaccurate, unclear, or unreliable, and collect a list of recommended documentation improvements. Treat the following as triggers for a recommendation:

- A control, tab, or sidebar entry the README names cannot be found where described, or is labelled differently in the portal.
- A placeholder or unresolved value the attendee must supply (for example `<your-hosted-agent>`, **to be confirmed**, or **TBD**) without enough guidance to resolve it.
- A step that assumes prior context, skips a navigation hop, or only works after an action the README does not mention.
- An expected element (column, card, metric, view) that is absent, empty, or named differently.
- Any moment where you had to guess to proceed.

For each trigger, record: the exact step, what the README says, what you actually observed, and a concrete suggested wording or screenshot that would remove the ambiguity. Report these together in the final results.

## Pre-flight - Verify the environment is ready

Before executing any lab steps, confirm the prerequisites are satisfied. **Do not proceed if a check fails** - report the failure and ask the user to resolve it.

### Check 1 - Open the Foundry portal and sign in

1. Use `open_browser_page` to navigate to `https://ai.azure.com`.
1. Read the page to confirm it loaded.
1. If a login dialog or sign-in prompt appears, pause and ask the user to sign in as `${input:attendeeUpn}`. Do not enter credentials automatically.
1. After sign-in, confirm the **New Foundry** toggle is on (top of the portal). If it is off, turn it on.
1. Navigate to the attendee's Foundry project and confirm the project workspace loads.

### Check 2 - Confirm telemetry exists

1. The Traces and Monitor views require at least one prior agent run and the project's Application Insights connection.
1. Confirm with the user that the `acl-remedy-advisor` agent (and a hosted agent from Module 09, if available) has been run at least once in this environment.

   **Check:** If no agent has been run, the Traces and Monitor grids will be empty. Record this as a blocking condition and ask the user to run an agent once from an earlier module, then continue.

### Check 3 - Identify the hosted agent name

The README refers to the hosted agent as `<your-hosted-agent>` and notes its name is **to be confirmed** in this revision.

1. Ask the user for the exact name of the hosted agent they built in Module 09 (for example `acl-remedy-advisor-hosted-1`).
1. If the user cannot supply it, plan to discover it under **Build → Agents** in Part 4 and record that the README left this value unresolved as a clarification recommendation.

---

## Part 1 - Find the agent identity on the Details tab

### Step 1 - Open the agent and its Details tab

1. In the project, select **Build** in the top navigation.
1. Open the `acl-remedy-advisor` agent.
1. Select the **Details** tab (marked **Preview**).
1. Read the page to confirm the Details tab loaded.

   **📸 Capture:** the Details tab showing the agent's identity information.

### Step 2 - Locate the Entra Agent Identity and blueprint

1. Locate the **Entra Agent Identity** value for the agent.
1. Confirm the README's claim: because `acl-remedy-advisor` is not yet published, it uses the **shared default project agent identity**.
1. Locate the associated **agent identity blueprint** value.
1. Confirm you understand what the identity is used for: governance (inventory, policy, audit) and secret-free tool authentication to downstream services.

   **Check:** If the **Entra Agent Identity** or **blueprint** fields are not visible on the Details tab, record exactly which field is missing and where you looked, and add a clarification recommendation.

   **📸 Capture:** the panel showing the Entra Agent Identity and blueprint values (redact nothing - these are non-secret identifiers).

---

## Part 2 - Per-agent operations: Traces (Conversations)

### Step 3 - Open Traces and switch sub-tabs

1. With `acl-remedy-advisor` still open, select the **Traces** tab.
1. Switch between the **Conversations** and **Responses** sub-tabs and confirm both load:
   - **Conversations** groups activity by conversation.
   - **Responses** lists individual model responses.

   **📸 Capture:** the **Conversations** sub-tab with at least one row of activity.

### Step 4 - Review the columns and scope the view

1. Confirm the grid shows the documented columns: **Conversation ID**, **Trace ID**, **Response ID**, **Status**, **Created at**, **Duration (s)**, **Tokens (In)**, **Tokens (Out)**, **Estimated cost ($)**, **Evaluation**, and **Agent version**.
1. Use the date-range selector (**Last Day**, **7D**, **1M**, **3M**) to scope the view so rows appear.

   **Check:** If the grid is empty, expand the date range and refresh. If it remains empty, confirm the agent has been run (Check 2) and note ingestion can lag a few minutes.

### Step 5 - Drill into a single trace

1. Select a **Trace ID** to open the execution path for that run.
1. Confirm the drill-down shows model and tool spans, timings, and inputs/outputs.

   **📸 Capture:** the trace drill-down showing the execution path.

---

## Part 3 - Per-agent operations: Monitor

### Step 6 - Open Monitor and read the summary

1. Select the **Monitor** tab.
1. Confirm the **summary cards** appear at the top and the **charts** appear below.

   **📸 Capture:** the Monitor dashboard showing summary cards and charts.

### Step 7 - Interpret the metrics

1. Confirm the dashboard surfaces the documented metrics: **Token usage**, **Latency**, **Run success rate**, and **Evaluation metrics**.
1. Locate the **gear icon** that opens **Monitor settings** (where continuous evaluation and red team scans are configured in Part 7).

   **Check:** If a documented metric or the gear icon is absent or named differently, record what you saw and add a clarification recommendation.

---

## Part 4 - Repeat for the hosted agent

> **Note:** Use the hosted agent from Module 09. Its name was supplied in Check 3 or is discovered here. Substitute it for `<your-hosted-agent>` throughout this part.

### Step 8 - Open the hosted agent's Details tab

1. Under **Build → Agents**, locate and open the hosted agent (name from Check 3, e.g. `acl-remedy-advisor-hosted-1`).
1. If you could not get the name in Check 3, record the actual hosted agent name you found here and confirm it against the README's `acl-remedy-advisor-hosted-*` pattern.
1. Select the **Details** tab and locate its **Entra Agent Identity**.
1. Confirm it has a **distinct agent identity and blueprint** rather than the shared project identity - verify this value differs from the one observed in Step 2 for `acl-remedy-advisor`.

   **📸 Capture:** the hosted agent's Details tab showing its distinct Entra Agent Identity.

### Step 9 - Review the hosted agent's Traces and Monitor

1. On the **Traces** tab, review the hosted agent's conversations and responses as in Part 2.
1. On the **Monitor** tab, review its operational metrics and evaluation scores as in Part 3.
1. Confirm the distinct identity isolates the hosted agent's permissions, auditability, and telemetry from the in-development agents.

   **📸 Capture:** the hosted agent's Monitor or Traces view confirming separate telemetry.

   **Check:** If the hosted agent is missing, record that Module 09 must be completed first and treat this part as blocked rather than failed.

---

## Part 5 - The Operate control plane

### Step 10 - Open Operate

1. Select **Operate** in the top navigation.
1. Confirm the control plane aggregates health and metrics across agents using their connected Application Insights resources.
1. Confirm the view covers prompt-based agents, workflows, hosted agents, and manually registered custom agents.

   **📸 Capture:** the Operate control plane overview showing agents across the project.

   **Check:** Different users may see different agents depending on access. If the view is empty for this attendee, note their access level rather than failing.

---

## Part 6 - The Agents view in Application Insights

### Step 11 - Open the Azure portal Application Insights resource

1. Use `open_browser_page` (or a new tab) to navigate to `https://portal.azure.com`.
1. If a sign-in dialog appears, pause and ask the user to sign in as `${input:attendeeUpn}`. Do not enter credentials automatically.
1. Navigate to the **Application Insights** resource connected to the attendee's Foundry project.

   **Check:** If the attendee cannot locate or open the Application Insights resource, record the access requirement (Log Analytics Reader) as a clarification recommendation, since the README does not say how to find the resource name.

### Step 12 - Open the Agents (details) view

1. Under **Investigate**, open the **Agents (details)** view.
1. Confirm the view surfaces agent performance and run activity, token usage and estimated cost, and errors and failures.

   **📸 Capture:** the Agents (details) view in Application Insights.

   **Check:** If **Agents (details)** is not under **Investigate** or is named differently, record the actual location and add a clarification recommendation.

---

## Part 7 (extra credit) - Configure evaluations and red teaming

> **Important:** Creating evaluation and red-team configurations changes project settings and typically requires the **`foundry-project-manager`** role or higher. If the attendee has the `foundry-user` role, walk through this part read-only without applying changes and record that in the report.

### Step 13 - Open Monitor settings

1. Return to the **Monitor** tab for `acl-remedy-advisor` and select the **gear icon** to open **Monitor settings**.
1. Confirm the settings expose: **Continuous evaluation**, **Scheduled evaluations** (preview), **Red team scans** (preview), and **Alerts** (preview).

   **📸 Capture:** the Monitor settings panel listing the evaluation and red-team options.

   **Check:** If the attendee's role blocks configuration, confirm the settings are read-only and record this as expected behaviour, not a failure.

---

## Validation - confirm all criteria

Work through each item in the lab's Validation section and confirm:

1. You can locate the **Entra Agent Identity** and blueprint on the **Details** tab and explain that `acl-remedy-advisor` uses the shared project identity while the hosted agent uses a distinct one.
1. You can open **Traces → Conversations** for both agents, read the run columns, and drill into a single trace.
1. You can read the **Monitor** dashboard metrics and locate where continuous evaluation and red team scans are configured.
1. You can open the **Operate** control plane and the **Agents (details)** view in Application Insights.
1. *(Extra credit)* You located the Monitor settings for continuous evaluation, scheduled evaluation, and scheduled red team scan (and configured them if your role allowed).

---

## Step 14 - Report results

Report the outcome of every step above. For each step state whether it **passed**, **failed**, or was **skipped/blocked** (with the reason, for example hosted agent not built or role does not permit configuration). For any failure or block, include:

- The exact step number and description.
- The observed behaviour.
- The expected behaviour.
- Any error messages, unexpected output, or unexpected portal state encountered.
- The screenshot filename saved under `docs/assets/screenshots/introduction-foundry-agent-service/lab-11/` that illustrates the step.

Then provide two summaries:

1. **Screenshots captured** - the full list of saved filenames with a one-line caption for each, so they can be reused to improve the module documentation.
1. **Clarification recommendations** - every ambiguity, missing control, unresolved placeholder (such as the hosted agent name or **TBD** estimated time), or guess you had to make, each with the exact step, what the README says, what you observed, and a concrete suggested fix.

If all non-skipped steps pass, confirm that lab module 11 end-to-end browser validation is complete.
