# 10. Build and run a hosted agent

**Estimated time:** TBD

## Objectives

- Create a hosted agent in your Foundry project.
- Interact with the hosted agent from Python using the Agent Framework.

## Steps

> [!NOTE]
> Steps 3 and 4 run Python scripts. Confirm your `.venv` virtual environment is active before running them — look for the `(.venv)` prefix in your terminal prompt. If it is not active, run `.venv\Scripts\Activate.ps1` (Windows PowerShell) or `source .venv/bin/activate` (macOS / Linux) from the repository root.

- [ ] Create a hosted agent in the portal or Foundry Toolkit:
  - [ ] Select the deployed `chat` model.
  - [ ] Provide instructions and attach any tools or knowledge from earlier steps.
- [ ] Note the hosted agent name or identifier.
- [ ] Open `src/starter.py` and set the hosted agent target.
- [ ] Run the starter and confirm it invokes the hosted agent and returns a
   response.
- [ ] Send a follow-up prompt to confirm the hosted agent maintains context.

## Validation

- The hosted agent appears in the Agents list.
- `python src/starter.py` invokes the hosted agent and prints its response.
- A follow-up prompt returns a contextually consistent response.

## Troubleshooting

- If the hosted agent is not found, confirm the agent name and that it is saved
  and available in your project.
- If invocation fails, confirm your role grants access to invoke agents in the
  project.
- If responses ignore tools or knowledge, confirm they are attached to the
  hosted agent configuration.
