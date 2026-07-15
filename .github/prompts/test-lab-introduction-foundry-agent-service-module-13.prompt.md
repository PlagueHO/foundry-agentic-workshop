---
description: "Test lab module 13 (Build a custom engine agent) end-to-end as a first-time attendee, including Azure and Entra provisioning, the local proxy, a development tunnel, Teams sideloading, and the complete conversation path. Requires an attendee-owned Azure subscription and Entra tenant, permission to create app registrations and Azure Bot Service resources, access to the workshop Foundry project, and authenticated browser sessions. Persists non-secret screenshots to docs/assets/screenshots/introduction-foundry-agent-service/lab-13."
---

## Inputs

- ${input:foundryUserUpn}: (Required) The UPN that can access the workshop Foundry project and `acl-remedy-advisor` (for example, `lab.attendee.1@MngEnvMCAP199525.onmicrosoft.com`).
- ${input:botTenantUserUpn}: (Required) The UPN in the attendee-owned tenant that can create an app registration, resource group, and Azure Bot Service.
- ${input:botSubscriptionId}: (Required) The attendee-owned Azure subscription ID where the Module 13 resources may be created.
- ${input:envName}: (Required) The azd environment name that contains the workshop Foundry project (for example, `foundry-hol8`).

---

You must test every step in #file:labs/introduction-foundry-agent-service/13-custom-engine-agent/README.md as a first-time attendee. Use `${input:botTenantUserUpn}` and `${input:botSubscriptionId}` for the attendee-owned Entra and Azure Bot Service resources. Use `${input:foundryUserUpn}` for access to the workshop Foundry project in `${input:envName}`.

This optional module creates an Entra app registration and client secret, deploys an Azure Bot Service into an attendee-owned subscription, runs a local FastAPI proxy on port 3978, exposes it through a public HTTPS development tunnel, packages and sideloads a Teams custom app, and sends a message through Teams to the existing `acl-remedy-advisor` Foundry agent.

Use terminal tools for repository, Azure CLI, dependency, proxy, tunnel, packaging, and HTTP checks. Use `open_browser_page` and related browser tools for Microsoft Entra, the Azure portal, Microsoft Foundry, and Microsoft Teams. The user must complete every interactive sign-in and credential prompt. Never enter credentials, MFA codes, client secrets, or tokens on the user's behalf.

> **Approach every step as a person who has never built or sideloaded a Teams app.** Follow the README literally before using repository knowledge to recover. Record every point where the instructions are inaccurate, incomplete, ordered incorrectly, or require guessing.
>
> **Security:** Never read an existing client secret from `.env`, print it, include it in tool output, place it in a screenshot, or report it. The provisioning script prints a newly created secret once; allow that output to remain only in the user's terminal and ask the user to place it in `.env` themselves. Do not transmit the secret through chat or browser automation.

## Test boundaries and resource consent

This test has persistent side effects outside the repository:

- Creates an Entra app registration and one-year client secret.
- Creates or updates an Azure resource group and Azure Bot Service resource.
- Enables the Microsoft Teams channel on the Bot Service.
- Updates `appPackage/manifest.json` with the created app ID.
- Creates a local Teams app ZIP package.
- Uploads a custom app to the attendee-owned Teams tenant.

Before creating any resource, show the user the exact subscription ID, tenant ID, resource-group name, Bot Service name, and Azure region. Ask for explicit confirmation to proceed. Do not provision until the user confirms. Record all created resource names and IDs needed for cleanup, but never record the client secret.

Do not delete resources at the end unless the user explicitly asks. Include cleanup commands in the final report.

## Screenshots - capture and persist

Screenshots may be reused to improve Module 13, so save them to `docs/assets/screenshots/introduction-foundry-agent-service/lab-13/`.

