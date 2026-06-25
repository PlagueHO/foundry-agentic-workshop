---
description: "Review and test a single module in the agent-framework-dotnet lab end-to-end. Validates structure, content, diagrams, documentation links, code quality, and execution of both solution and starter code. Produces a severity-graded findings report."
---

## Inputs

- ${input:moduleNumber}: (Required) Two-digit module number to test (e.g. `02`, `04`, `09`).
- ${input:envName}: (Required) The azd environment name the lab was provisioned into (e.g. `foundry-hol2`).

---

You must review and test module `${input:moduleNumber}` of the `agent-framework-dotnet` lab located at `labs/agent-framework-dotnet/${input:moduleNumber}-*/`. The module is a .NET 10 C# project that uses the Microsoft Agent Framework (MAF) and targets Azure AI Foundry.

> [!IMPORTANT]
> Any Azure login dialogs that appear during testing must be completed by the user. Pause and prompt the user whenever a sign-in dialog is encountered. Do not enter credentials automatically.

Track every finding as you work through each section below. You will produce a consolidated report at the end.

---

## Pre-flight — Verify the environment is ready

Before executing any module steps, confirm all prerequisites are satisfied. **Do not proceed if any check fails** — report the failure and ask the user to resolve it.

### Check 1 — Locate the module directory

1. Identify the full module directory path by finding the folder matching `labs/agent-framework-dotnet/${input:moduleNumber}-*/`.
1. Confirm the following files exist inside it:

   ```powershell
   Get-ChildItem labs/agent-framework-dotnet/${input:moduleNumber}-* -Recurse -Include README.md, Program.cs
   ```

1. Confirm at minimum: `README.md`, `src/Program.cs`, and `solution/Program.cs` are present.
1. Record the resolved directory name (e.g. `04-function-tools`) — use it as `MODULE_DIR` in all subsequent steps.

### Check 2 — Confirm .NET SDK is available

1. Run:

   ```powershell
   dotnet --version
   ```

1. Confirm the version is `10.x` or later (required by `labs/agent-framework-dotnet/global.json`).

### Check 3 — Confirm `.env` file exists and contains required values

1. Confirm `.env` exists at the repository root and `FOUNDRY_PROJECT_ENDPOINT` is set:

   ```powershell
   Select-String -Path .env -Pattern 'FOUNDRY_PROJECT_ENDPOINT'
   ```

1. Confirm the value has the form `https://<resource>.services.ai.azure.com/api/projects/<project>`.
1. Confirm `AGENT_MODEL` is set (or note that it defaults to `chat` when absent).
1. If the module under test requires additional environment variables (for example `AZURE_SEARCH_SERVICE_ENDPOINT` for Module 06, or `OTEL_EXPORTER_OTLP_ENDPOINT` for Module 12), confirm those are present too. Check the module's `README.md` for the full list.

   **Check:** If `.env` does not exist, confirm with the user that Module 01 has been completed, then copy `shared/.env.example` to `.env` and populate it from `azd env get-values`.

### Check 4 — Confirm Azure authentication

1. Confirm the Azure CLI is signed in:

   ```powershell
   az account show --query '{user:user.name, subscription:id}' -o table
   ```

1. Confirm the subscription ID matches `AZURE_SUBSCRIPTION_ID` from `.env`.
1. If the command fails, pause and ask the user to run `az login` before continuing.

### Check 5 — Restore NuGet packages for the module

1. Restore packages for the starter project:

   ```powershell
   dotnet restore labs/agent-framework-dotnet/MODULE_DIR/src
   ```

1. Restore packages for the solution project:

   ```powershell
   dotnet restore labs/agent-framework-dotnet/MODULE_DIR/solution
   ```

1. Confirm both commands complete without errors.

---

## Section A — Structure review

Review the `README.md` against the canonical lab module structure defined in `.github/instructions/lab-module-readme.instructions.md`.

### A1. Title format

1. Open `README.md` and confirm the first line matches the pattern `# NN. Title` (two-digit zero-padded number, period, space, title — no "Module" prefix).

   **Check:** Record a finding if the title format deviates.

### A2. Section order

1. Confirm the following sections appear in this exact order:

   ```text
   # NN. Title
   **Estimated time:** N minutes
   ![diagram](path)
   > [!IMPORTANT]   (prerequisite callout — omit only for Module 01)
   > [!TIP]         (tick-the-checkbox reminder)
   ## Objectives
   ## Concepts
   ## Steps
   ## Validation
   ## Congratulations 🎉
   ## Troubleshooting
   ```

1. Record a finding for any missing section or ordering deviation.

### A3. Steps structure

