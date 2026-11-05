# Method 1 scope notes

## Desired change

Help Azure agent builders, architects, and operators who are new to practical evaluation propose and deliver repeatable evaluation. They should use results to make quality decisions, investigate failures, and improve at least one quality aspect.

The user wants an evaluation suite to be a reusable delivery and handover artifact. It should support development, agent or model updates, and production evaluation. Later Method 3 decisions require hands-on production evaluation of synthetic live lab-agent activity, with failure investigation through its conversation or trace. CI/CD execution is optional extra credit with a real GitHub Actions workflow. Exact technical integration remains open; see `..\prd.md` for the current draft.

## User-confirmed boundaries

- Separate track; preserve the introduction track's numbering.
- Basic Foundry, agent, and application knowledge; no practical evaluation experience required.
- Include engineers and architects. Do not require Python authoring.
- Supplied Python scripts may be required. Keep their source available.
- Support facilitated and independent completion.
- Reuse workshop provisioning and attendee projects.
- Include grounded advice and read-only MCP tool use.
- Demonstrate improvement of at least one quality aspect. Do not cover every evaluator.
- Teach rubric creation and evaluation use as primary outcomes; retain Agent Optimizer as a secondary activity.
- Make lower agent cost the main optimization objective for this lab, with quality and rubric-adherence improvements as additional outcomes.
- Match or exceed baseline quality by default. A slight reduction for a large cost saving may be explicitly accepted by the customer.
- Include a small controlled hands-on AI red-team exercise as a secondary activity.

The user's later priority clarification allows primary completion when deployment conditions block Optimizer or red-team activities. Report those activities separately with their actual status, cause, and next action; do not report blocked work as executed.

## Not yet selected

- Detailed agent and knowledge configuration, evaluator examples, and module sequence.
- Cost measurement method and acceptable trade-off values.
- Automation depth for development and production.
- Exact roles authorized to accept a quality exception.
- Cloud red-team region and tool compatibility.

## Later scenario decisions from Method 2

The user selected flight disruption as the working scenario. The agent will advise passengers directly, use read-only tools, and draw on clearly labelled fictional airline policy. Real-world legal-entitlement advice is out of scope. General retail is a parked alternative; ACL is no longer the active scenario.

## Evidence boundary

The scope records the requester's learning intent. It does not establish that partners currently lack evaluation capability or that training will improve sales.