1. Use the naming `NN-descriptive-kebab.png`, numbered in lab order (for example, `01-bot-service-configuration.png`).
1. Create the folder before the first capture if it does not exist.
1. Persist browser screenshots to the local disk with `run_playwright_code`:

   ```js
   await page.screenshot({ path: 'docs/assets/screenshots/introduction-foundry-agent-service/lab-13/NN-descriptive-kebab.png' });
   ```

1. Frame each screenshot around the relevant portal, Teams control, configuration, or result.
1. Capture every state marked **Capture** below.
1. Inspect every screenshot before reporting it. Retake any image containing a client secret, access token, authorization header, tenant-sensitive sign-in dialog, unrelated personal information, or notification content.

## Clarification recommendations

Collect documentation recommendations while testing. Create a recommendation whenever:

- A README instruction cannot be followed in its written order.
- A named control is absent, moved, or labelled differently.
- The README assumes a tool is installed without naming or installing it.
- A command requires an environment value that the README says to leave unset.
- The implementation does not match the documented architecture, authentication, or protocol behavior.
- A Teams manifest field, icon, policy, or packaging requirement is missing.
- The workflow needs one Azure identity for the Bot Service subscription and another for the workshop Foundry project without explaining how authentication switches.
- You must guess, consult another source, or perform an undocumented recovery step.

For each recommendation, record the exact README step, its current wording, the observed behavior, and concrete replacement wording or a suggested screenshot.

## Pre-flight - verify the environment is ready

Do not create resources until every blocking check passes and the user grants resource consent.

### Check 1 - confirm the module files and optional dependencies

1. From the repository root, confirm these paths exist:

   ```powershell
   Get-Item labs/introduction-foundry-agent-service/13-custom-engine-agent/README.md
   Get-Item labs/introduction-foundry-agent-service/13-custom-engine-agent/src/main.py
   Get-Item labs/introduction-foundry-agent-service/13-custom-engine-agent/src/agent.py
   Get-Item labs/introduction-foundry-agent-service/13-custom-engine-agent/solution/main.py
   Get-Item labs/introduction-foundry-agent-service/13-custom-engine-agent/solution/agent.py
   Get-Item labs/introduction-foundry-agent-service/13-custom-engine-agent/solution/start_server.py
   Get-Item labs/introduction-foundry-agent-service/13-custom-engine-agent/solution/provision_bot_service.py
   Get-Item labs/introduction-foundry-agent-service/13-custom-engine-agent/appPackage/manifest.json
   Get-Item labs/introduction-foundry-agent-service/13-custom-engine-agent/infra/bot-service.bicep
   ```

1. Run `uv sync --group module-13`.
1. Confirm the declared Microsoft 365 Agents SDK packages and FastAPI import successfully:

   ```powershell
   uv run python -c "import fastapi; import microsoft_agents; print('Module 13 dependencies OK')"
   ```

   **Check:** If the import path differs from the installed package API, inspect the package rather than hiding the failure. Record the mismatch and use a valid minimal import to prove installation.

### Check 2 - review the implementation against the architecture claims

1. Read `solution/main.py` and `solution/agent.py` before provisioning.
1. Confirm whether the implementation actually uses the documented Microsoft 365 Agents SDK `CloudAdapter` and `AgentApplication`.
1. Confirm whether `POST /api/messages` validates the Bot Framework `Authorization` JWT before processing an Activity.
1. Confirm whether `BOT_APP_CLIENT_ID`, `BOT_APP_CLIENT_SECRET`, and `BOT_TENANT_ID` are read by the running proxy.
1. Confirm whether the proxy logs incoming Activities and responses as required by Step 8.

   **Check:** Do not treat package references as proof that the SDK is used. If the solution is a plain FastAPI JSON handler, record the architecture, authentication, and logging claims as failed documentation or implementation checks. Continue only after telling the user that the public endpoint may accept unauthenticated requests and receiving confirmation to test it.

### Check 3 - confirm the workshop Foundry agent

