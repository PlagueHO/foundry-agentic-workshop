---
description: "Test lab module 04 (Create and chat with a Prompt Agent) end-to-end by operating inside an already-open GitHub Codespace for this repository in VS Code Insiders, verifying every step carefully via the browser. The Codespace must already be open and authenticated to Azure with the Foundry project set as default before this prompt is run."
---

## Inputs

- ${input:attendeeUpn}: (Required) The UPN of the attendee to test with (e.g. `lab.attendee.1@MngEnvMCAP199525.onmicrosoft.com`).
- ${input:envName}: (Required) The azd environment name the lab was provisioned into (e.g. `foundry-hol2`).

---

You must test the steps in the #file:labs/introduction-foundry-agent-service/04-prompt-based-agents/README.md by operating inside an open GitHub Codespace browser session. The attendee is `${input:attendeeUpn}` in the environment `${input:envName}`.

> **Important:** Any Azure or GitHub login dialogs that appear during the test must be completed by the user. Pause and prompt the user whenever a sign-in dialog is encountered. Do not attempt to enter credentials automatically.

## Pre-flight - Verify the Codespace is ready

Before executing any lab steps, confirm all prerequisites are satisfied. **Do not proceed if any check fails** - report the failure and ask the user to resolve it.

### Check 1 - Confirm the Codespace browser page is open and shared

1. Use `open_browser_page` to check which pages are currently available.
1. Confirm a page is open with a URL matching `*.github.dev/*` or `github.dev/*`, indicating a GitHub Codespace connected to VS Code Insiders in the browser.
1. If no such page is available, pause and instruct the user to:
   - Navigate to `https://github.com/PlagueHO/foundry-agentic-workshop`.
   - Click **Code → Codespaces** and open or create a codespace on the current branch.
   - Wait for the devcontainer to finish building, then share the resulting browser tab with this session.
1. Take a screenshot of the Codespace page to confirm it is showing VS Code Insiders with the `foundry-agentic-workshop` repository open.

### Check 2 - Confirm Azure authentication

1. In the Codespace terminal, run:

   ```bash
   az account show --query '{user:user.name, subscription:id}' -o table
   ```

1. Confirm the output shows `${input:attendeeUpn}` as the signed-in user and that the subscription ID matches `AZURE_SUBSCRIPTION_ID` from the environment.
1. If the command fails or shows a different identity, pause and ask the user to run `az login` in the codespace terminal and complete the browser sign-in before continuing.

### Check 3 - Confirm the Foundry project is set as default in the Foundry Toolkit

1. Click the **Foundry Toolkit** icon in the Activity Bar (the blue Foundry spark logo).
1. In **My Resources**, confirm the project name assigned to `${input:attendeeUpn}` is shown and expanded, with sub-sections including **Models**, **Prompt Agents**, **Hosted Agents (Preview)**, **Tools**, **Knowledge**, and **Evaluations** visible.
1. If the project is not set, follow the Set Default Project flow from module 03 before continuing.

### Check 4 - Confirm the `.env` file exists and contains required values

1. In the Codespace terminal, run:

   ```bash
   cat .env | grep -E 'FOUNDRY_PROJECT_ENDPOINT|AGENT_NAME'
   ```

1. Confirm `FOUNDRY_PROJECT_ENDPOINT` is populated with a non-empty value.
1. If `AGENT_NAME` is already set, note its current value. It will be set to `acl-remedy-advisor` during step 5 of the lab.
1. If `.env` does not exist, confirm with the user that module 01 has been completed, then copy `shared/.env.example` to `.env` and populate `FOUNDRY_PROJECT_ENDPOINT` from the attendee onboarding file at `.azure/${input:envName}/<upn_local>.md` (where `<upn_local>` is the part of `${input:attendeeUpn}` before `@`).

---

## Part 1 - Create the Prompt Agent in Agent Builder

### Step 1 - Open Agent Builder

1. Click the **Foundry Toolkit** icon in the Activity Bar.
1. In the **Developer Tools** section, click **Create Agent**.
1. Confirm the Create Agent screen appears.
1. Click **Open Agent Builder** under *Design an agent without code*.
1. Confirm the Agent Builder panel opens in the editor area.

   **Check:** If **Create Agent** is not visible, the Foundry Toolkit may not have loaded correctly. Reload the VS Code window (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> → **Developer: Reload Window**) and retry.

### Step 2 - Configure the agent

1. In the **Agent name** field, enter exactly:

   ```text
   acl-remedy-advisor
   ```

   > **Note:** The agent name is case-sensitive. Entering it differently will cause the Python code in Part 2 to fail with "Agent not found".

1. In the **Model** dropdown, select `chat (via Microsoft Foundry)`.

   **Check:** If `chat (via Microsoft Foundry)` is not listed, expand **My Resources → Models** and confirm the `chat` deployment is present. If it is absent, report a failure - the environment may not be provisioned correctly.

