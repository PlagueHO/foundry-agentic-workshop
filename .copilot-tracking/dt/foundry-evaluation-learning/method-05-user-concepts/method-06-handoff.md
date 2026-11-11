# Method 5 handoff to Method 6

## Approval and selected concept

The requester explicitly approved bounded Method 5 closure and progression to Method 6 at 2026-11-07T16:43:57.048+13:00. Select one combined concept: **Run Understand Customize**. The Evidence First and Criteria First cards in `concepts.yml` preserve the alternatives that informed it; they are not competing current options.

The normal exit signal is "30-second comprehensible visual with feedback captured". Requester feedback is captured in `stakeholder-alignment.md`, but the timed comprehension test and independent learner review have not occurred. Method 5 is complete for progression, not fully validated.

## Selected journey

1. Introduce and run a simple built-in evaluator on supplied answers.
1. Inspect scores and explanations, including what the check does not establish.
1. Use supplied priorities and fictional airline policy to generate a rubric in Foundry.
1. Review the generated criteria and evaluate the supplied answers.
1. Incorporate one supplied additional requirement and test the revised rubric.
1. Evaluate a live agent, make a guided change, and compare results.
1. Evaluate synthetic live lab activity and investigate supporting evidence.

The coach recommends keeping supplied answers unchanged for the rubric-version comparison. This distinguishes changed measurement from agent improvement; it does not guarantee a score or pass/fail change. For agent-version comparisons, keep the dataset, rubric, and judge settings fixed.

## Selection rationale and three-lens assessment

| Lens | Evidence and rationale | Remaining limit |
|---|---|---|
| Desirability | The requester asked for hands-on built-in checks before rubric creation, automatic generation from lab-supplied priorities, and a supplied new requirement. The combined journey incorporates those corrections. | Requester approval is not independent learner evidence; initial concept wording caused confusion. |
| Feasibility | Official documentation supports built-in evaluation and generated rubrics. Supplied examples avoid dependence on a fresh agent making a specific mistake. | Integrated hosted-agent execution, live improvement, production scoring, input mappings, and elapsed time remain unverified. |
| Viability | One scenario and reusable supplied assets support a tooling-focused lab without customer role-play or required Python authoring. | Facilitator effort, maintenance, model/runtime cost, and learner completion remain unmeasured. |

This is a reasoned working selection, not evidence that every lens has passed validation.

## Constraints carried forward

- Target less than 120 minutes, excluding required provisioning pre-work. The proposed 119-minute budget is planning arithmetic, not measured duration.
- Keep consultants, delivery engineers, and solution architects equally important. Require no Python authoring; make supplied source available.
- Use synthetic flight-disruption data, read-only tools, and fictional policy. Exclude booking, claim submission, and legal-entitlement advice.
- Explain the provenance of supplied answers. Their evaluation is real, but does not demonstrate live generation or production behavior.
- Generated criteria require review. Fixed input does not make model judgments deterministic.
- Keep hands-on live improvement and production evaluation in the intended core. Do not silently substitute saved answers for them.
- Optimizer, red teaming, and CI/CD remain track requirements with proposed optional placement outside the timed core; closure does not approve their removal or all earlier scope cuts.
- Approximately 80% coverage has no agreed denominator. Do not present it as measured coverage.

## Method 6 scope and tests

Start with rough, human-read walkthroughs of the opening built-in-to-rubric transition. Test one assumption per variation: whether a learner can distinguish the purpose of the built-in check from the purpose of the domain rubric.

Use the planning alternatives in `../method-06-lofi-prototypes/prototype-plan.md`. Capture observed actions, hesitations, and misunderstandings, not invented stakeholder responses. No participant has been recruited or tested.

A paper or text walkthrough cannot verify portal correctness, evaluator behavior, live-agent reliability, cloud cost, ingestion latency, or full completion time. Those require separately authorized functional testing. No model invocation, cloud job, implementation, commit, push, or PR is authorized by this transition.
