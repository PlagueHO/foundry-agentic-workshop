# Consolidated problem definition

## Problem

Consultants, delivery engineers, and solution architects need practical ways to define, run, and interpret repeatable evaluations from the start of development and throughout the product lifecycle so they can agree quality requirements, design and build agentic solutions, assess changes against those requirements, and hand over checks and processes for continued use.

The requester approved this gap. It refines the original feature request for rubric evaluation into a reusable delivery and operating capability. It does not assert that all partners lack evaluation knowledge.

The requester explicitly gives delivery engineers and solution architects equal importance to consultants. Their needs must not be reduced to explaining evaluation to customers.

### Role-specific working needs

| Role | Working problem framing |
|---|---|
| Consultant | Connect customer expectations to quality criteria and explain evidence, limits, and delivery commitments |
| Delivery engineer | Adopt evaluation early, evaluate while building, and repeatedly check how changes affect agreed quality requirements |
| Solution architect | Design evaluation into the solution lifecycle and define where checks, quality decisions, and operating responsibilities belong |

Equal audience priority and the delivery-engineer need for early, repeated evaluation are requester-confirmed requirements. The consultant and architect descriptions remain design interpretations. None is independently validated across the learner population.

The requester compares this practice to TDD: evaluation should provide feedback while engineers build, not only at release or handover. Evaluation is a verification capability for non-functional requirements such as agreed agent quality. The requirement, evaluation criterion, evidence, and decision must remain linked throughout product development. This analogy does not require identical generated answers, a particular test framework, or mandatory CI/CD.

## Audience and scope

Partner consultants, AI engineers, presales and solution architects, and operators with basic Foundry and agent knowledge. No previous workshop track or Python authoring is required. Supplied scripts are acceptable.

Use a separate evaluation track with a passenger-facing flight-disruption assistant. Policy is fictional and tools are read-only. General retail remains parked. Preserve the existing introduction progression.

### Explicit Microsoft product objective

The requester also intends to build awareness and practical capability in Microsoft Foundry evaluation features. Partner engineers, consultants, and architects must be able to use these features and clearly communicate their value in customer solutions. The lab is not only a platform-neutral introduction to evaluation.

Core completion must not require a third-party evaluation platform. This does not prohibit optional integrations or establish that Foundry meets every possible need. Feature claims and support limits must match verified behavior. This is a requester objective, not evidence that partners currently lack product awareness or that the platform is universally sufficient.

## Observable outcomes

- After the first run, explain what evaluation is, its value to a customer and agentic solution, and why it should be provided.
- Run evaluations, create or revise a rubric, interpret case-level evidence, and improve at least one quality aspect.
- Establish evaluation criteria early and repeat checks during development to assess changes against an explicit non-functional quality requirement.
- Use evidence for a reasoned change or release decision, including deciding not to release.
- In the core production exercise, identify a quality failure in live lab-agent activity, inspect its conversation or trace, and explain what needs investigation. Use synthetic passenger requests.
- Carry reusable checks and processes into handover. Treat CI/CD execution as optional extra credit, not a core prerequisite.
- Use Microsoft Foundry evaluation features hands-on and explain their role, customer value, and limits without relying on a required third-party evaluation platform.

Optimizer and controlled red teaming remain secondary learning activities. Report blocked, unverified, failed, and completed states honestly. They must not gate primary completion when deployment conditions block them.

## Five-dimension assessment

| Dimension | Assessment | Remaining evidence |
|---|---|---|
| Research fidelity | Source types, quotations, paraphrases, and requester requirements are distinguished | Supplied practitioner excerpts have not been independently retrieved; no observed workflows |
| Stakeholder completeness | Requester and two practitioner perspectives are represented | Direct learners, customers, and operators are not represented |
| Pattern robustness | Customer-value framing has support from both practitioners; handover has narrower support; external engineering guidance supports early repeated evaluation | No basis for population-wide adoption claims or measured training benefit |
| Actionability | Outcomes and core/optional boundaries are explicit | Architecture, delivery duration, budget, module sequence, and technical tests remain open |
| Team alignment | Requester confirmed bounded closure and the move to Method 4 after the equal-audience, early-evaluation, and Foundry capability objectives were captured | Proposed PRD acceptance criteria and representative learner understanding still need review |

## Disposition

The requester explicitly confirmed closing this synthesis round as a working design baseline and moving cautiously to Method 4 on 2026-11-05. Method 3 is recorded complete for this round by team agreement, not as fully validated research: stakeholder completeness and pattern robustness remain limited. This is a user-approved bounded transition, not an automatic pass of the normal five-dimension gate. No validated RPI handoff is issued.

The draft PRD may capture agreed intent now. It does not approve architecture, implementation, cloud jobs, or the document's proposed acceptance details. Preserve the gaps for later research and representative learner testing rather than inventing evidence.

No canonical deck is offered at this checkpoint because the validated problem-space exit has not been reached. No board export or rendering is required to author the draft.

The normal exit signal is "Themes validated across sources; team alignment confirmed." It is only partly met. Carry the gaps into ideation and later learner testing; reconsider the baseline if new evidence contradicts it. The industry research supports the early-evaluation principle, not the lab's learning effectiveness.

## Sources

- `insight-statements.md`: evidence-linked insights and confidence.
- `affinity-clusters.md`: grouped evidence, tensions, and agreed teaching candidates.
- `practitioner-evidence.md`: anonymous practitioner summaries and limits.
- `..\implementation-plan.md`: detailed scope decisions and technical questions.
- [Industry evidence](../../../research/2026-11-05/evaluation-driven-development-research.md): support and limits for evaluation-driven development.
