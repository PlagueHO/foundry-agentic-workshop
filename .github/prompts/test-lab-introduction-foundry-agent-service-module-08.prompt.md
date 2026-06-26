---
description: "Test lab module 08 (Use Agent Framework for Python) end-to-end from a local terminal, verifying every step carefully. Requires the repository checked out locally, a configured .env with FOUNDRY_PROJECT_ENDPOINT, an authenticated Azure CLI session, and the grounded acl-remedy-advisor agent created in Modules 04-07. Does not require a GitHub Codespace or VS Code Insiders."
---

## Inputs

- ${input:attendeeUpn}: (Required) The UPN of the attendee to test with (e.g. `lab.attendee.1@MngEnvMCAP199525.onmicrosoft.com`).
- ${input:envName}: (Required) The azd environment name the lab was provisioned into (e.g. `foundry-hol2`).

---

You must test the steps in the #file:labs/introduction-foundry-agent-service/08-agent-framework-python/README.md from a local terminal in this repository. The attendee is `${input:attendeeUpn}` in the environment `${input:envName}`.

This module is run entirely from code: it connects to the grounded `acl-remedy-advisor` Prompt Agent built in Modules 04-07 and runs it from Python with the Microsoft Agent Framework. There is no Codespace or browser UI to drive for the core flow - the test runs the solution and starter scripts locally and verifies their output. The only prerequisites are the local repository, a configured `.env`, an authenticated Azure CLI session, and the agent existing in the Foundry project.

> **Important:** Any Azure login dialogs that appear during the test must be completed by the user. Pause and prompt the user whenever a sign-in dialog is encountered. Do not attempt to enter credentials automatically.

## Pre-flight - Verify the environment is ready

Before executing any lab steps, confirm all prerequisites are satisfied. **Do not proceed if any check fails** - report the failure and ask the user to resolve it.

### Check 1 - Confirm the repository and solution scripts are present

1. In a terminal at the repository root, confirm the module 08 scripts exist:

   ```bash
   ls labs/introduction-foundry-agent-service/08-agent-framework-python/src/starter.py
   ls labs/introduction-foundry-agent-service/08-agent-framework-python/solution/run_prompt_agent.py
   ls labs/introduction-foundry-agent-service/08-agent-framework-python/solution/create_knowledge_base_agent.py
   ```

1. Confirm all three paths resolve without error.

### Check 2 - Confirm dependencies are installed

1. Confirm the shared dependencies (which include `agent-framework`) are installed by running `uv sync` from the repo root if not already done:

   ```bash
   uv sync
   ```

1. Confirm `agent_framework` imports cleanly:

   ```bash
   uv run python -c "from agent_framework.foundry import FoundryAgent; print('agent_framework OK')"
   ```

   **Check:** If the import raises `ModuleNotFoundError`, run `uv sync` from the repo root and retry.

### Check 3 - Confirm the `.env` file exists and contains required values

1. Confirm `.env` exists and the required values are populated:

   ```bash
   cat .env | grep -E 'FOUNDRY_PROJECT_ENDPOINT|AGENT_NAME|AGENT_VERSION|RETAIL_REMEDY_OPS_MCP_SERVER_URL'
   ```

1. Confirm `FOUNDRY_PROJECT_ENDPOINT` is set to a non-empty value of the form `https://<resource>.services.ai.azure.com/api/projects/<project>`.
1. Confirm `AGENT_NAME` is either unset (the script defaults to `acl-remedy-advisor`) or set to `acl-remedy-advisor`.
1. Confirm `AGENT_VERSION` is either unset or empty (the script uses the latest published version when it is empty).
1. Confirm `RETAIL_REMEDY_OPS_MCP_SERVER_URL` is set to the shared **Azure Container Apps** MCP server URL the organizer deployed. It ends in `/mcp` and the host looks like `https://ca-mcp-<env>.<region>.azurecontainerapps.io/mcp`. The grounded `acl-remedy-advisor` agent calls this deployed server when its MCP tools fire during a run, so it must be present and reachable - no local server or tunnel is required.

   **Check:** If `.env` does not exist, confirm with the user that Module 01 has been completed, then copy `shared/.env.example` to `.env` and populate `FOUNDRY_PROJECT_ENDPOINT` and `RETAIL_REMEDY_OPS_MCP_SERVER_URL` from the attendee onboarding file at `.azure/${input:envName}/<upn_local>.md` (where `<upn_local>` is the part of `${input:attendeeUpn}` before `@`), or from `azd env get-values`.