1. Confirm `.env` exists without printing its contents.
1. Check only whether `FOUNDRY_PROJECT_ENDPOINT` and `AGENT_NAME` are present and non-empty. Do not display their values unless needed to diagnose a mismatch.
1. Confirm `AGENT_NAME` is unset (defaults to `acl-remedy-advisor`) or equals `acl-remedy-advisor`.
1. Sign in as `${input:foundryUserUpn}` when prompted, then run a minimal Foundry request or use the Foundry portal to confirm `acl-remedy-advisor` exists and responds.

   **Check:** If `${input:foundryUserUpn}` cannot run the agent, stop. Module 13 cannot validate grounding without the existing agent.

### Check 4 - confirm attendee-owned Azure permissions and identity switching

1. Ask the user to sign in with Azure CLI as `${input:botTenantUserUpn}`. The user must perform the sign-in.
1. Select `${input:botSubscriptionId}` and show this non-secret summary:

   ```powershell
   az account set --subscription "${input:botSubscriptionId}"
   az account show --query "{subscription:id,tenant:tenantId,user:user.name}" -o table
   ```

1. Confirm the subscription ID and user match the inputs.
1. Confirm this identity can create app registrations and deploy resources, without creating anything yet.
1. Determine how the running proxy will authenticate to the workshop Foundry project after provisioning in the attendee-owned tenant. If the same Azure CLI session cannot access both, document the required `az login --tenant ...` switch or other credential strategy before proceeding.

   **Check:** Treat an unexplained dual-tenant credential conflict as blocking. The provisioning identity must not be silently mistaken for the Foundry-calling identity.

### Check 5 - confirm Teams tenant policy and browser sessions

1. Use `open_browser_page` to open Microsoft Teams in the tenant for `${input:botTenantUserUpn}`.
1. Ask the user to complete sign-in if prompted.
1. Confirm **Apps → Manage your apps → Upload a custom app** is available.
1. Open `https://portal.azure.com` and confirm the same attendee-owned tenant and subscription are selected.
1. Open `https://ai.azure.com` in a separate browser context or tab and confirm `${input:foundryUserUpn}` can access the workshop project.

   **Check:** If custom app upload is disabled by policy, mark Parts 4 and 5 blocked. Continue with source, provisioning, proxy, tunnel, and direct HTTP validation only if the user approves the partial test.

### Check 6 - choose and verify development-tunnel tooling

1. Detect an installed development-tunnel tool that can expose local port 3978 over public HTTPS. Prefer the tool documented for the attendee's environment.
1. Record the exact command and whether authentication is required.
1. Do not assume `atk` creates the tunnel; the README describes `atk` only as optional scaffolding and sideload tooling.

   **Check:** If no supported tunnel tool is installed, stop before provisioning. Ask the user to install or select one, because `BOT_MESSAGING_ENDPOINT` is required by the current provisioning script.

### Check 7 - confirm manifest assets and packaging readiness

1. Inspect `appPackage/manifest.json` and list every referenced file asset.
1. Confirm the package contains the required color and outline icons expected by the Teams manifest schema.
1. Confirm the manifest ID and `bots[0].botId` are placeholders before modification.
1. Validate the manifest against its declared schema when a validator is available.

   **Check:** If icons or required manifest properties are missing, record packaging as blocked unless Teams validation proves the package is accepted. Do not invent assets during a literal test.

## Part 1 - confirm access and prepare the code

### Step 1 - follow the prerequisite instructions literally

1. Execute the checks in README Step 1 using the identities and subscription established in pre-flight.
1. Confirm the README clearly distinguishes the attendee-owned Azure identity from the workshop Foundry identity.
1. Record whether `atk` is installed, but do not fail the module if it is absent because manual upload is the supported path.

### Step 2 - review the starter and solution

1. Open all three starter files and their matching solution files.
1. Map every starter TODO to an explicit README instruction or solution implementation.
1. Confirm the README provides enough code or guidance to complete the starter without copying the entire solution blindly.
1. Confirm `uv sync --group module-13` completed successfully.

## Part 2 - provision the identity and Azure Bot Service

