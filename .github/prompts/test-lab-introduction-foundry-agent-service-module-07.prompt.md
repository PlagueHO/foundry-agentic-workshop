---
description: "Test lab module 07 (Ground the agent with Foundry IQ knowledge bases) end-to-end by operating inside the already-open Microsoft Foundry portal (ai.azure.com) browser session, using an open GitHub Codespace for verification commands. Both the Foundry portal and the Codespace must already be open and authenticated to Azure with the Foundry project set as default, and Module 06 must have been completed (the acl-remedy-advisor agent must exist at v3 with three tools) before this prompt is run."
---

## Inputs

- ${input:attendeeUpn}: (Required) The UPN of the attendee to test with (e.g. `lab.attendee.1@MngEnvMCAP199525.onmicrosoft.com`).
- ${input:envName}: (Required) The azd environment name the lab was provisioned into (e.g. `foundry-hol2`).

---

You must test the steps in the #file:labs/introduction-foundry-agent-service/07-foundry-iq/README.md by operating inside the open Microsoft Foundry portal browser session at `https://ai.azure.com`, using an open GitHub Codespace browser session for verification commands and script fallbacks. The attendee is `${input:attendeeUpn}` in the environment `${input:envName}`.

> **Important:** Any Azure or GitHub login dialogs that appear during the test must be completed by the user. Pause and prompt the user whenever a sign-in dialog is encountered. Do not attempt to enter credentials automatically.

## Pre-flight — Verify the environment is ready

Before executing any lab steps, confirm all prerequisites are satisfied. **Do not proceed if any check fails** — report the failure and ask the user to resolve it.

### Check 1 — Confirm the Foundry portal is open and authenticated

1. Use `open_browser_page` to list currently available pages and confirm a page is open at `https://ai.azure.com`.
1. If no such page is available, use `open_browser_page` to navigate to `https://ai.azure.com`.
1. Take a screenshot and confirm a project page or the portal home page is visible.
1. Confirm the signed-in account displayed in the top-right corner matches `${input:attendeeUpn}`. If a login dialog or account-picker is shown, pause and instruct the user to sign in with `${input:attendeeUpn}` before continuing. Do not enter credentials automatically.
1. Navigate to the attendee's Foundry project (use **All projects** to find the project assigned to `${input:attendeeUpn}` if needed) and note the project name.

### Check 2 — Confirm the Codespace browser page is open and shared

1. Use `open_browser_page` to confirm a page is open with a URL matching `*.github.dev/*` or `github.dev/*`, indicating a GitHub Codespace connected to VS Code in the browser.
1. If no such page is available, pause and instruct the user to:
   - Navigate to `https://github.com/PlagueHO/foundry-agentic-workshop`.
   - Click **Code → Codespaces** and open or create a codespace on the current branch.
   - Wait for the devcontainer to finish building, then share the resulting browser tab with this session.
1. Take a screenshot of the Codespace page to confirm it is showing VS Code with the `foundry-agentic-workshop` repository open.

### Check 3 — Confirm Azure authentication in the Codespace

1. Switch to the Codespace browser page and open a terminal (if one is not already open).
1. Run:

   ```bash
   az account show --query '{user:user.name, subscription:id}' -o table
   ```

1. Confirm the output shows `${input:attendeeUpn}` as the signed-in user and that the subscription ID matches `AZURE_SUBSCRIPTION_ID` from the environment.
1. If the command fails or shows a different identity, pause and ask the user to run `az login` in the Codespace terminal and complete the browser sign-in before continuing.

### Check 4 — Confirm the `.env` file exists and contains required values

1. In the Codespace terminal, run:

   ```bash
   cat .env | grep -E 'FOUNDRY_PROJECT_ENDPOINT|AGENT_NAME|RETAIL_REMEDY_OPS_MCP_SERVER_URL|KNOWLEDGE_BASE_NAME|AZURE_SEARCH_PRODUCT_INDEX_NAME|AZURE_SEARCH_DOCUMENT_INDEX_NAME'
   ```

