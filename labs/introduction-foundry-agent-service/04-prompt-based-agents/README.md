# 04. Create and run a prompt-based agent

## Objectives

- Create a prompt-based agent with the Foundry Toolkit.
- Configure the agent to use a deployed model.
- Run the agent in VS Code and validate behavior with test prompts.

## Steps

1. In the Foundry Toolkit, create a new **prompt-based agent**.
1. Give the agent a clear name, for example `retail-assistant`.
1. Configure the agent:
   1. Select the deployed `chat` model.
   1. Provide instructions that describe a helpful retail assistant for an
      online store.
   1. Keep tools and knowledge empty for now; you add them in later steps.
1. Save the agent and confirm it appears in the Agents list.
1. Run the agent from the toolkit chat surface.
1. Execute a few simple test prompts, for example:
   1. "What can you help me with?"
   1. "Suggest a gift under 50 dollars for a coffee lover."
   1. "Summarize your role in one sentence."
1. Review the responses and confirm the agent follows its instructions.

## Validation

- The agent appears in the Agents list with the deployed `chat` model.
- The agent responds to test prompts and stays in character.
- You can re-run the agent and get consistent, on-topic responses.

## Troubleshooting

- If the model is unavailable, confirm the `chat` deployment exists on the
  Build tab and that your role grants access.
- If responses are empty, check the agent instructions are saved and not blank.
- If requests fail, confirm your session is authenticated and the project is
  the one assigned in Module 00.
