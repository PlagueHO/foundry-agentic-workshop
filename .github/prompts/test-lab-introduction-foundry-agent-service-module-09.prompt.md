---
description: "Test lab module 09 (Build and run a hosted agent) end-to-end from a local terminal, verifying every step carefully. Requires a provisioned lab environment, the repository checked out locally, a configured .env with FOUNDRY_PROJECT_ENDPOINT and container-registry values, an authenticated Azure CLI session signed in as the lab attendee, and an open_browser_page already on the authenticated ai.azure.com Foundry portal for the same attendee. Docker is optional (Part 1 only)."
---

## Inputs

- ${input:attendeeUpn}: (Required) The UPN of the attendee to test with (e.g. `lab.attendee.1@MngEnvMCAP199525.onmicrosoft.com`).
- ${input:envName}: (Required) The azd environment name the lab was provisioned into (e.g. `foundry-hol8`).

---

You must test the steps in the #file:labs/introduction-foundry-agent-service/09-hosted-agents/README.md from a local terminal in this repository. The attendee is `${input:attendeeUpn}` in the provisioned environment `${input:envName}`.

This module packages a code-first Agent Framework agent and deploys it as a **hosted agent** running fully managed inside the attendee's Foundry project. Hosted agents are a **preview** feature; the SDK calls pass `allow_preview=True` and use `project.beta.agents`. The test deploys the agent (Part 2 from source code is the primary path; Part 1 from a container image is optional and needs Docker), invokes the deployed endpoint over the Responses protocol, and then verifies the deployed agent and its metrics in the Foundry portal.

The lab environment must already be provisioned and the Azure CLI must already be signed in as the attendee. An `open_browser_page` is already open on `https://ai.azure.com`, authenticated as the same attendee, so you can confirm the deployed hosted agent and inspect its metrics in the portal.

> **Important:** Any Azure login dialogs that appear during the test must be completed by the user. Pause and prompt the user whenever a sign-in dialog is encountered. Do not attempt to enter credentials automatically.

## Pre-flight - Verify the environment is ready

Before executing any lab steps, confirm all prerequisites are satisfied. **Do not proceed if any check fails** - report the failure and ask the user to resolve it.

### Check 1 - Confirm the repository, agent bundle, and scripts are present

1. In a terminal at the repository root, confirm the module 09 scripts and agent bundle exist:

   ```bash
   ls labs/introduction-foundry-agent-service/09-hosted-agents/src/starter.py
   ls labs/introduction-foundry-agent-service/09-hosted-agents/src/agent/main.py
   ls labs/introduction-foundry-agent-service/09-hosted-agents/solution/deploy_hosted_agent_code.py
   ls labs/introduction-foundry-agent-service/09-hosted-agents/solution/deploy_hosted_agent_container.py
   ls labs/introduction-foundry-agent-service/09-hosted-agents/solution/invoke_hosted_agent.py
   ls labs/introduction-foundry-agent-service/09-hosted-agents/solution/hosted_agent_support.py
   ```

1. Confirm all paths resolve without error.

### Check 2 - Activate the virtual environment and confirm dependencies

1. Activate the `.venv` virtual environment from the repository root:

   - **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
   - **macOS / Linux:** `source .venv/bin/activate`

1. Confirm the terminal prompt now shows the `(.venv)` prefix.
1. Confirm the shared dependencies are installed:

   ```bash
   python -m pip install -r shared/requirements.txt
   ```

1. Confirm the Foundry projects SDK imports cleanly:

   ```bash
   python -c "from azure.ai.projects import AIProjectClient; print('azure.ai.projects OK')"
   ```

   **Check:** If the import raises `ModuleNotFoundError`, reinstall `shared/requirements.txt` in the active environment and retry. Confirm the `(.venv)` prefix is present so the install targets the correct interpreter.

### Check 3 - Confirm the `.env` file exists and contains required values

1. Confirm `.env` exists and the required hosted-agent values are populated:

   ```bash
   cat .env | grep -E 'FOUNDRY_PROJECT_ENDPOINT|AZURE_SUBSCRIPTION_ID|AZURE_RESOURCE_GROUP|FOUNDRY_RESOURCE_NAME|AZURE_CONTAINER_REGISTRY_NAME|AZURE_CONTAINER_REGISTRY_ENDPOINT|HOSTED_AGENT_NAME_CONTAINER|HOSTED_AGENT_NAME_CODE|AGENT_MODEL|RETAIL_REMEDY_OPS_MCP_SERVER_URL|RETAIL_REMEDY_OPS_MCP_SERVER_LABEL'
   ```

