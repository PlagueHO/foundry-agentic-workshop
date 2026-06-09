# 06. Integrate MCP tools

**Estimated time:** TBD

> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Add Model Context Protocol (MCP) tools to the prompt-based agent.
- Invoke the tools during agent execution.

## Steps

- [ ] Open the `retail-assistant` agent.
- [ ] Add an MCP tool source to the agent:
  - [ ] Select **Tools** and add an MCP tool connection.
  - [ ] Confirm the tool's available functions are discovered and listed.
- [ ] Update the agent instructions to describe when to call the MCP tool.
- [ ] Run the agent and issue a prompt that should trigger the tool, for example a
   request that requires a live lookup the model cannot answer on its own.
- [ ] Inspect the run and confirm the MCP tool was invoked and its result was used
   in the response.

## Validation

- The MCP tool appears in the agent's tool list with discovered functions.
- A test prompt triggers the tool and the response reflects the tool output.
- The run trace shows the tool invocation.

## Troubleshooting

- If tool functions are not discovered, confirm the MCP server endpoint is
  reachable and the connection is authenticated.
- If the tool is never called, strengthen the agent instructions about when to
  use it, and use a prompt that clearly requires it.
- If invocation fails, review the run trace for the specific tool error.