### Step 3 - test the documented provisioning order

1. Set `BOT_SERVICE_NAME`, `BOT_RESOURCE_GROUP`, and `BOT_LOCATION` to the README defaults unless the user supplied alternatives.
1. Before creating resources, confirm consent using the exact values and the tenant discovered in Check 4.
1. Follow the README literally by leaving `BOT_MESSAGING_ENDPOINT` unset and running the provisioning script.
1. Capture the result without exposing a secret.

   **Check:** The current script is expected to reject an unset endpoint with `BOT_MESSAGING_ENDPOINT must be an HTTPS URL ending in /api/messages.` If reproduced, mark the literal instruction failed and add a clarification recommendation. Do not repeatedly run the script, because every successful run creates another app registration and secret.

1. Recover by completing Step 4 and Step 5 far enough to obtain a stable public HTTPS tunnel URL.
1. Set `BOT_MESSAGING_ENDPOINT` to `<public-tunnel-url>/api/messages` and run the provisioning script exactly once.
1. Ask the user to copy the printed `BOT_APP_CLIENT_ID`, `BOT_APP_CLIENT_SECRET`, `BOT_TENANT_ID`, `BOT_SERVICE_NAME`, and `BOT_RESOURCE_GROUP` values into `.env`. Never request or inspect the secret.
1. Verify the created app registration and Azure Bot Service using IDs and portal metadata that do not reveal the secret.

   **Capture:** the Azure Bot Service Configuration page showing the messaging endpoint, Microsoft App ID, app type, and tenant ID, with no secrets visible.

   **Capture:** the Bot Service Channels page showing Microsoft Teams enabled.

## Part 3 - run the proxy and expose it

### Step 4 - start and inspect the local proxy

1. Start the solution proxy as a long-running process:

   ```powershell
   uv run python labs/introduction-foundry-agent-service/13-custom-engine-agent/solution/start_server.py
   ```

1. Confirm port 3978 is listening.
1. Confirm OpenAPI reports `POST /api/messages` without sending a Bot Framework request yet.
1. Confirm startup output does not reveal `BOT_APP_CLIENT_SECRET`.
1. Keep the process running for subsequent tests.

   **Check:** If startup succeeds without reading any bot app credentials, correlate that result with the source review in Check 2 rather than claiming Bot Framework authentication works.

### Step 5 - create and verify the development tunnel

1. Start the selected tunnel as a long-running process forwarding public HTTPS traffic to port 3978.
1. Confirm the public URL is stable for the duration of the test.
1. Verify the public endpoint reaches the local app without sending secrets.
1. Confirm `BOT_MESSAGING_ENDPOINT` ends in `/api/messages` and matches the Bot Service configuration.
1. If the tunnel URL changed after provisioning, update the Bot Service by rerunning only the safe update path. Do not create another app registration merely to change the endpoint. If the script has no update-only behavior, update the endpoint in the Azure portal or with a targeted Azure CLI command and record the missing idempotent update path.

   **Capture:** the development-tunnel view showing the public HTTPS forwarding URL and local port 3978, with account details hidden.

### Step 5A - test the unauthenticated endpoint boundary

Only perform this check if Check 2 found that the solution does not validate Bot Framework authentication and the user approved continuing.

1. Send a minimal Activity-shaped JSON request to the public `/api/messages` endpoint without an `Authorization` header.
1. Use a benign message and no personal information.
1. Record whether the endpoint accepts it and calls Foundry.

   **Check:** An authenticated Bot Framework endpoint should reject an unauthenticated request. If it returns a successful agent response, report a high-severity security and correctness defect. Do not publish the tunnel URL in the final report.

## Part 4 - package and sideload the Teams app

### Step 6 - update and package the manifest

1. Replace both placeholder values with the app ID printed by the provisioning script:

   - Top-level `id`.
   - `bots[0].botId`.

