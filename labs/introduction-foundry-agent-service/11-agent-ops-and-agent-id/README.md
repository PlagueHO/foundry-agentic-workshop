# Module 11: Agent operations and Agent ID

## Objectives

- Understand how agents are identified and managed in Foundry.
- Review the operational metadata available for an agent.

## Steps

1. Open the `retail-assistant` agent in the portal.
1. Review the agent's overview, including its name, identifier, and the project
   it belongs to.
1. Review the operational metadata:
   1. The deployed model the agent uses.
   1. Attached tools and knowledge sources.
   1. Run history and any available metrics or traces.
1. Note how the agent identity ties together its configuration, runs, and
   access, and how this supports operations and governance.

## Validation

- You can locate the agent's identifier and the project it belongs to.
- You can list the agent's model, tools, and knowledge from the overview.
- You can find recent run history or operational metadata for the agent.

## Troubleshooting

- If metadata is missing, confirm the agent has been run at least once.
- If run history is empty, run the agent from an earlier step and refresh.
- If access is denied, confirm your role grants read access to the project.