1. Confirm `FOUNDRY_PROJECT_ENDPOINT` is set to a non-empty value of the form `https://<resource>.services.ai.azure.com/api/projects/<project>`.
1. Confirm `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `FOUNDRY_RESOURCE_NAME`, `AZURE_CONTAINER_REGISTRY_NAME`, and `AZURE_CONTAINER_REGISTRY_ENDPOINT` are all set to non-empty values.
1. Confirm `RETAIL_REMEDY_OPS_MCP_SERVER_URL` is set to a non-empty public URL ending in `/mcp` (the Module 06 MCP server endpoint), and that `RETAIL_REMEDY_OPS_MCP_SERVER_LABEL` is either unset (defaults to `retail_remedy_ops`) or set to `retail_remedy_ops`.
1. Confirm `HOSTED_AGENT_NAME_CONTAINER` (defaults to `acl-remedy-advisor-hosted-container`) and `HOSTED_AGENT_NAME_CODE` (defaults to `acl-remedy-advisor-hosted-code`) are either unset or set to their defaults, and that `AGENT_MODEL` is either unset (defaults to `chat`) or set to `chat`.

   **Check:** If `.env` does not exist, confirm with the user that Module 01 has been completed, then copy `shared/.env.example` to `.env` and populate the values from the attendee onboarding file at `.azure/${input:envName}/<upn_local>.md` (where `<upn_local>` is the part of `${input:attendeeUpn}` before `@`), or from `azd env get-values`.

### Check 4 - Confirm the Module 06 MCP server is running and publicly exposed

The hosted agent calls the **Retail Remedy Operations MCP server** from Module 06 over `RETAIL_REMEDY_OPS_MCP_SERVER_URL` at runtime. The server must be running and reachable on its public dev-tunnel URL for the deploy verification and invoke steps to succeed.

1. Confirm the MCP server is running locally (Module 06 starts it with `python shared/mcp-servers/retail-remedy-ops/src/server.py`).
1. Confirm `RETAIL_REMEDY_OPS_MCP_SERVER_URL` points to the **public** dev-tunnel URL (ending in `/mcp`), not a `localhost` address - the hosted agent runs in Foundry's managed compute and cannot reach `localhost`.
1. Confirm the public endpoint responds:

   ```bash
   curl -i -X POST "$RETAIL_REMEDY_OPS_MCP_SERVER_URL" -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
   ```

   **Check:** Expect an HTTP `200` with a JSON-RPC response listing the `retail_remedy_ops` tools. If the request fails or times out, restart the Module 06 server, re-expose the dev tunnel publicly, and update `RETAIL_REMEDY_OPS_MCP_SERVER_URL` before continuing. If you change the URL after deploying, you must redeploy the agent.

### Check 5 - Confirm Azure authentication

1. Confirm the Azure CLI is signed in as the attendee:

   ```bash
   az account show --query '{user:user.name, subscription:id}' -o table
   ```

1. Confirm the output shows `${input:attendeeUpn}` as the signed-in user and that the subscription ID matches `AZURE_SUBSCRIPTION_ID` from the environment.
1. If the command fails or shows a different identity, pause and ask the user to run `az login` and complete the browser sign-in before continuing. Do not enter credentials automatically.

### Check 6 - Confirm the constrained role-assignment permission

The deploy scripts assign the hosted agent's own Microsoft Entra identity the **Foundry User** role after the version becomes active. This requires the project to have been provisioned with the constrained Role Based Access Control Administrator role.

1. Confirm with the user that the lab environment `${input:envName}` was provisioned by the facilitator (which grants this constrained role).
1. No command is required here - the assignment is attempted automatically during deploy. If it fails with `PrincipalNotFound` or an authorization error, capture the error for the Troubleshooting follow-up rather than retrying blindly.

### Check 7 - Confirm the browser portal session is ready

1. Use the already-open `open_browser_page` on `https://ai.azure.com` and confirm the signed-in account matches `${input:attendeeUpn}`.
1. If a login dialog appears, pause and ask the user to sign in. Do not enter credentials automatically.
1. Navigate to the attendee's Foundry project and confirm the **Agents** list loads. Note whether `acl-remedy-advisor-hosted-container` or `acl-remedy-advisor-hosted-code` already exist (from a prior run) so you can distinguish a fresh deployment later.