1. Review the bot scopes and display metadata.
1. Confirm every referenced icon exists and has the required dimensions and format.
1. Create a ZIP whose root contains `manifest.json` and the referenced icons. Do not include the parent `appPackage` folder, `.env`, source code, or any secret.
1. List the ZIP entries and inspect them before upload.

   **Check:** If the package cannot be made from the repository contents exactly as documented, mark the step blocked and add a concrete documentation or asset recommendation.

### Step 7 - upload the custom app

1. In Teams, open **Apps → Manage your apps → Upload a custom app**.
1. Upload the ZIP.
1. Record any manifest validation errors exactly.
1. Open the resulting **ACL Remedy Advisor** app if upload succeeds.

   **Capture:** the Teams custom-app upload control immediately before selecting the ZIP.

   **Capture:** the ACL Remedy Advisor app details or conversation view after successful upload.

## Part 5 - verify the end-to-end conversation

### Step 8 - send the documented message

1. Ensure the local proxy and tunnel are running.
1. Ensure the active Azure CLI credential used by `DefaultAzureCredential` can call the workshop Foundry project as `${input:foundryUserUpn}`.
1. Send the README's exact refrigerator message in Teams.
1. Confirm the local proxy receives the Activity.
1. Confirm Teams displays a response from `acl-remedy-advisor`.
1. Confirm the response addresses the $1,200 refrigerator, 14-month failure, and Australian Consumer Law remedy rather than giving a generic answer.

   **Capture:** the Teams conversation showing the complete test message and grounded response. Review the screenshot for personal or tenant-sensitive information before keeping it.

1. Stop the proxy and send a second benign message.
1. Confirm the failure is visible in Teams, the Bot Service, tunnel logs, or another attendee-observable location. Record the exact behavior and timeout.
1. Restart the proxy and confirm a new message succeeds.

   **Capture:** the attendee-visible failure state while the proxy is stopped, provided it contains no sensitive information.

## Validation - confirm every criterion with evidence

1. Verify the Entra app registration and Bot Service exist in the attendee-owned tenant and resource group.
1. Verify the proxy starts without exposing a secret.
1. Determine whether `POST /api/messages` accepts only authenticated Bot Framework requests. Do not mark this passed solely because Teams can reach it.
1. Verify the Teams app package uploads and opens.
1. Verify the Teams message reaches the local proxy and the response returns to Teams.
1. Verify the answer is grounded by the existing `acl-remedy-advisor` agent.
1. Explain the observed difference between this proxy and Module 12's Foundry-managed publishing bridge.
1. Reconcile every architecture claim in the README with the implementation and runtime evidence.

## Step 9 - report results

Report every pre-flight check and numbered step as **passed**, **failed**, or **skipped/blocked**. For each failure or block, include:

- The exact check or step.
- What the README says.
- The observed behavior.
- The expected behavior.
- The exact non-secret error message or portal state.
- The relevant screenshot filename.
- Whether the issue is in documentation, implementation, environment policy, permissions, or an external preview service.

Then provide these summaries:

1. **End-to-end verdict** - state the furthest verified boundary: source only, local HTTP, public tunnel, Bot Service, Teams delivery, or grounded Foundry response.
1. **Screenshots captured** - list every saved filename with a one-line caption.
1. **Clarification recommendations** - list every ambiguity or mismatch with exact replacement wording or asset guidance.
1. **Security findings** - report authentication, secret-handling, public-endpoint, and package-content findings without exposing sensitive values.
1. **Created resources** - list the tenant ID, subscription ID, resource group, Bot Service name, app registration display name and app ID, and local ZIP path. Never list the secret.
1. **Cleanup commands** - provide commands to delete the attendee-owned resource group, app registration, local ZIP, and sideloaded Teams app. Do not execute them without explicit approval.

If every non-skipped criterion passes, confirm that Module 13 end-to-end validation is complete. Do not claim the documented Microsoft 365 Agents SDK authentication path passed unless the runtime actually validates Bot Framework requests through the SDK.