1. Confirm `FOUNDRY_PROJECT_ENDPOINT` is populated with a non-empty value.
1. Confirm `AGENT_NAME` is set to `acl-remedy-advisor`.
1. Confirm `RETAIL_REMEDY_OPS_MCP_SERVER_URL` is populated and ends in `/mcp` (either the shared Azure Container Apps URL the organizer deployed, or a Public Codespace tunnel URL).
1. Confirm `KNOWLEDGE_BASE_NAME` is populated with the per-attendee knowledge base name (for example `acl-remedy-knowledge-lab-attendee-1`).
1. Note the values of `AZURE_SEARCH_PRODUCT_INDEX_NAME` (default `retail-products`) and `AZURE_SEARCH_DOCUMENT_INDEX_NAME` (default `retail-policies`); these are the indexes you select as knowledge sources.

   **Check:** If `.env` does not exist, confirm with the user that Module 01 has been completed, then copy `shared/.env.example` to `.env` and populate `FOUNDRY_PROJECT_ENDPOINT`, `RETAIL_REMEDY_OPS_MCP_SERVER_URL`, and `KNOWLEDGE_BASE_NAME` from the attendee onboarding file at `.azure/${input:envName}/<upn_local>.md` (where `<upn_local>` is the part of `${input:attendeeUpn}` before `@`), or from `azd env get-values`.

### Check 5 — Confirm the attendee can create knowledge bases

Creating a Foundry IQ knowledge base requires the **`foundry-project-manager`** role or higher. The `foundry-user` role cannot create knowledge bases.

1. In the Foundry portal, confirm the attendee can reach **Build → Knowledge** in the project's left navigation.
1. If the **Create a knowledge base** action is disabled or returns an access error in Part 1, pause and ask the organizer to elevate `${input:attendeeUpn}` to `foundry-project-manager` (the recommended default is `AZURE_ATTENDEE_DEFAULT_ROLE=foundry-project-manager`). After elevation, have the user sign out of the portal and sign back in to refresh the token.

### Check 6 — Confirm the `acl-remedy-advisor` agent exists at the end state of Module 06

This module requires the `acl-remedy-advisor` agent to already exist with three direct tools — **Web search**, **Code Interpreter**, and the **`retail-remedy-ops` MCP** server — saved as **v3** during Module 06.

1. In the Foundry portal, navigate to the attendee's project and click **Agents** (under **Build**) in the left navigation.
1. Confirm `acl-remedy-advisor` is listed and open it.
1. Confirm the agent is at **v3** (or higher) and that its **Tools** section lists **Code interpreter**, **Web search**, and the `retail-remedy-ops` MCP server.
1. Confirm the instructions include both the Code Interpreter paragraph (from Module 05) and the MCP tool-routing paragraph (from Module 06).
1. Take a screenshot of the agent showing **v3** with all three tools visible.

   **Check:** If the agent does not exist or is not at v3 with three tools, run the Module 06 solution script from the Codespace terminal to restore the v3 three-tool agent before continuing:

   ```bash
   python labs/introduction-foundry-agent-service/06-mcp-tools/solution/create_agent_with_mcp.py
   ```

   Confirm `RETAIL_REMEDY_OPS_MCP_SERVER_URL` is set in `.env` first. Then re-verify the agent state before proceeding.

### Check 7 — Confirm the search indexes exist and are populated

Module 07 grounds the agent on two pre-seeded Azure AI Search indexes connected to the project.

1. In the Codespace terminal, confirm both indexes contain documents (substitute the index names from Check 4 if they differ from the defaults):

   ```bash
   python scripts/health-check.py
   ```

1. Confirm the health check reports the Azure AI Search service is reachable and that both the `retail-products` and `retail-policies` indexes exist with a non-zero document count.

   **Check:** If either index is missing or empty, seed it from the repository root, then re-run the health check:

   ```bash
   python scripts/seed-product-index.py
   python scripts/seed-document-index.py
   ```

   **Check:** The workshop indexes live in the connected Azure AI Search service, not in Foundry, so they do **not** appear on the Foundry **Indexes** tab — this is expected. They are still selectable by name in the **Select search index** dropdown in Part 1.

