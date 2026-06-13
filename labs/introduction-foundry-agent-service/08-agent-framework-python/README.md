# 08. Use Agent Framework for Python

**Estimated time:** TBD

> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Connect to your Foundry project from Python with the Microsoft Agent
  Framework.
- Run the prompt-based agent programmatically.
- Inspect the response in a runnable starter application.

## Steps

- [ ] Activate the `.venv` virtual environment from the repository root, then confirm the shared dependencies are installed:

  - **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
  - **macOS / Linux:** `source .venv/bin/activate`

   ```bash
   python -m pip install -r shared/requirements.txt
   ```

   > [!NOTE]
   > If you completed lab 01 in the same terminal session, your virtual environment may already be active. Look for the `(.venv)` prefix in the terminal prompt to confirm.

- [ ] Confirm `azd env get-values` exposes the Foundry project endpoint and that
   you are signed in with `az login`.
- [ ] Open `src/starter.py` and review the Agent Framework client setup.
- [ ] Run the starter and confirm it connects to your project and returns a
   response from the agent.

  > [!NOTE]
  > The script authenticates using `DefaultAzureCredential`, which relies on your Azure CLI session. If you see an authentication error, run `az login` in the terminal and retry.
- [ ] Modify the prompt and rerun to observe different responses.

## Validation

- `python src/starter.py` runs without authentication or connection errors.
- The script prints a response generated through the Agent Framework.
- Changing the prompt changes the response.

## Troubleshooting

- **Authentication fails** — the script uses `DefaultAzureCredential`, which relies on your Azure CLI session. Run `az login` in the terminal to re-authenticate, then confirm the active subscription with `az account show`.
- If the endpoint is missing, confirm `AZURE_AI_FOUNDRY_ENDPOINT` and the
  project name with `azd env get-values`.
- If the package is missing, reinstall `shared/requirements.txt` in your active
  Python environment.
