# Module 09: Use Agent Framework for Python

## Objectives

- Connect to your Foundry project from Python with the Microsoft Agent
  Framework.
- Run the prompt-based agent programmatically.
- Inspect the response in a runnable starter application.

## Steps

1. Install the shared dependencies from `shared/requirements.txt`.
1. Confirm `azd env get-values` exposes the Foundry project endpoint and that
   you are signed in with `az login`.
1. Open `src/starter.py` and review the Agent Framework client setup.
1. Run the starter and confirm it connects to your project and returns a
   response from the agent.
1. Modify the prompt and rerun to observe different responses.

## Validation

- `python src/starter.py` runs without authentication or connection errors.
- The script prints a response generated through the Agent Framework.
- Changing the prompt changes the response.

## Troubleshooting

- If authentication fails, run `az login` and confirm the active subscription.
- If the endpoint is missing, confirm `AZURE_AI_FOUNDRY_ENDPOINT` and the
  project name with `azd env get-values`.
- If the package is missing, reinstall `shared/requirements.txt` in your active
  Python environment.