### Check 8 — Confirm the MCP server is reachable

The agent routes operational lookups to the `retail-remedy-ops` MCP server (from Module 06). Confirm it is reachable before testing in Part 6.

1. In the Codespace terminal, confirm the configured endpoint responds:

   ```bash
   curl -s -o /dev/null -w "%{http_code}" "$(grep '^RETAIL_REMEDY_OPS_MCP_SERVER_URL=' .env | cut -d= -f2-)"
   ```

1. Confirm the HTTP status code is `200`, `405`, or `406` (a non-connection response confirms the endpoint is reachable).
1. Take a screenshot of the terminal showing the status code.

   **Check:** If the command times out or returns a connection error, the MCP server is unavailable. If the shared Azure Container Apps server is down, ask the user to confirm its status with the organizer. Alternatively, the user can run their own server locally and expose it on a **Public** port 8080 tunnel (see Module 06, Part 2):

   ```bash
   python shared/mcp-servers/retail-remedy-ops/src/server.py
   ```

   Then set `RETAIL_REMEDY_OPS_MCP_SERVER_URL` in `.env` to the tunnel URL ending in `/mcp` and re-run the `curl` check.

---

## Part 1 — Create the knowledge base and add the first source

### Step 1 — Open the Knowledge page

1. In the Foundry portal, navigate to the attendee's project.
1. In the left navigation under **Build**, click **Knowledge**.
1. Confirm the page heading reads **Knowledge (Foundry IQ)** and the **Knowledge bases** tab is selected.
1. Take a screenshot of the Knowledge (Foundry IQ) page.

   **Check:** If **Knowledge** is not visible in the left navigation, confirm you are inside a project (not at the account or **All projects** level). If the **Create a knowledge base** button is disabled, revisit Check 5 (role elevation).

### Step 2 — Choose the knowledge type

1. Click **Create a knowledge base**. Confirm the **Choose a knowledge type** dialog opens, listing source types (Azure AI Search Index, Azure Blob Storage, Web, SharePoint, OneLake, Fabric IQ, Azure SQL, Work IQ, File, MCP Server).
1. Select the **Azure AI Search Index** tile ("Enterprise scale search for app development").
1. Click **Connect**.
1. Confirm the **Create a new knowledge base** page opens (with **Save knowledge base** and **Cancel** in the top-right) and immediately shows the **Create a knowledge source** dialog.
1. Take a screenshot of the Choose a knowledge type dialog (before clicking Connect) and of the Create a new knowledge base page.

   **Check:** If the **Create a knowledge source** dialog does not appear automatically, look for an **Add sources** dropdown on the Create a new knowledge base page and choose **Azure AI Search Index** from it.

### Step 3 — Create the retail-products knowledge source

1. In the **Create a knowledge source** dialog, set the fields:
   - **Name**: replace the default (for example `ks-searchindex-69`) with:

     ```text
     retail-products
     ```

   - **Description** (optional):

     ```text
     Retail product catalog: specifications, compatibility, and feature details for store products.
     ```

   - **Select search index**: choose **retail-products** from the dropdown (use the value of `AZURE_SEARCH_PRODUCT_INDEX_NAME` if it differs from the default).
1. Confirm there is **no field mapping step** — Foundry IQ reads the index's semantic configuration automatically. Confirm the dialog notes *"Search index must contain semantic configuration"*.
1. Take a screenshot of the Create a knowledge source dialog with `retail-products` configured.
1. Click **Create**. Confirm the source appears in the knowledge base's **Knowledge sources** list with type **Azure AI Search Index**.
1. Take a screenshot of the Create a new knowledge base page showing the `retail-products` source listed.

   **Check:** If `retail-products` is not selectable in the **Select search index** dropdown, return to Check 7 and confirm the index exists and is populated. The index lives in the connected Azure AI Search service, so it will not appear on the Foundry **Indexes** tab.

   **Check:** If the dialog reports *"Search index must contain semantic configuration"*, the index was created without one. Re-run `python scripts/seed-product-index.py` from the repository root to recreate it with its semantic configuration, then reopen the dialog.