---

## Part 1 - Deploy from a container image (optional, needs Docker)

This part needs **Docker** and the **Azure CLI**. If Docker is not available, skip to **Part 2** - it deploys a separate hosted agent without Docker.

### Step 1 - Check for Docker

1. Confirm Docker is available:

   ```bash
   docker --version
   ```

   **Check:** If the command reports `docker: command not found` (or similar), record Part 1 as **skipped (Docker unavailable)** and proceed to Part 2.

### Step 2 - Deploy the agent from a container image

1. From the repository root, run:

   ```bash
   python labs/introduction-foundry-agent-service/09-hosted-agents/solution/deploy_hosted_agent_container.py
   ```

1. Watch the status messages: the script builds for `linux/amd64`, logs in to the shared registry, pushes the image under the project-specific tag, creates the hosted agent version, waits for it to become active, and assigns the agent identity the Foundry User role.
1. Confirm the script prints `Hosted agent acl-remedy-advisor-hosted-container is active.`

   **Check:** If a role-assignment error appears, note it for Troubleshooting (Check 6). The version may still be active even if the role takes a moment to propagate.

---

## Part 2 - Deploy from source code (preview, recommended)

This is the primary deployment path. Foundry zips `src/agent/`, builds the image remotely, and runs it as a hosted agent - no local Docker required.

### Step 3 - Complete the three TODOs in starter.py

1. Open [src/starter.py](labs/introduction-foundry-agent-service/09-hosted-agents/src/starter.py).
1. Apply the three snippets so the starter matches `solution/deploy_hosted_agent_code.py`:

   - **TODO 1** - build the `CreateAgentVersionFromCodeContent`:

     ```python
     content = CreateAgentVersionFromCodeContent(
         metadata=CreateAgentVersionFromCodeMetadata(
             description='ACL Remedy Advisor hosted agent deployed from source code.',
             definition=HostedAgentDefinition(
                 cpu=CPU,
                 memory=MEMORY,
                 environment_variables={'AZURE_AI_MODEL_DEPLOYMENT_NAME': model_deployment},
                 code_configuration=CodeConfiguration(
                     runtime=RUNTIME,
                     entry_point=['python', 'main.py'],
                     dependency_resolution=CodeDependencyResolution.REMOTE_BUILD,
                 ),
                 protocol_versions=[ProtocolVersionRecord(protocol='responses', version='1.0.0')],
             ),
         ),
         code=(f'{agent_name}.zip', zip_bytes, 'application/zip'),
     )
     ```

   - **TODO 2** - create the agent version from code:

     ```python
     created = client.beta.agents.create_version_from_code(
         agent_name=agent_name,
         content=content,
         code_zip_sha256=zip_sha256,
     )
     print(f'Created hosted agent {agent_name} version {created.version}; Foundry is building it.')
     ```

   - **TODO 3** - wait for the version to become active and grant the agent identity RBAC:

     ```python
     wait_for_agent_version_active(client, agent_name, created.version)
     ensure_agent_identity_rbac(created, credential)
     ```

1. Confirm the completed `starter.py` no longer raises `NotImplementedError` and that the `content = ...` placeholder and all three TODO comments are resolved. Ensure `wait_for_agent_version_active` and `ensure_agent_identity_rbac` are imported from `hosted_agent_support` (the solution imports them at the top of the file).

### Step 4 - Run the completed starter

1. From the repository root, run:

   ```bash
   python labs/introduction-foundry-agent-service/09-hosted-agents/src/starter.py
   ```