### Check 4 - Confirm Azure authentication

1. Confirm the Azure CLI is signed in as the attendee:

   ```bash
   az account show --query '{user:user.name, subscription:id}' -o table
   ```

1. Confirm the output shows `${input:attendeeUpn}` as the signed-in user and that the subscription ID matches `AZURE_SUBSCRIPTION_ID` from the environment.
1. If the command fails or shows a different identity, pause and ask the user to run `az login` and complete the browser sign-in before continuing. Do not enter credentials automatically.

### Check 5 - Confirm the `acl-remedy-advisor` agent exists in the Foundry project

This module connects to the grounded `acl-remedy-advisor` Prompt Agent built across Modules 04-07.

1. Confirm the agent exists by listing the attendee's agents (the helper script reads `FOUNDRY_PROJECT_ENDPOINT` from `.env`):

   ```bash
   python scripts/list-attendee-projects.py
   ```

   If the helper is not applicable to a single attendee, confirm the agent another way - for example by running the module 08 solution in Part 3, which fails fast with a clear "agent not found" error if the agent is missing.

1. Confirm `acl-remedy-advisor` is present in the project.

   **Check:** If the agent does not exist (Module 07 was not completed), recreate its end state from the solution folder before continuing:

   ```bash
   python labs/introduction-foundry-agent-service/08-agent-framework-python/solution/create_knowledge_base_agent.py
   ```

   This script requires the additional environment variables documented in its header (for example `AZURE_SEARCH_SERVICE_NAME` and `KNOWLEDGE_BASE_NAME`). Confirm those are present in `.env` before running. After it completes, re-verify the agent exists, then continue.

---

## Part 1 - Run the agent from the solution script

The solution script `run_prompt_agent.py` is the completed version of `starter.py`. Running it is the deterministic way to validate that the agent connects and responds.

### Step 1 - Run the solution

1. From the repository root, run:

   ```bash
   python labs/introduction-foundry-agent-service/08-agent-framework-python/solution/run_prompt_agent.py
   ```

1. Wait for the script to complete.

   **Check:** If the script raises `KeyError: 'FOUNDRY_PROJECT_ENDPOINT'`, confirm `.env` is saved and that `FOUNDRY_PROJECT_ENDPOINT` is not blank (Check 3).

   **Check:** If the script raises an authentication error, run `az login` and retry (Check 4).

   **Check:** If the script reports the agent could not be found, recreate it with `solution/create_knowledge_base_agent.py` (Check 5), then retry.

### Step 2 - Verify the single-response output

1. Confirm the output contains an `Agent:` block followed by a complete answer printed in one piece.
1. Confirm the answer addresses the built-in `QUERY` (a $1,200 fridge that stopped cooling after 14 months with a 12-month store warranty) and includes:
   - A remedy recommendation under the Australian Consumer Law.
   - Reasoning that distinguishes a major failure from a minor failure, or otherwise justifies the remedy.

### Step 3 - Verify the streaming output

1. Confirm a second block appears, prefixed with `Agent (streaming):`.
1. Confirm the streamed answer is printed incrementally (token by token) rather than all at once, and that it conveys the same kind of grounded remedy guidance as the single-response block.
1. Confirm the script exits cleanly with no traceback after the streaming block.

---

## Part 2 - Complete and run the starter script

This part confirms the learner-facing path (completing the TODOs in `starter.py`) produces the same result as the solution.

### Step 4 - Complete the four TODOs in starter.py