---

## Part 2 — Add the retail-policies knowledge source

### Step 4 — Add the second source

1. On the **Create a new knowledge base** page, open the **Add sources** dropdown and choose **Azure AI Search Index** again.
1. In the **Create a knowledge source** dialog, set the fields:
   - **Name**:

     ```text
     retail-policies
     ```

   - **Description** (optional):

     ```text
     Store policies: returns, refunds, warranties, loyalty program, and store-brand guarantees.
     ```

   - **Select search index**: choose **retail-policies** (use the value of `AZURE_SEARCH_DOCUMENT_INDEX_NAME` if it differs from the default).
1. Click **Create**. Confirm both `retail-products` and `retail-policies` now appear in the **Knowledge sources** list.
1. Take a screenshot of the Knowledge sources list showing both sources.

   **Check:** If `retail-policies` is not selectable, return to Check 7 and confirm the index exists. Re-run `python scripts/seed-document-index.py` if it is missing or empty.

---

## Part 3 — Name and save the knowledge base

### Step 5 — Complete the basic configuration

1. In the **Basic configuration** section, set:
   - **Name**: use the per-attendee knowledge base name from `KNOWLEDGE_BASE_NAME` (for example, `acl-remedy-knowledge-lab-attendee-1`).
   - **Description** (optional):

     ```text
     Retail product catalog and store policy knowledge for the ACL Remedy Advisor agent.
     ```

   - **Chat completions model**: leave as **Select model** (not required for extractive retrieval).
   - **Retrieval reasoning effort**: **Minimal**.
   - **Output mode**: **Extractive data**.
   - **Retrieval instructions** (optional): leave empty.
1. Confirm the **Knowledge sources** table lists both `retail-products` and `retail-policies` as type **Azure AI Search Index** with status **Active**.
1. Take a screenshot of the basic configuration showing the per-attendee name, **Minimal** retrieval reasoning effort, **Extractive data** output mode, and both sources **Active**.

   **Check:** If either source shows a status other than **Active**, wait a few seconds and refresh. If a source remains inactive, remove and re-add it via the **Add sources** dropdown.

### Step 6 — Save the knowledge base

1. Click **Save knowledge base** in the top-right.
1. Wait for creation to complete. Confirm the knowledge base detail page opens (its heading is the knowledge base name) with **Save** and **Use in an agent** buttons in the top-right.
1. Take a screenshot of the knowledge base detail page.

   **Check:** If the save fails with an access error, revisit Check 5 — knowledge base creation requires the `foundry-project-manager` role. After elevation, sign out and back in, then retry from Step 1 (the partially configured knowledge base may need to be recreated).

---

## Part 4 — Attach the knowledge base to the agent

### Step 7 — Use the knowledge base in an agent

1. On the knowledge base detail page, click **Use in an agent** in the top-right.
1. In the **Recent agents** dropdown, select **acl-remedy-advisor** (use **View all agents** if it is not listed).
1. Take a screenshot of the Use in an agent dropdown showing `acl-remedy-advisor` selectable.

   **Check:** If `acl-remedy-advisor` is not listed under Recent agents or View all agents, confirm the agent exists in the same project (revisit Check 6).

### Step 8 — Confirm the Knowledge section

1. Confirm you land on the **acl-remedy-advisor** agent's **Build** page.
1. Scroll the configuration panel and confirm a **Knowledge** section now lists your knowledge base, separate from the **Tools** section (which still shows **Code interpreter**, **Web search**, and the `retail-remedy-ops` MCP server).
1. Confirm attaching the knowledge base auto-saved the agent as a new version (for example, **Version 4** / **v4**).
1. Take a screenshot of the agent Build page showing the **Knowledge** section alongside the existing **Tools** section.

   **Check:** If the **Knowledge** section does not appear, reload the agent Build page. If the knowledge base still is not attached, return to the knowledge base detail page and repeat Step 7.