1. Confirm Steps are grouped into `### Part N — Description` sub-sections.
1. Confirm each individual step uses `#### N. Step title` heading format.
1. Confirm every attendee action is a `- [ ]` task-list item with code blocks indented 2 spaces under the item.
1. Confirm `TODO` comments in the starter follow the pattern `// ── TODO N ──...`.

### A4. Validation section

1. Confirm the `## Validation` section lists observable, concrete outcomes (printed output, file existence, console colours, or HTTP responses) — not vague statements like "the agent responds".

### A5. Congratulations section

1. Confirm the `## Congratulations 🎉` section ends with a `> [!TIP]` next-up callout using the format `**Next up → [Module NN: Title](../NN-name/README.md)**`.
1. Confirm the congratulations paragraph summarises what was achieved in this specific module.

### A6. Troubleshooting table

1. Confirm the `## Troubleshooting` section contains a `| Symptom | Fix |` table.
1. Confirm a `NotImplementedException` row is present when the module has TODO items in the starter.
1. Confirm an `AuthenticationFailedException` row is present.

---

## Section B — Diagrams and images review

### B1. Diagram presence and placement

1. Confirm a diagram or banner image appears immediately after the `**Estimated time:**` line.
1. Confirm the image path is relative and references a file under `docs/assets/`.

### B2. Diagram relevance

1. Read the `alt` text of the diagram.
1. Confirm the alt text accurately describes a diagram or visual that is relevant to the module's content — not a generic banner reused from an unrelated module.
1. Confirm the image file referenced by the `![...](path)` actually exists on disk:

   ```powershell
   Test-Path <image-path>
   ```

1. Record a finding if the diagram is generic, mismatched to module content, or the file is missing.

### B3. Screenshots (if any)

1. If the module contains `<details><summary>📸 Screenshot:` blocks, confirm each screenshot file referenced inside them exists on disk.
1. Record a finding for any missing screenshot file.

---

## Section C — Content and concept clarity review

### C1. Objectives completeness

1. Read the `## Objectives` bullet list.
1. Confirm every MAF type or method introduced in the Steps section (for example `AIFunctionFactory.Create`, `AgentSession`, `McpServer`, `AIContextProvider`) is named in Objectives.
1. Record a finding for any major API introduced in Steps but absent from Objectives.

### C2. Concepts section

1. Confirm the `## Concepts` section introduces every new MAF construct used in the starter TODOs before it appears in the Steps.
1. Confirm each concept entry includes a focused code snippet demonstrating the construct in isolation (not lifted directly from the solution).
1. Confirm concepts are explained at the appropriate level — new attendees should understand what each type does and why it is needed, without reading the source code.
1. Record a finding for any concept that is missing, too terse, or explained only by showing code without prose.

### C3. Microsoft Learn links

1. Search the `README.md` for links to `learn.microsoft.com`.
1. Confirm at least one link to the Microsoft Agent Framework documentation is present. The canonical overview URL is:

   `https://learn.microsoft.com/en-us/agent-framework/overview/`

1. Confirm any `learn.microsoft.com` links present point to pages that exist and are relevant to the module's content. Use `fetch_webpage` to spot-check up to three links.
1. Record a finding if no Microsoft Learn link is present, or if a link resolves to a 404 or unrelated page.

---

## Section D — Code quality review

### D1. Starter code — TODO coverage

1. Open `src/Program.cs`.
1. Confirm every `// ── TODO N` block in the starter is commented-out working code matching the snippet provided in the `README.md` Steps section.
1. Confirm the starter compiles as-is (before any TODOs are filled in):

   ```powershell
   dotnet build labs/agent-framework-dotnet/MODULE_DIR/src --no-restore
   ```

1. Record a finding if the starter fails to build or if a TODO block does not match the README snippet.

### D2. Solution code — completeness

1. Open `solution/Program.cs`.
1. Confirm the solution contains no `TODO` comments.
1. Confirm every TODO from the starter is resolved in the solution.
1. Confirm the solution compiles cleanly:

   ```powershell
   dotnet build labs/agent-framework-dotnet/MODULE_DIR/solution --no-restore
   ```

1. Record a finding if the solution fails to build.

### D3. Code clarity and comments

1. Review both `src/Program.cs` and `solution/Program.cs` for:
   - Clear, concise comments on every MAF construct (for example `AIAgent`, `AgentSession`, `AIFunctionFactory`, `McpServer`, `AIContextProvider`).
   - Comments that explain the *why* of a pattern, not just the *what* (for example "// AgentSession maintains conversation state across turns — pass it to every RunAsync call").
   - Console output messages that let attendees see when the agent, tool, or streaming call is active.