1. Open [src/starter.py](labs/introduction-foundry-agent-service/08-agent-framework-python/src/starter.py).
1. Apply the four snippets from the README exactly:

   - **TODO 1** - import the client:

     ```python
     from agent_framework.foundry import FoundryAgent
     ```

   - **TODO 2** - connect to the existing Prompt Agent:

     ```python
     agent = FoundryAgent(
         project_endpoint=endpoint,
         agent_name=agent_name,
         agent_version=agent_version,
         credential=credential,
     )
     ```

   - **TODO 3** - run once and print the full response:

     ```python
     result = await agent.run(QUERY)
     print(f'\nAgent:\n{result.text}\n')
     ```

   - **TODO 4** - run again and stream the response:

     ```python
     print('Agent (streaming): ', end='', flush=True)
     async for chunk in agent.run(QUERY, stream=True):
         if chunk.text:
             print(chunk.text, end='', flush=True)
     print('\n')
     ```

1. Confirm the completed `starter.py` now matches the structure of `solution/run_prompt_agent.py` (the `agent = None` placeholder is replaced and all four TODO comments are resolved).

### Step 5 - Run the completed starter

1. From the repository root, run:

   ```bash
   python labs/introduction-foundry-agent-service/08-agent-framework-python/src/starter.py
   ```

1. Confirm it produces the same two blocks as the solution: a complete `Agent:` response followed by an incremental `Agent (streaming):` response.
1. Confirm the script exits cleanly with no traceback.

   **Check:** If the starter raises `TypeError` or `AttributeError` near the agent call, confirm TODO 2 created a real `FoundryAgent` (the `agent = None` placeholder must be replaced).

---

## Part 3 - Confirm the QUERY is configurable

### Step 6 - Change the QUERY and rerun

1. In `src/starter.py`, change the `QUERY` string to a different retail scenario, for example:

   ```python
   QUERY = (
       'A customer bought a $300 pair of running shoes that fell apart after '
       'three weeks of normal use. What remedy should we offer under the '
       'Australian Consumer Law, and why?'
   )
   ```

1. Rerun the starter:

   ```bash
   python labs/introduction-foundry-agent-service/08-agent-framework-python/src/starter.py
   ```

1. Confirm the response is clearly about the new scenario and differs from the fridge response, demonstrating that the query drives the grounded answer.

---

## Part 4 (optional) - Verify the runs appear in the Foundry portal Traces

This step uses only the Foundry portal in a browser and does not require a Codespace. Skip it if browser access is not available.

### Step 7 - Open the agent's Traces tab

1. Use `open_browser_page` to navigate to `https://ai.azure.com` and confirm the signed-in account matches `${input:attendeeUpn}`. If a login dialog appears, pause and ask the user to sign in. Do not enter credentials automatically.
1. Navigate to the attendee's Foundry project, open **Agents**, and select `acl-remedy-advisor`.
1. Open the **Traces** tab.
1. Confirm one or more traces recorded during this test (the solution run, the starter runs, and the changed-QUERY run) appear alongside any earlier playground conversations.
1. Take a screenshot of the Traces tab showing the recorded Python runs.

   **Check:** If no traces appear, refresh the page after a short wait - trace ingestion can lag a few seconds behind the run.

---

## Validation - confirm all criteria

Work through each item in the lab's Validation section and confirm:

1. The starter and solution scripts run without authentication or connection errors.
1. The first call prints a complete answer under `Agent:`.
1. The second call prints the same kind of answer token by token under `Agent (streaming):`.
1. Changing the `QUERY` string changes the response.
1. (Optional) The runs appear under the agent's **Traces** tab in the Foundry portal.

---

## Step 8 - Report results

Report the outcome of every step above. For each step state whether it **passed** or **failed**. For any failure, include:

- The exact step number and description.
- The observed behaviour.
- The expected behaviour.
- Any error messages, unexpected output, or unexpected state encountered.
- The screenshot filename or description if a screenshot was taken.

If all steps pass, confirm that lab module 08 end-to-end validation is complete.