1. Confirm the output includes `Built code archive from ...`, then `Created hosted agent acl-remedy-advisor-hosted-code version <n>; Foundry is building it.`, and finally `Hosted agent acl-remedy-advisor-hosted-code is active.`.
1. Confirm the script exits cleanly with no traceback.

   **Check:** If the starter raises `NameError` or `ImportError`, confirm the TODO 1-3 snippets were applied and that the support helpers are imported (Step 3).

   **Check:** If the version never becomes active, open the agent in the Foundry portal and read the version's build logs. A failed remote build usually means a dependency in `src/agent/requirements.txt` could not be installed.

   **Check:** If you get stuck, run the reference implementation instead and continue:

   ```bash
   python labs/introduction-foundry-agent-service/09-hosted-agents/solution/deploy_hosted_agent_code.py
   ```

---

## Part 3 - Invoke the hosted agent

### Step 5 - Chat with the deployed hosted agent

1. From the repository root, run:

   ```bash
   python labs/introduction-foundry-agent-service/09-hosted-agents/solution/invoke_hosted_agent.py
   ```

1. Confirm the script prints `Using hosted agent acl-remedy-advisor-hosted-code version <n>.` and `Session created (...)`.
1. Confirm the first prompt (a laptop on receipt `R-1007` with dead pixels after 14 months) returns a grounded remedy answer under the Australian Consumer Law that references the receipt/purchase rather than answering generically.
1. Confirm the second prompt (the follow-up about the original box and charger) produces a context-aware answer that builds on the first turn.
1. Confirm the script prints `Session deleted (...)` and exits cleanly with no traceback.

   **Check:** If the invoke fails with a 403 at runtime, the Foundry User role may still be propagating to the new agent identity. Wait a minute and retry.

   **Check:** If the agent is reported not found, confirm Part 2 completed successfully and that `HOSTED_AGENT_NAME_CODE` matches in `.env`.

---

## Part 4 - Verify the deployment and metrics in the Foundry portal

Use the already-open, authenticated `open_browser_page` on `https://ai.azure.com`. Do not enter credentials automatically - pause for the user if a sign-in dialog appears.

### Step 6 - Confirm the hosted agent appears with an active version

1. In the portal, open the attendee's Foundry project and select **Agents**.
1. Confirm `acl-remedy-advisor-hosted-code` (and `acl-remedy-advisor-hosted-container` if Part 1 ran) appears in the list with an **active** version.
1. Open the agent and confirm it is a hosted agent (not a Prompt Agent) and that the version created during this test is active.
1. Take a screenshot of the agent's overview showing the active version.

### Step 7 - Inspect the hosted agent's metrics

1. In the agent view, open the **Metrics** (or **Monitoring** / **Observability**) area for `acl-remedy-advisor-hosted-code`.
1. Confirm metrics reflect the invocation from Step 5 - for example request count, latency, or session activity recorded during this test.
1. If a **Traces** tab is available, confirm one or more traces from the invoke run appear, and that the hosted agent called its retail tools (for example looking up receipt `R-1007`) rather than answering generically.
1. Take a screenshot of the metrics (and traces, if shown) for the hosted agent.

   **Check:** If no metrics or traces appear, refresh the page after a short wait - ingestion can lag a few seconds behind the run.

---

## Validation - confirm all criteria

Work through each item in the lab's Validation section and confirm:

1. The deploy step prints `Hosted agent acl-remedy-advisor-hosted-code is active.` (Part 2), and `Hosted agent acl-remedy-advisor-hosted-container is active.` if Docker was available for Part 1.
1. `invoke_hosted_agent.py` prints a grounded remedy answer for the first prompt and a context-aware answer for the follow-up.
1. `acl-remedy-advisor-hosted-code` (and `acl-remedy-advisor-hosted-container` if Part 1 ran) appears in the **Agents** list in the Foundry portal with an active version.
1. The hosted agent calls its retail tools (for example receipt `R-1007`) rather than answering generically.
1. The Foundry portal shows metrics (and, if available, traces) for the hosted agent reflecting this test's invocation.

---

## Step 8 - Report results

Report the outcome of every step above. For each step state whether it **passed**, **failed**, or was **skipped** (with the reason, for example Docker unavailable in Part 1). For any failure, include:

- The exact step number and description.
- The observed behaviour.
- The expected behaviour.
- Any error messages, unexpected output, or unexpected state encountered.
- The screenshot filename or description for any screenshot taken.

If all non-skipped steps pass, confirm that lab module 09 end-to-end validation is complete.