---

## Part 5 — Update the agent instructions

### Step 9 — Add tool-routing and grounding instructions

1. In the **Instructions** field, confirm the existing instructions from Modules 04–06 are present and intact (base ACL advisor text, the Code Interpreter paragraph, and the MCP tool-routing paragraph).
1. Position the cursor at the end of the existing instructions and press **Enter** twice to create a blank line.
1. Add the following paragraphs exactly:

   ```text
   When a staff member provides a receipt ID, order ID, or customer ID — or asks
   you to look up a purchase, verify an order, or open a support case — use the
   retail-remedy-ops tools to perform that operational lookup or action. Never
   invent receipt, order, or case details; always retrieve them with the tools.

   When answering questions about specific products available in the store —
   including product names, descriptions, categories, prices, ratings, or stock
   availability — use the knowledge base to retrieve accurate product information
   and cite the source in your response.

   When answering questions about store policies — including return windows,
   refund eligibility, warranty coverage, loyalty program rules, or store-brand
   guarantees — use the knowledge base to retrieve the relevant policy and quote
   it directly.

   Prefer knowledge base retrieval over your training knowledge for all product
   and policy questions. The knowledge base reflects the store's current catalog
   and policies, not general retail conventions.

   To summarise tool routing: use the retail-remedy-ops tools for operational
   lookups and actions, the knowledge base for product and policy questions, web
   search for current ACCC and Australian Consumer Law guidance, and code
   interpreter for refund, depreciation, pro-rata, or price calculations.
   ```

1. Take a screenshot of the Instructions field showing the new paragraphs at the bottom.

   **Check:** Confirm the original Modules 04–06 instructions remain intact above the new paragraphs. If any text was accidentally replaced, undo and retry.

### Step 10 — Save the agent

1. Click **Save** in the top-right.
1. Wait for the save to complete and confirm the agent advances to a new version (for example, **Version 5** / **v5**).
1. Take a screenshot confirming the new version.

   **Check:** If the save fails, retry the **Save** action. If it continues to fail, confirm the project is still selected and the portal session is still authenticated as `${input:attendeeUpn}`.

---

## Part 6 — Test grounded retrieval

> **Important:** Confirm the MCP server is still reachable before testing (Check 8). The agent routes operational lookups (Step 12) to the `retail-remedy-ops` server.

### Step 11 — Run a combined policy query

1. Open the **Playground** (Chat) panel for the agent (ensure it targets the latest version saved in Step 10).
1. Send the following message:

   ```text
   According to our store's return policy, how many days do customers have to return non-perishable items with a receipt, and within what timeframe should spoiled perishable items be reported?
   ```

1. Wait for the full response and take a screenshot.
1. Confirm the agent:
   - Answers **14 days** for non-perishable returns with a receipt and **48 hours** for reporting spoiled perishable items.
   - Includes numbered citations (for example `[1]` `[2]`) that link to `mcp://searchindex/...` sources.
   - Shows the knowledge base tool chip (for example `kb-...`) in the response trace.
1. Confirm the agent did **not** invoke the `retail-remedy-ops` MCP tools for this query — it has no receipt or customer ID, so it should ground from the knowledge base only.

   **Check:** If the response is not cited and uses generic retail conventions instead of the workshop data, re-read the instructions from Step 9. The phrase *"Prefer knowledge base retrieval over your training knowledge"* is required — without it the model may default to training knowledge. Confirm the **Knowledge** section still lists the knowledge base (Step 8).

   **Check:** If the response returns an access error (HTTP 403) when retrieving from the knowledge base, the project's managed identity may be missing the **Search Index Data Reader** role on the Azure AI Search service. The workshop infrastructure assigns this automatically; data-plane assignments can take several minutes to propagate. Wait and retry, or ask the organizer to re-run `azd provision` to reconcile role assignments.

### Step 12 — (Optional) Exercise the other tools

