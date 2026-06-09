# 11. Agent operations and Agent ID

**Estimated time:** TBD

## Objectives

- Understand how agents are identified and managed in Foundry.
- Review the operational metadata available for an agent.

## Steps

- [ ] Open the `retail-assistant` agent in the portal.
- [ ] Review the agent's overview, including its name, identifier, and the project
   it belongs to.
- [ ] Review the operational metadata:
  - [ ] The deployed model the agent uses.
  - [ ] Attached tools and knowledge sources.
  - [ ] Run history and any available metrics or traces.
- [ ] Note how the agent identity ties together its configuration, runs, and
   access, and how this supports operations and governance.

## Validation

- You can locate the agent's identifier and the project it belongs to.
- You can list the agent's model, tools, and knowledge from the overview.
- You can find recent run history or operational metadata for the agent.

## Troubleshooting

- If metadata is missing, confirm the agent has been run at least once.
- If run history is empty, run the agent from an earlier step and refresh.
- If access is denied, confirm your role grants read access to the project.
