# Resume Foundry Evaluation Learning

## Current checkpoint

The user paused during Design Thinking Method 2 to continue from another machine. Method 1 is complete. Method 2 is not complete, and no move to Method 3 has been approved.

This checkpoint saves planning and research only. It does not authorize lab implementation, infrastructure changes, paid evaluations, optimization jobs, or red-team scans. No cloud feasibility run has been completed.

## Read these files first

1. `coaching-state.md`: YAML state in a fenced block, user quotations, decisions, method history, and remaining questions.
1. `implementation-plan.md`: working learning outcomes, proposed modules, deployment requirements, and implementation boundaries.
1. `method-02-research\constraint-catalog.md`: repository evidence, official sources, scenario comparison, and the latest red-team clarification.
1. `method-01-scope\scope-boundaries.md`, `method-01-scope\stakeholder-map.md`, and `method-01-scope\assumptions-log.md`: learner scope and unvalidated assumptions.

All paths above are relative to this directory. The repository copies are authoritative; recovery must not depend on the earlier machine's session directory.

## Confirmed direction

- Build a separate evaluation track without requiring completion of another track.
- Use flight disruption as the working scenario. The assistant advises passengers directly.
- Use read-only operational tools and clearly labelled fictional airline policy. Exclude real-world legal-entitlement advice.
- Keep general retail as a parked alternative. Do not implement both scenarios or retain ACL as the active scenario.
- Do not require learners to write Python. Supplied scripts are acceptable, with source available.
- Require rubric creation, use with Agent Optimizer, and a small hands-on red-team exercise.
- Prioritize lower agent runtime cost while matching or exceeding baseline quality. Any quality reduction needs explicit customer acceptance.
- Support independent and facilitated learning, including reusable evaluation assets for handover and operations.
- Reuse existing provisioning. Support multiple tracks through maintained, data-driven requirements, with individual and organizer behavior.
- Recommend East US 2 for new environments. Preserve existing regions and organizer choices, and report module-specific limitations.

## Preferred technical direction, not a final architecture

Investigate one supplied Python hosted Responses agent, prepared for optimization, throughout the track. The earlier prompt-agent portal recommendation is suspended. Unknown Optimizer access must not by itself force a prompt-agent fallback.

The existing .NET travel track supplies scenario and tool ideas; it is not a requirement to adopt .NET or a multi-agent design.

## Latest unresolved question

The last discussion corrected an overly broad interpretation of red-team support.

- Agent response testing, tool-mediated simulation or indirect-injection coverage, and MCP backend security are separate concerns.
- Official documentation lists hosted container agents as supported targets and excludes non-Azure tools, but does not explain the exact effect of a custom remote MCP dependency.
- Do not claim that such a dependency blocks all agent scans. Do not assume it is fully supported either.
- Ask whether ordinary content-risk scans can target the unchanged hosted agent. Separately ask which agentic tests can observe, mock, or inject into custom remote MCP results.
- A completed scan does not establish backend security or complete tool coverage.

Sources and a proposed incremental feasibility test are in the constraint catalog. No support question has been sent on the user's behalf.

## Remaining research

- Clarify red-team execution and coverage through authoritative guidance or a separately authorized non-production test.
- Verify hosted rubric-to-Optimizer integration, effective identity access, model roles, quota, and cost evidence.
- Prepare an aligned flight/policy fixture proposal with a fixed scenario clock. Existing flight lookups do not validate booking ownership or passenger eligibility.
- Do not reuse the existing rights-focused knowledge unchanged. Existing flight tools also include a claim-submission operation outside the read-only scope.
- Revisit partner evidence when replies arrive. Beginner evaluation experience remains a design assumption, not a verified partner finding.
- Agree detailed tasks, rubric criteria, module sequence, and operational automation depth before implementation.

## Resume protocol

Load the DT coaching foundation and Method 2 references. Read the saved state and confirm the checkpoint with the user. Continue from the red-team execution-versus-coverage question unless the user redirects. Do not restart Method 1 or mark deferred research complete.
