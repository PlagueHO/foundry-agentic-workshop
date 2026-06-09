# 05. Agent tools and evaluations

**Estimated time:** TBD

## Objectives

- Add built-in tools to the prompt-based agent.
- Run evaluations to measure agent quality and safety.

## Steps

1. Open the `retail-assistant` agent in the Foundry Toolkit.
1. Add built-in tools to the agent:
   1. Select **Tools** and enable tools appropriate for a retail assistant,
      such as file search or code interpreter.
   1. Confirm each tool appears in the agent's tool list.
1. Update the agent instructions to describe when each tool should be used.
1. Run the agent and issue prompts that trigger each tool.
1. Inspect the run trace to confirm the correct tool was invoked and its output
   was incorporated into the response.
1. Open the **Evaluations** panel for the agent.
1. Create a new evaluation run:
   1. Select an evaluation dataset or provide sample prompts.
   1. Choose one or more built-in evaluators, such as groundedness or
      relevance.
   1. Start the evaluation and wait for results.
1. Review the evaluation report and note any low-scoring responses.
1. Adjust the agent instructions or tool configuration based on findings and
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