1. In the **Instructions** field, paste the following text exactly (confirm there is no truncation):

   ```text
   You are an Australian Consumer Law (ACL) Remedy Advisor for retail staff.
   When a customer reports a problem with a product, help staff determine the
   correct remedy under the ACL consumer guarantees.

   Distinguish between a **major failure** (the customer may choose a refund,
   replacement, or repair) and a **minor failure** (the business may choose to
   repair the product within a reasonable time, or offer a replacement or
   refund).

   When assessing a situation consider:
   - The type of product and its expected lifespan
   - The price paid
   - How long the customer has had the product
   - What a reasonable consumer would expect

   Use web search to ground your guidance in current ACCC guidance at
   accc.gov.au and always cite your sources with links.

   Always state clearly that you provide general guidance, not legal advice,
   and that "no refund" signs are unlawful under the ACL.

   Be concise and practical - retail staff need fast, clear answers in a
   busy store environment.
   ```

1. Take a screenshot confirming the agent name, model, and (beginning of) instructions are correctly filled in.

### Step 3 - Add the Web Search tool

1. Scroll down to the **TOOL** section in the Agent Builder and click **Add Tool**.
1. Confirm a dialog opens.
1. Click the **Configured** tab within the dialog.
1. Locate **Web search** (labelled *Built-in · Microsoft Foundry*) and select it.
1. Click **Add Tools (1)** to confirm.
1. Confirm the dialog closes and **Web search** now appears in the **TOOL** section of the Agent Builder.

   **Check:** If the Configured tab is empty or Web search is absent, the provisioned environment may be missing the built-in tool configuration. Report this as a failure.

### Step 4 - Save and test in the playground

#### Save to Foundry

1. Click **Save to Foundry**.
1. Wait for the confirmation notification: *Agent 'acl-remedy-advisor' published to Foundry successfully.*

   **Check:** If the save fails, check the following in order:
   - The Default Project is set correctly (verify via **My Resources**).
   - The Codespace can reach the Foundry endpoint (run `curl -I $FOUNDRY_PROJECT_ENDPOINT` in the terminal).
   - If the endpoint is unreachable, report a failure - the environment may need re-provisioning.

1. Confirm the Agent Builder header now shows `acl-remedy-advisor | Microsoft Foundry | v1`. Record this version badge for later validation.

#### Test in the playground

1. Locate the playground input at the bottom of the Agent Builder.
1. Type the following test message and send it:

   ```text
   A customer wants to return a $1,200 TV that stopped working after 18 months. What are their rights under Australian Consumer Law?
   ```

1. Wait for the response and take a screenshot.
1. Verify the response meets all of these criteria:
   - Identifies whether the failure is **major** or **minor** (or both, explaining the distinction).
   - Cites at least one URL from `accc.gov.au` or a state consumer affairs site.
   - Includes a statement that the answer is general guidance, not legal advice.

   **Check:** If the response contains no citation links, the web search tool may not have fired. Try rephrasing with: *"Search accc.gov.au for current rules on consumer guarantee major failures."* If links still do not appear after rephrasing, record this as a warning (the instructions tell the agent to use web search, but the agent may not always invoke it for every query).

1. Ask a follow-up question to confirm conversation context is preserved:

   ```text
   The customer says they just want a refund and don't want a repair. Can the store insist on repairing it first?
   ```

1. Confirm the response references the TV or the 18-month scenario from the first turn - this demonstrates conversation memory is working within the Agent Builder playground.

---

## Part 2 - Chat with the agent from code

### Step 5 - Set up the environment

1. Confirm `.env` exists at the repository root. If it does not, copy it now:

   ```bash
   cp shared/.env.example .env
   ```

1. Open `.env` in the editor and confirm or set both of these values:

   ```env
   FOUNDRY_PROJECT_ENDPOINT=<your value from the onboarding file>
   AGENT_NAME=acl-remedy-advisor
   ```

   The value for `FOUNDRY_PROJECT_ENDPOINT` comes from the attendee onboarding file at `.azure/${input:envName}/<upn_local>.md`.

1. Verify `AGENT_NAME` is set to exactly `acl-remedy-advisor` (case-sensitive, with hyphens, no quotes in the file).

1. Confirm the Python dependencies are installed:

   ```bash
   uv sync
   ```

   Confirm the command completes without error. If `azure-ai-projects` is not installed, report this and run the install command again.

### Step 6 - Complete the starter code

Open `labs/introduction-foundry-agent-service/04-prompt-based-agents/src/starter.py` in the editor. Confirm the file contains four `TODO` comments. Work through each one:

#### TODO 1 - Connect to the Foundry project

Locate the line `# TODO 1` and replace it with:

```python
client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
openai = client.get_openai_client()
```

**Check:** Confirm `AIProjectClient` and `DefaultAzureCredential` are already imported at the top of the file. They should be present in the starter - if not, add the imports:

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
```

#### TODO 2 - Start a conversation thread

Locate the line `# TODO 2` and replace it with:

```python
conversation = openai.conversations.create()
print(f'Conversation started: {conversation.id}\n')
```

#### TODO 3 - Send a message to the agent

Locate the line `# TODO 3` and replace it with:

```python
response = openai.responses.create(
    conversation=conversation.id,
    extra_body={
        'agent_reference': {
            'name': agent_name,
            'type': 'agent_reference',
        },
    },
    input=user_input,
)
```

#### TODO 4 - Display the response

Locate the line `# TODO 4` and replace it with:

```python
for item in response.output:
    if item.type == 'web_search_call':
        print('[web search]')

print(f'\nAdvisor: {response.output_text}\n')
```

After completing all four TODOs, save the file (<kbd>Ctrl</kbd>+<kbd>S</kbd>). Confirm no syntax errors are shown in the editor (no red underlines in the code).

### Step 7 - Run the starter script

1. Open a terminal in the Codespace (if one is not already open).

1. Run the script:

   ```bash
   uv run python labs/introduction-foundry-agent-service/04-prompt-based-agents/src/starter.py
   ```

1. Confirm the output begins with `Conversation started:` followed by a UUID-format conversation ID. Record this ID for use in Step 8.

1. At the `You:` prompt, type the following question and press <kbd>Enter</kbd>:

   ```text
   A customer wants to return a $1,200 TV that stopped working after 18 months. What are their rights under Australian Consumer Law?
   ```

1. Confirm the output shows:
   - `[web search]` printed at least once before the advisor response (indicating the web search tool was invoked).
   - `Advisor:` followed by a response text that includes ACCC citations.

   **Check:** If `[web search]` does not appear, confirm `extra_body` in TODO 3 is correct and the agent's instructions include web search directives. The web search tool may not fire for every query; this is a warning rather than a failure if the response is otherwise accurate.

   **Check:** If the script raises `KeyError: 'FOUNDRY_PROJECT_ENDPOINT'`, confirm `.env` is saved and that `FOUNDRY_PROJECT_ENDPOINT` is not blank.

   **Check:** If the script raises an authentication error, run `az login` in the terminal.

   **Check:** If the script raises `Agent not found`, confirm `AGENT_NAME=acl-remedy-advisor` in `.env` and that the agent was saved successfully in Step 4.

1. At the second `You:` prompt, type the follow-up:

   ```text
   The customer says they just want a refund and don't want a repair. Can the store insist on repairing it first?
   ```

1. Confirm the response references the TV or 18-month scenario from the first question, demonstrating that the conversation thread is maintaining context across turns.

1. Type `exit` and press <kbd>Enter</kbd> to quit. Confirm the output shows `Goodbye.` and the script exits cleanly.

1. Take a screenshot of the terminal showing the two-turn conversation with the final `Goodbye.` message.

### Step 8 - Inspect the conversation in Agent Builder

1. Return to the **Agent Builder** tab in the editor area.

1. Click the **Conversations** tab in the Agent Builder header (it may appear as an icon or tab label alongside the configuration view).

1. Confirm the conversation recorded in Step 7 appears in the list. Identify it by matching the conversation ID printed by the script. Confirm it shows a **Completed** status and has token counts recorded.

1. Click the conversation entry to open the detail view.

1. In the detail panel, verify the agentic loop is recorded in full:
   - A **user message** item showing the question about the TV.
   - At least one **`web_search_call`** tool invocation item.
   - A **message** run step containing the final advisor response text.

1. Take a screenshot of the conversation detail view showing the agentic loop items.

   > **Note:** The entire agent loop - reasoning, tool dispatch, and response generation - executed inside Foundry Agent Service. The Python code only submitted the user message and received the finished result; the intermediate steps are only visible here in Agent Builder.

---

## Validation - confirm all criteria

Work through each item in the lab's Validation section and confirm:

1. `acl-remedy-advisor` appears under **Prompt Agents** in the Foundry Toolkit **My Resources** panel.
1. The Agent Builder header shows `acl-remedy-advisor | Microsoft Foundry | v1` (or higher if saved multiple times) after saving.
1. The playground response for the TV question cites at least one link from `accc.gov.au` or a state consumer affairs site.
1. Running `src/starter.py` prints a conversation ID, shows a `[web search]` indicator (at least for the first question), and returns a cited advisor response.
1. The follow-up question receives an answer that references the TV scenario from the first question, confirming conversation memory is working across turns in code.
1. The conversation appears in the Agent Builder **Conversations** tab with **Completed** status and the agentic loop items (user message, web_search_call, message) are visible in the detail view.

---

## Step 9 - Report results

Report the outcome of every step above. For each step state whether it **passed** or **failed**. For any failure, include:

- The exact step number and description.
- The observed behaviour.
- The expected behaviour.
- Any error messages, unexpected output, or unexpected UI state encountered.
- The screenshot filename or description if a screenshot was taken.

If all steps pass, confirm that lab module 04 end-to-end validation is complete.
