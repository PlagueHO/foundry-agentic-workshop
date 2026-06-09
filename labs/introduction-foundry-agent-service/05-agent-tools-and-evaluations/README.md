# 05. Agent tools and evaluations

**Estimated time:** TBD

> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Add built-in tools to the prompt-based agent.
- Run evaluations to measure agent quality and safety.

## Steps

- [ ] Open the `retail-assistant` agent in the Foundry Toolkit.
- [ ] Add built-in tools to the agent:
  - [ ] Select **Tools** and enable tools appropriate for a retail assistant,
      such as file search or code interpreter.
  - [ ] Confirm each tool appears in the agent's tool list.
- [ ] Update the agent instructions to describe when each tool should be used.
- [ ] Run the agent and issue prompts that trigger each tool.
- [ ] Inspect the run trace to confirm the correct tool was invoked and its output
   was incorporated into the response.
- [ ] Open the **Evaluations** panel for the agent.
- [ ] Create a new evaluation run:
  - [ ] Select an evaluation dataset or provide sample prompts.
  - [ ] Choose one or more built-in evaluators, such as groundedness or
      relevance.
  - [ ] Start the evaluation and wait for results.
- [ ] Review the evaluation report and note any low-scoring responses.
- [ ] Adjust the agent instructions or tool configuration based on findings and
   re-run the evaluation.

## Validation

- Each added tool appears in the agent's tool list.
- Test prompts trigger the expected tools and the run trace confirms invocation.
- An evaluation run completes and produces scores for the selected evaluators.
- You can identify at least one response to improve from the evaluation report.

## Troubleshooting

- If a tool is not invoked, strengthen the agent instructions about when to use
  it and try a prompt that clearly requires it.
- If the evaluation dataset is empty, confirm the dataset is uploaded or
  provide inline sample prompts in the evaluation wizard.
- If evaluator scores are unexpectedly low, review the groundedness and context
  settings and ensure the agent has access to the required data sources.