1. **Product lookup (knowledge base):** send *"Recommend a healthy breakfast cereal with nuts, and include its price and rating."* — confirm a specific product from `retail-products` with a citation.
1. **Operational lookup (retail-remedy-ops):** provide a receipt ID from Module 06 and ask the agent to look it up — confirm an MCP tool call appears in the trace.
1. **Consumer law guidance (web search):** send *"What does the ACCC say about repair versus replacement for a major failure?"* — confirm a web-search-grounded answer citing accc.gov.au.
1. **Calculation (Code Interpreter):** send *"A customer paid $480 for an appliance 18 months into a 36-month expected life. Calculate a pro-rata refund."* — confirm a worked calculation.
1. Take a screenshot of any tool-exercising response and its trace.

   **Check:** If operational lookups do not call the MCP server, re-run the `curl` reachability check from Check 8 and confirm `RETAIL_REMEDY_OPS_MCP_SERVER_URL` still points at a reachable endpoint. Adding the knowledge base must not displace the existing tools.

---

## Part 7 (optional) — Recreate the end state from code

If the portal walkthrough cannot be completed (for example in a Codespace with network restrictions, or to reset an attendee project to a known-good state), the Module 07 solution script reproduces the same end state: two knowledge sources, the knowledge base, the project connection, and a new agent version that attaches the knowledge base as an MCP tool with tool-routing instructions.

### Step 13 — Run the solution script

1. In the Codespace terminal, confirm `FOUNDRY_PROJECT_ENDPOINT`, `AZURE_SEARCH_SERVICE_NAME`, `KNOWLEDGE_BASE_NAME`, and `RETAIL_REMEDY_OPS_MCP_SERVER_URL` are set in `.env`.
1. Run the script from the repository root:

   ```bash
   python labs/introduction-foundry-agent-service/07-foundry-iq/solution/create_knowledge_base_agent.py
   ```

1. Confirm the script completes without error and reports the knowledge base, the knowledge sources, the project connection, and a new agent version.
1. Reload the agent in the Foundry portal and confirm the **Knowledge** section lists the knowledge base and the agent advanced to a new version.
1. Take a screenshot of the terminal output and the reloaded agent.

   **Check:** If the script raises a `KeyError`, confirm the required environment variables above are present and non-empty. If it raises an authentication error, run `az login` in the terminal. If knowledge source or knowledge base creation fails with an authorization error, confirm the account has **Search Service Contributor** on the search service and **Foundry Project Manager** on the project.

---

## Validation — confirm all criteria

Work through each item in the lab's Validation section and confirm:

1. **Knowledge base created**: The knowledge base (the `KNOWLEDGE_BASE_NAME` value) is listed on the **Knowledge bases** tab.
1. **Two knowledge sources**: The knowledge base shows both `retail-products` and `retail-policies` as **Azure AI Search Index** sources with status **Active**.
1. **Attached to agent**: The knowledge base appears in the `acl-remedy-advisor` agent's **Knowledge** section, and the agent advanced to a new version after attaching it.
1. **Instructions updated and saved**: The tool-routing and grounding paragraphs from Step 9 are present, and the agent advanced to a further new version (for example, **Version 5** / **v5**).
1. **Grounded policy answers**: Policy queries return answers with numbered citations to `mcp://searchindex/...` sources rather than generic retail conventions, including **14 days** for non-perishable returns and **48 hours** for spoiled perishable reporting.
1. **Grounded product answers**: Product queries return specific product names, prices, and ratings that match the `retail-products` index.
1. **Tool routing intact**: Operational queries (with a receipt ID) still call the `retail-remedy-ops` MCP server, web search still answers consumer-law questions, and Code Interpreter still performs calculations. Adding the knowledge base did not displace the existing tools.

---

## Step 14 — Report results

Report the outcome of every check and step above. For each one state whether it **passed** or **failed**. For any failure, include:

- The exact check or step number and description.
- The observed behaviour.
- The expected behaviour.
- Any error messages, unexpected output, or unexpected UI state encountered.
- The screenshot filename or description if a screenshot was taken.

If all steps pass, confirm that lab module 07 end-to-end validation is complete.