1. Record a finding for any MAF construct used without an explanatory comment.

### D4. DRY and simplicity

1. Confirm there is no duplicate environment-loading or credential-creation boilerplate that could be extracted (given that each module is a self-contained `Program.cs`, a helper method or local function is acceptable).
1. Confirm the code is as short as possible while remaining readable — no dead code, no commented-out blocks left from prior modules, no unused `using` directives.
1. Record a finding for any obvious duplication or dead code.

### D5. Agent Framework samples alignment

1. Fetch the Microsoft Agent Framework .NET samples index from GitHub and compare patterns:

   ```
   https://github.com/microsoft/agent-framework/tree/main/dotnet/samples
   ```

1. Identify the sample most similar to this module (for example `SingleTurnAgent` for Module 02, `FunctionToolsAgent` for Module 04).
1. Confirm the module code uses the same primary APIs and patterns as the equivalent sample.
1. Record a finding for any significant API or pattern divergence (for example using a deprecated method, missing a recommended option, or using a workaround the samples do not use).

---

## Section E — Execution testing

### E1. Run the solution

1. Run the solution project directly:

   ```powershell
   dotnet run --project labs/agent-framework-dotnet/MODULE_DIR/solution
   ```

1. Wait for the run to complete (or for the interactive loop to start, if the module uses one).
1. Confirm the output matches the expected behaviour described in the `## Validation` section of the README.
1. Record any error, unexpected output, or missing output as a finding.

### E2. Complete the starter and run it

1. Create a temporary working copy of the starter source:

   ```powershell
   $tmp = "labs/agent-framework-dotnet/MODULE_DIR/.test-starter"
   Copy-Item -Recurse -Force labs/agent-framework-dotnet/MODULE_DIR/src $tmp
   ```

1. Open `$tmp/Program.cs`.
1. Apply each TODO replacement exactly as described in the module README Steps — replace every `// ── TODO N` commented-out block with the uncommented snippet from the README.
1. Confirm no `TODO` comments remain in the file.
1. Run the completed starter from the temporary copy:

   ```powershell
   dotnet run --project $tmp
   ```

1. Confirm the output matches the same `## Validation` criteria as the solution run.
1. Clean up the temporary copy:

   ```powershell
   Remove-Item -Recurse -Force $tmp
   ```

1. Record any mismatch between the starter output and the solution output as a finding.

### E3. Verify streaming output (if applicable)

1. If the module includes a streaming call (`RunStreamingAsync` or similar), confirm the output is clearly incremental (tokens appearing progressively) rather than all at once.
1. Record a finding if the streaming section produces no visible incremental output.

### E4. Verify tool invocation (if applicable)

1. If the module registers function tools or MCP tools, confirm the `[Tool]` log lines appear in the console output, showing that the agent actually called the tool.
1. Record a finding if expected `[Tool]` lines are absent.

---

## Section F — Dependency and environment review

### F1. Project file review

1. Open the `.csproj` file in `src/`.
1. Confirm package references are satisfied by the central `Directory.Packages.props` (no `Version=` attributes on `<PackageReference>` items).
1. Confirm the `<TargetFramework>` matches `net10.0`.
1. Record a finding for any hardcoded version or wrong target framework.

### F2. Environment variable documentation

1. Confirm every environment variable referenced in `src/Program.cs` or `solution/Program.cs` is listed in:
   - The `README.md` (either in a prerequisite callout or the Setup steps).
   - `shared/.env.example`.
1. Record a finding for any undocumented or unexemplified environment variable.

---

## Report

After completing all sections, produce a findings report. List every finding recorded during the review. For each finding include:

- **ID** — sequential number (F-01, F-02, …).
- **Section** — the letter and number code above (e.g. A1, C3, E2).
- **Severity** — one of: `Critical` (blocks execution or learning), `Major` (significant gap in quality or correctness), `Minor` (style, clarity, or non-blocking issue), `Info` (suggestion or observation).
- **Location** — file and line number or region (e.g. `README.md line 45`, `src/Program.cs TODO 2`, `solution/Program.cs`).
- **Description** — what was found.
- **Recommendation** — the specific change that would resolve the finding.

Present the report as a Markdown table:

| ID | Section | Severity | Location | Description | Recommendation |
|----|---------|----------|----------|-------------|----------------|

If no findings exist for a section, omit it from the table and note `No findings` at the end of the section's check.

After the table, provide a one-paragraph summary stating whether module `${input:moduleNumber}` passes end-to-end validation, how many findings were recorded at each severity level, and the single most important improvement to make first.
