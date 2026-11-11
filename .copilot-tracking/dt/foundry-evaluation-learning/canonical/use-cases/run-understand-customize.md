# Run Understand Customize

## Learning use case

### Use Case Description

A learner runs a built-in evaluation, generates and reviews a domain rubric, and uses repeated evaluation to understand criteria changes and agent quality. This is the selected working concept, not an implemented lab.

### Use Case Overview

The lab supplies the scenario, quality priorities, fictional policy, and introductory answers. Foundry proposes rubric criteria; the learner checks and refines them rather than inventing domain requirements from a blank page. Separate live-agent exercises extend the learning beyond supplied answers.

### Business Value

The intended value is practical Foundry skill and the ability to explain evaluation evidence during solution design, development, and operation. Earlier quality alignment may support customer trust, but this lab has not demonstrated that effect. Completion time and learning effectiveness remain unmeasured.

### Primary User

A partner consultant, delivery engineer, or solution architect with basic Foundry and agent knowledge. These roles have equal priority. No prior workshop track or Python authoring is required.

### Secondary User

A facilitator supports workshop delivery. Independent learners must also be able to complete the intended core. Customers are professional context, not participants in a required delivery simulation.

### Preconditions

- Required workshop infrastructure provisioning is complete before the timed lab.
- The learner can access the required Foundry project and configured models.
- Supplied policy, requirements, datasets, and scripts are available.
- The lab readiness check confirms activity-specific access and availability.

These are intended preconditions, not verified deployment results. Architecture and detailed configuration remain open.

### Steps

1. Read the simple built-in evaluator introduction and run the supplied example.
1. Inspect its scores and explanations. Identify what the check does not establish.
1. Read the supplied scenario priorities and fictional policy.
1. Generate a rubric in Foundry. Review its criteria against those priorities.
1. Evaluate supplied answers with the rubric and compare with built-in results.
1. Add the lab-supplied additional quality requirement and test the revised rubric.
1. Evaluate the live-agent baseline, make a guided change, and compare results with the dataset, rubric, and judge settings held fixed.
1. Use separate held-back examples to check the change.
1. Evaluate synthetic live lab activity and inspect supporting conversation or trace evidence.
1. Explain the result, limits, and next investigation or quality decision.

Exact evaluator selection, the new requirement, portal steps, and live execution mechanics remain open. Keeping answers unchanged for the rubric-version comparison is a coach recommendation. Do not promise deterministic scores or a particular failure.

### Data Requirements

Use synthetic passenger requests, clearly labelled supplied answers, fictional airline policy, and explicit quality priorities. Include tool interaction data when the selected evaluator needs it. Keep separate held-back validation examples.

Keep dataset, rubric, judge settings, result explanations, and agent version identifiable when making comparisons. Generated criteria and results are intended outputs, not assets already created by this snapshot.

### Equipment Requirements

Use the workshop Foundry environment and a browser. Supplied scripts may use the workshop development environment; their source must be available. Exact hosted-agent configuration, evaluator input mappings, and model availability require verification.

### Operating Environment

Support both facilitator-led and independent use. Target less than 120 minutes after provisioning pre-work; keep agent readiness inside that time. The proposed 119-minute budget is planning arithmetic, not a measured run.

Actual device, accessibility, network, and interruption constraints: `<insufficient knowledge>`.

#### Questions to Ask

- Which device or network constraints prevent learners from completing the intended workflow?
- Which reading, navigation, or assistive-technology needs must the prototype test?

### Success Criteria

The intended learner can explain a built-in check's scope, review a generated rubric, incorporate the supplied new requirement, and interpret case-level evidence. They can distinguish changed scoring criteria from agent improvement and explain where to investigate a live result.

The intended core includes a verified quality improvement and investigation of live lab activity. Neither has been demonstrated. A saved response or text walkthrough is not a substitute for this evidence.

### Pain Points

The requester wants practical tooling experience rather than a feature tour or customer simulation. Initial concept wording caused confusion. A fresh agent cannot be assumed to produce a specific bad answer on demand, so the introductory practice uses supplied examples.

Wider learner difficulties and their frequency have not been independently measured.

### Extensions

Agent Optimizer, controlled red teaming, and CI/CD remain track requirements with proposed placement outside the timed core. Optional placement and earlier scope cuts are not all finalized. A proposed GitHub Actions evaluation workflow is not implemented.

Approximately 80% feature coverage is an unmeasured breadth goal with no agreed denominator. Do not claim catalogue coverage.

### Evidence

- [Method 5 handoff](../../method-05-user-concepts/method-06-handoff.md): selected concept, three-lens assessment, and retained constraints.
- [Requester review](../../method-05-user-concepts/stakeholder-alignment.md): built-in-first run, guided automatic generation, and supplied rubric change.
- [Problem definition](../../method-03-synthesis/problem-definition.md): audience, early repeated evaluation, and evidence limits.
- [Prototype plan](../../method-06-lofi-prototypes/prototype-plan.md): first assumption and candidate rough formats.

This snapshot records an agreed working design. It does not approve the draft PRD, implementation, cloud jobs, or release.
