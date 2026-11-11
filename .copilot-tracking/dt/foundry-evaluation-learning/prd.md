---
prd_id: "PRD-FOUNDRY-EVALUATION-LEARNING"
title: "Foundry Evaluation Learning Track"
status: "draft"
version: "0.2.0"
owners: ["Workshop requester"]
reviewers: ["Workshop maintainer", "Technical reviewer", "Representative learner"]
created_date: "2026-11-05"
last_updated: "2026-11-11"
product_goal_ids: ["GOAL-001", "GOAL-002", "GOAL-003", "GOAL-004"]
product_goal_smart_status: "deferred"
fr_to_ac_coverage_threshold_pct: 80.0
fr_to_goal_coverage_threshold_pct: 100.0
diagram_format: "none"
lineage:
  supersedes: []
  superseded_by: []
source_brd_id: null
requirement_id_prefixes:
  fr: "FR"
  ac: "AC"
  nfr: "NFR"
  con: "CON"
  goal: "GOAL"
license: "CC-BY 4.0 (Microsoft HVE-Core)"
---

# Foundry Evaluation Learning Track

> **PRD-FOUNDRY-EVALUATION-LEARNING** | Draft 0.2.0 | Not approved for implementation

## Executive Summary

Create a separate Microsoft Foundry workshop track that teaches consultants, delivery engineers, solution architects, and operators to run and use evaluations. Consultants, delivery engineers, and architects are equally important audiences with distinct needs. Learners should define quality expectations, design evaluation into solutions, run repeatable checks, explain evidence and its limits, improve at least one quality aspect, and carry reusable evaluation assets into delivery and handover.

This is a hands-on learning lab like the existing repository labs, not a real customer delivery. Customer priorities and handover explain why the tooling matters; they do not require customer role-play, agreement meetings, or a separate delivery/handover simulation. Interpret the lifecycle and reuse requirements below as learning outcomes and reusable lab guidance.

Microsoft product capability is an explicit learning objective, not just the hosting context. Learners must gain practical experience with Microsoft Foundry evaluation features and explain how those features support customer solutions. The core path must not require a third-party evaluation platform. Teach product value through actual use and evidence, with support limits stated accurately; do not imply that Foundry covers every evaluation need or that external systems are never appropriate.

Use a passenger-facing flight-disruption assistant with read-only tools, synthetic requests, and fictional airline policy. The agent is a teaching vehicle, not a production airline service. No earlier track completion or Python authoring is required.

Delivery engineers must learn to adopt evaluation early and evaluate while building. Like the feedback cycle in TDD, repeated checks should show how changes affect the system throughout product development. Teach evaluation as a capability for verifying non-functional quality requirements, not only as a final release or handover activity. Link the requirement, criteria, evidence, and decision; do not imply that an evaluation score alone proves compliance.

Hands-on production evaluation is core. Learners identify a quality failure in live lab-agent activity, inspect its supporting conversation or trace, and explain what needs investigation. CI/CD execution is optional extra credit with a real repository GitHub Actions workflow. Agent Optimizer and controlled red teaming are secondary activities whose deployment limitations must not block primary completion.

Primary success evidence is a learner's completed evaluation and explanation, not a portal click sequence or an improved score alone. The requester confirmed infrastructure provisioning as pre-work outside the less-than-two-hour lab target and asked for approximately 80% feature coverage. Treat the coverage request as a breadth objective, not a measured percentage of the entire Foundry catalogue: the feature denominator is not agreed. Detailed pacing, spend budget, cohort targets, and release date remain open. This draft captures agreed intent and proposed acceptance tests; it does not prove learning effectiveness or technical feasibility.

The selected journey is **Run Understand Customize**. Learners first run a simple built-in evaluator on labelled supplied answers and inspect the results. They then generate and review a rubric from lab-supplied priorities and policy, evaluate the answers, and test a rubric revision against one supplied additional requirement. Separate exercises address live-agent improvement and production evaluation. The lab does not require blank-page domain discovery or writing all criteria from scratch.

## Product Context

The original rubric-module request expanded into a reusable evaluation learning track. Two anonymous practitioner perspectives describe differing assessment practices: semantic comparison and pilot judgment in one case; lifecycle checks and recommended handover in another. One source expresses interest in a more formal lab. This is limited evidence, not an industry-wide capability assessment.

The requester approved the problem framing and learning boundaries. Detailed synthesis is in [problem-definition.md](method-03-synthesis/problem-definition.md). No approved BRD, feasibility handoff, or formal RPI research handoff was supplied. Existing planning notes provide contextual observations, not those formal contracts.

On 2026-11-11 the requester authorized PRD refinement while explicitly leaving Method 6 incomplete. Methods 1-5 are closed for progression, with bounded validation limits for Methods 3 and 5. Method 6 has a [prototype plan](method-06-lofi-prototypes/prototype-plan.md), but no built variations, confirmed participants, test observations, or constraint discoveries. This is a requirements-authoring transfer, not a validated Solution Space exit, Method 7 transition, or implementation approval.

The [selected-concept handoff](method-05-user-concepts/method-06-handoff.md) and [requester feedback](method-05-user-concepts/stakeholder-alignment.md) supply the later learning-design decisions. The original Evidence First and Criteria First openings are design history, not unresolved alternatives. Requester selection is not independent learner validation.

## Users and Personas

| Role | Job | Potential difficulty | Intended outcome |
|---|---|---|---|
| Consultant | Explain and propose evaluation as normal delivery practice | Connecting technical scores to customer expectations | Explain value, limits, and a reasoned quality decision |
| Delivery engineer, including AI engineer | Adopt evaluation early and evaluate while building | Seeing how development changes affect non-functional quality requirements | Establish criteria and a baseline early, repeat checks, and investigate improvements or regressions |
| Solution architect | Design evaluation into the solution lifecycle | Defining check placement, quality decisions, and operating responsibilities | Explain how evaluation supports design, delivery, changes, and handover |
| Customer, successor partner, or operator | Maintain confidence after changes and handover | Reusing checks without the original project team | Run the supplied process and identify investigation needs |
| Facilitator or organizer | Provide a usable shared learning environment | Model, access, region, and quota differences | Prepare assets and report activity-specific readiness |

These are role-based descriptions, not invented biographies or observed learner behavior. Equal audience priority and the delivery-engineer need for early, repeated evaluation are requester-confirmed. Other detailed difficulties remain working design interpretations, not independent research findings. Practical evaluation experience is assumed limited; operator and customer perspectives still need direct validation.

## Design Decisions

| ID | Decision | Authority and status |
|---|---|---|
| DD-001 | Separate evaluation track; preserve the introduction progression | User-confirmed |
| DD-002 | Flight advice, read-only tools, fictional policy, no legal-entitlement advice | User-confirmed teaching scope |
| DD-003 | Production evaluation is hands-on core; GitHub Actions CI/CD is optional extra credit | User-confirmed |
| DD-004 | Secondary Optimizer/red-team deployment blocks do not prevent primary completion | User-confirmed |
| DD-005 | Investigate one supplied Python hosted agent | Preferred direction, not approved architecture |
| DD-006 | Author a draft PRD before implementation | User-authorized; formal synthesis validation remains incomplete |
| DD-007 | Teach Microsoft Foundry feature use and value explicitly; no third-party evaluation platform required for core completion | User-confirmed objective; technical support still requires verification |
| DD-008 | Use Run Understand Customize, with an actual simple built-in run and result review before rubric generation | Requester-selected in Method 5; comprehension and execution remain untested |
| DD-009 | Use labelled supplied acceptable/unacceptable answers for introductory practice and explain their purpose | Requester-confirmed; does not satisfy live-agent improvement or production evaluation |
| DD-010 | Generate a starting rubric from supplied priorities and policy, review it, then test one supplied additional requirement | Requester-confirmed learning direction; exact criteria and edit workflow remain open |
| DD-011 | Refresh this existing draft while leaving Method 6 incomplete | Explicit user authorization on 2026-11-11; no validated DT exit, PRD sign-off, or implementation approval |

## Product Goals

| ID | Goal | Priority | Observable success evidence |
|---|---|---|---|
| GOAL-001 | Explain and use repeatable evaluation for customer quality decisions | MUST | First-run explanation, case-level interpretation, and a justified quality decision |
| GOAL-002 | Investigate and improve agent quality through development and production practice | MUST | Verified improvement in at least one aspect and a live-activity investigation |
| GOAL-003 | Transfer reusable evaluation capability into delivery, handover, and optional automation | MUST | Reusable assets/process instructions and a runnable optional GitHub Actions exercise |
| GOAL-004 | Use Microsoft Foundry evaluation features and communicate their value and limits in customer solutions | MUST | Actual Foundry evaluation evidence linked to a clear feature/value explanation, without a required third-party evaluation platform |

SMART assessment is deferred. Baselines, cohort success targets, measurement ownership, and release horizon must be agreed before approval. Do not invent completion rates or customer sales uplift.

## Functional Requirements

Statements below capture agreed capabilities. Acceptance detail is proposed for review. MUST means required in the delivered track; SHOULD marks a secondary activity, not a primary-completion gate.

| ID | Requirement | Priority | Actor, trigger, and expected outcome |
|---|---|---|---|
| FR-001 | The track shall provide creation of its required agent and assets from the provisioned workshop starting state. | MUST | Learner starts this track without assets from another track; setup prepares its prerequisites |
| FR-002 | The first evaluation exercise shall require an explanation of what evaluation provides and why it matters to a customer and agentic solution. | MUST | Learner completes the first run and explains value and limits |
| FR-003 | The track shall provide an early, repeatable local development evaluation cycle using supplied scripts to assess changes against an explicit non-functional quality requirement. | MUST | Learner links a requirement to criteria, records a baseline, and reruns checks while building without authoring Python |
| FR-004 | The track shall contrast the selected built-in evaluator results with scenario-specific rubric results. | MUST | Learner compares checks on supplied examples and explains each check's purpose and limits |
| FR-005 | The rubric exercise shall guide learners to a reviewed Foundry-generated rubric based on lab-supplied quality priorities and fictional policy. | MUST | Learner generates a starting rubric, checks its criteria against the supplied priorities, and uses criterion-level results; writing all criteria from scratch is not required |
| FR-006 | The evaluation exercises shall provide representative cases and separate held-back validation cases. | MUST | Learner assesses a change without treating improvement examples as independent validation |
| FR-007 | The improvement exercise shall require verification of at least one quality change against a recorded baseline. | MUST | Learner changes an aspect and uses comparable evidence to determine the effect |
| FR-008 | The decision exercise shall require a justified change or release recommendation based on evaluation evidence and its limits. | MUST | Learner recommends proceeding or retaining the baseline; neither outcome is forced |
| FR-009 | The core production exercise shall evaluate synthetic live activity from the deployed lab agent. | MUST | Learner produces lab activity and obtains evaluation evidence, without customer production access |
| FR-010 | The core production exercise shall require investigation of a quality failure through its supporting conversation or trace. | MUST | Learner connects a failure to evidence and explains what needs investigation |
| FR-011 | The track shall provide a repeatable operational evaluation process for regular production use. | MUST | Learner can describe how future runs and failure review fit operating practice; mechanism remains open |
| FR-012 | The handover guidance shall provide reusable evaluation assets and processes for a successor team. | MUST | Customer, internal team, or another partner can identify how to rerun and maintain the checks |
| FR-013 | Readiness reporting shall distinguish completed, blocked, unverified, and failed activities with a reason and next action where applicable. | MUST | A prerequisite is checked or an activity runs; learner sees the actual state rather than a success-shaped skip |
| FR-014 | Primary completion shall remain available when deployment conditions block secondary Optimizer or red-team activities. | MUST | Learner completes actual core evaluation work without needing a secondary result |
| FR-015 | Where supported, the track shall provide an Agent Optimizer exercise comparing runtime cost and quality evidence. | SHOULD | Learner evaluates candidates; baseline quality is preserved unless an explicit customer exception is recorded |
| FR-016 | Where supported, the track shall provide a controlled hands-on red-team exercise with explicit coverage limits. | SHOULD | Learner runs authorized synthetic testing and interprets findings without claiming backend security |
| FR-017 | The optional CI/CD module shall provide a real repository GitHub Actions workflow evaluating the lab-deployed agent. | MUST, optional learner participation | Learner forks, configures settings and access, then runs the workflow against an existing deployment |
| FR-018 | Setup shall use maintained track requirements and report module-specific environment limitations. | MUST | Individual or organizer prepares selected tracks; supported work remains available without silent region changes |
| FR-019 | Core exercises shall provide hands-on use of Microsoft Foundry evaluation features and require learners to explain their role, value, and limits in a solution without requiring a third-party evaluation platform. | MUST | Partner engineer, consultant, or architect connects actual feature use and results to a customer quality need |
| FR-020 | The introductory evaluation exercise shall identify supplied answers and explain why they are used. | MUST | Learner uses labelled acceptable/unacceptable examples without mistaking them for newly generated live-agent evidence |
| FR-021 | The rubric-change exercise shall require learners to incorporate and test one lab-supplied additional quality requirement. | MUST | Learner revises the rubric and explains its effect on measurement, separately from any agent change |
| FR-022 | The core journey shall include a completed simple built-in evaluation and result review before rubric generation. | MUST | Learner inspects actual scores and explanations before generating the domain rubric |

Acceptance and goal links for every requirement are maintained in the Traceability Matrix.

## Non-Functional Requirements

These are proposed verifiable quality conditions for the draft, not claims that the current repository satisfies them.

### Performance and Capacity

NFR-001: Before an exercise starts paid work, instructions shall identify its cost drivers and bounded run/sample settings. Design the required lab for less than 120 minutes elapsed learner time, including the agent readiness check, expected waits, and contingency. Infrastructure provisioning is required pre-work and does not count against this session target. Detailed timing requires validation; numeric spend and individual job-runtime budgets remain open.

### Reliability and Resilience

NFR-002: Execution errors shall be reported as failures. Unknown support shall remain unverified. A primary-path failure shall not be hidden by secondary skip handling.

### Security

NFR-003: The core agent shall expose only the approved read-only tools; submitting bookings or claims shall not be available through that tool configuration.

NFR-004: Credentials shall not be stored in tracked files or workflow artifacts. Runtime configuration shall use approved environment or identity mechanisms. Exact evaluation roles require verification.

### Privacy

NFR-005: Workshop activity shall use synthetic passenger data. Repository research notes shall omit practitioner and company names. Real customer conversations are not required.

### Scalability and Elasticity

No numeric concurrency target is agreed. Shared organizer operation must be assessed before approval; this is a retained capacity gap, not an unlimited scaling requirement.

### Maintainability and Operability

NFR-006: Comparison records shall identify the agent version, actual model identity/version, dataset, evaluator/rubric configuration, and relevant tool configuration used. Agent-change comparisons shall keep the dataset, rubric, and judge settings fixed. Any other changed setting shall be disclosed so that the comparison does not imply an isolated agent effect.

NFR-007: New environment settings shall be reflected in the canonical `shared/.env.example` and setup generation or derivation path. Reprovisioning must not depend on preserving undocumented manual edits.

### Observability

NFR-008: Production exercise evidence shall support navigation from a quality result to its conversation or trace without exposing credentials. Exact telemetry schema, sampling, retention, and detection latency remain open.

### Usability and Accessibility

NFR-009: Core exercises shall be completable without Python authoring or CI-platform setup. Supplied code remains visible to engineers.

NFR-010: New instructional assets shall use clear headings, descriptive links, and text alternatives for informative images. Any new custom interactive surface shall target WCAG 2.2 AA and require manual review; no accessibility certification is claimed.

### Compatibility and Interoperability

NFR-011: The selected SDK, judge model, agent message/tool-result shape, identity permissions, and evaluator mappings shall be verified together before a supported path is documented as runnable.

### Portability

NFR-012: Tracked artifacts shall not contain device-specific paths, internal package feeds, or credentials. Local package managers select their configured sources.

## Constraints

| ID | Boundary | Imposing source | Category and impact |
|---|---|---|---|
| CON-001 | Preserve introduction numbering and existing learner paths | Requester and repository conventions | Organizational; separate track rather than renumbering |
| CON-002 | No previous track completion or Python authoring | Requester | Scope; supplied setup and scripts required |
| CON-003 | Fictional policy, synthetic activity, read-only advice; no legal-entitlement advice | Requester | Operational; no production airline or customer system required |
| CON-004 | Reuse existing provisioning in individual and organizer modes | Requester | Technical; avoid a separate deployment system |
| CON-005 | Recommend East US 2 for new environments while preserving explicit choices and existing regions | Requester | Technical; module warnings instead of automatic relocation |
| CON-006 | CI/CD is optional extra credit; production evaluation is hands-on core | Requester | Scope; no CI dependency for production learning |
| CON-007 | Do not run paid jobs just to determine readiness | Requester | Financial; use known prerequisites and explicit evidence |
| CON-008 | No live jobs, infrastructure changes, access changes, or implementation are authorized by this draft | Current planning authorization | Governance; later execution requires appropriate approval |

These constraints are imposed within this draft's scope. A change requires explicit requester review.

## Acceptance Criteria

All criteria are **Not Started**. Each statement is a proposed test, not a passed result.

| ID | Given / When / Then | Covers |
|---|---|---|
| AC-001 | Given only the documented provisioned workshop starting state, when track setup completes, then all required core agent, tool, policy, and data assets are available without completing another track. | FR-001 |
| AC-002 | Given the first evaluation output, when the learner explains it, then the explanation states what was checked, its customer value, and at least one limit of the evidence. | FR-002 |
| AC-003 | Given the documented local environment and an explicit non-functional quality requirement linked to evaluation criteria before a development change, when the learner runs supplied checks before and after the change without editing Python, then actual case-level results identify its effect against those criteria and support a next development decision without CI/CD setup. | FR-003 |
| AC-004 | Given selected built-in and rubric results for supplied examples, when the learner compares them, then the explanation states what each check measures, what input evidence it uses, and which supplied domain requirement a built-in score alone does not establish. | FR-004 |
| AC-005 | Given supplied quality priorities, fictional policy, and labelled answers, when the learner generates and reviews a rubric in Foundry, then they identify how its criteria cover the supplied priorities, refine gaps or explain why no refinement is needed, and use criterion-level scores and reasons to explain a judgment. | FR-005 |
| AC-006 | Given improvement and held-back case sets, when the learner validates a change, then the validation evidence identifies the held-back set separately. | FR-006 |
| AC-007 | Given a baseline and a changed configuration, when comparable evaluations run, then the learner demonstrates at least one improved quality aspect and records any regressions. | FR-007 |
| AC-008 | Given case-level results and agreed gates, when a recommendation is made, then it cites evidence, limitations, and critical failures; an average does not silently override a designated critical failure. | FR-008 |
| AC-009 | Given a deployed lab agent and synthetic passenger requests, when live activity is generated and evaluated, then a completed evaluation result is linked to that activity rather than only to prerecorded answers. | FR-009 |
| AC-010 | Given a known quality failure in evaluated live activity, when the learner investigates, then they locate supporting conversation or trace evidence and explain a next investigation step. | FR-010 |
| AC-011 | Given the operational exercise, when the learner follows its repeat-run process, then a subsequent evaluation can be performed without completing the optional GitHub Actions module. Cadence and automation mechanism require design review. | FR-011 |
| AC-012 | Given the handover assets, when a successor follows the instructions, then they can identify how to run checks, interpret failures, maintain cases/criteria, and record gate decisions without undocumented project-team knowledge. | FR-012 |
| AC-013 | Given a supported, blocked, unknown, or failed activity, when its status is reported, then the reported state matches evidence and names the reason and next action for incomplete work. | FR-013 |
| AC-014 | Given an evidenced deployment block to Optimizer or red teaming, when the learner completes the primary exercises, then primary completion does not require the blocked activity or describe it as executed. | FR-014 |
| AC-015 | Given a supported Optimizer environment, when candidates are compared, then evidence separates optimization-job costs from selected-agent runtime cost and records quality checks and any explicit exception. | FR-015 |
| AC-016 | Given a supported and authorized red-team environment, when a run completes, then the learner reviews findings and skipped coverage separately and does not infer tool-backend security from scan completion. | FR-016 |
| AC-017 | Given a fork, configured access/settings, and an existing lab-deployed agent, when the optional evaluation workflow is invoked, then it produces real evaluation evidence and a gate outcome without provisioning or deleting the lab environment. | FR-017 |
| AC-018 | Given selected tracks in individual or organizer mode, when setup resolves requirements, then it preserves explicit configuration and reports unsupported modules without removing unrelated supported work. | FR-018 |
| AC-019 | Given completed core exercises using Microsoft Foundry, when the learner explains the solution to a customer or delivery team, then they identify the Foundry evaluation features actually used, link their results to a quality need, and state relevant limits; core completion requires no third-party evaluation platform account or deployment. | FR-019 |
| AC-020 | Given the introductory answers and instructions, when the learner runs their evaluation, then the answers are labelled as supplied examples, the instructions explain why a fresh agent mistake is not required for this exercise, and the results are not reported as newly generated live-agent evidence. | FR-020 |
| AC-021 | Given an initial rubric and one supplied additional quality requirement, when the learner revises and evaluates the rubric, then the revised criteria represent that requirement and the learner explains what changed in measurement without claiming that a score difference proves an agent improvement. | FR-021 |
| AC-022 | Given the documented core path, when the learner follows it, then they complete a real simple built-in evaluation and inspect its scores, explanations, and limits before starting rubric generation. | FR-022 |

## Traceability Matrix

Source codes below identify supporting artifacts, not independent evidence counts.

| Code | Source | Authority and limit |
|---|---|---|
| S1 | [Working plan](implementation-plan.md) and [coaching state](coaching-state.md) | Requester scope and history; the later recorded decisions take precedence over older proposals |
| S2 | [Anonymous practitioner evidence](method-03-synthesis/practitioner-evidence.md) | Two requester-supplied perspectives, not population-level evidence |
| S3 | [Synthesis insights](method-03-synthesis/insight-statements.md) and [problem definition](method-03-synthesis/problem-definition.md) | Bounded working baseline, not fully validated synthesis |
| S4 | [Evaluator fit notes](method-03-synthesis/affinity-clusters.md) | Documentation-based suitability, not live verification |
| S5 | [Selected-concept handoff](method-05-user-concepts/method-06-handoff.md) | Requester-selected journey with explicit Method 5 limits |
| S6 | [Requester feedback and corrections](method-05-user-concepts/stakeholder-alignment.md) | Chronological decisions; later corrections supersede earlier suggestions |
| S7 | [Method 6 prototype plan](method-06-lofi-prototypes/prototype-plan.md) | Planned clarity tests, no observations or validated solution exit |
| S8 | [Official rubric guidance](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators) | Rechecked on 2026-11-11; supports generation and human refinement, not this lab's integrated feasibility |

### Feasibility Candidate Disposition

Not applicable: no formal feasibility-to-PRD handoff was consumed. Technical proposals remain retained gaps, not accepted feasibility verdicts.

### FR-to-AC Coverage

| Requirement | Acceptance | Count | Source |
|---|---|---|---|
| FR-001 | AC-001 | 1 | S1 |
| FR-002 | AC-002 | 1 | S1, S3 |
| FR-003 | AC-003 | 1 | S1 |
| FR-004 | AC-004 | 1 | S1, S4, S5 |
| FR-005 | AC-005 | 1 | S1, S5, S6, S8 |
| FR-006 | AC-006 | 1 | S1 |
| FR-007 | AC-007 | 1 | S1 |
| FR-008 | AC-008 | 1 | S1, S3 |
| FR-009 | AC-009 | 1 | S1 |
| FR-010 | AC-010 | 1 | S1, S3 |
| FR-011 | AC-011 | 1 | S1 |
| FR-012 | AC-012 | 1 | S1, S2, S3 |
| FR-013 | AC-013 | 1 | S1 |
| FR-014 | AC-014 | 1 | S1 |
| FR-015 | AC-015 | 1 | S1 |
| FR-016 | AC-016 | 1 | S1 |
| FR-017 | AC-017 | 1 | S1 |
| FR-018 | AC-018 | 1 | S1 |
| FR-019 | AC-019 | 1 | S1, S3 |
| FR-020 | AC-020 | 1 | S5, S6 |
| FR-021 | AC-021 | 1 | S5, S6 |
| FR-022 | AC-022 | 1 | S5, S6 |

Coverage: 22/22 requirements have acceptance links (100%). This is document coverage, not execution evidence or proof of requirement quality.

### FR-to-GOAL Alignment

| Requirement | Product goal | Count |
|---|---|---|
| FR-001 | GOAL-001 | 1 |
| FR-002 | GOAL-001 | 1 |
| FR-003 | GOAL-001 | 1 |
| FR-004 | GOAL-001 | 1 |
| FR-005 | GOAL-001 | 1 |
| FR-006 | GOAL-002 | 1 |
| FR-007 | GOAL-002 | 1 |
| FR-008 | GOAL-001 | 1 |
| FR-009 | GOAL-002 | 1 |
| FR-010 | GOAL-002 | 1 |
| FR-011 | GOAL-003 | 1 |
| FR-012 | GOAL-003 | 1 |
| FR-013 | GOAL-001 | 1 |
| FR-014 | GOAL-001 | 1 |
| FR-015 | GOAL-002 | 1 |
| FR-016 | GOAL-002 | 1 |
| FR-017 | GOAL-003 | 1 |
| FR-018 | GOAL-003 | 1 |
| FR-019 | GOAL-004 | 1 |
| FR-020 | GOAL-001 | 1 |
| FR-021 | GOAL-001 | 1 |
| FR-022 | GOAL-004 | 1 |

Alignment: 22/22 requirements have goal links (100%). No coverage waiver is requested.

## MVP and Release Framing

Core: FR-001 through FR-014 and FR-018 through FR-022. Include the built-in-first opening, guided rubric generation and revision, local evaluation, live-agent improvement, evidence-based decisions, hands-on production investigation, and reusable process guidance. Explicitly teach the Microsoft Foundry features used and their solution value, without a required third-party evaluation platform. Preserve the workshop's Python-first flow and support individual and facilitated use.

Secondary: FR-015 and FR-016. Include practical instructions for supported environments and actionable incomplete states elsewhere. Their successful execution is not required for primary completion.

Optional learner extension: FR-017. The delivered track includes a real workflow and extra-credit module; the learner does not need to fork or configure CI/CD to complete the core.

Not in scope: production airline functionality, legal-entitlement guidance, booking or claim execution, exhaustive evaluator coverage, a required Azure DevOps implementation, customer production access, or mandatory execution of all secondary features.

### Selected core learning journey

This sequence is requester-selected learning intent. It is not a fixed module structure, verified portal procedure, or measured schedule.

| Stage | Learner action | Required evidence | Requirements |
|---|---|---|---|
| Ready | Check the provisioned environment and locate the supplied assets | Actual readiness state and activity-specific limits | FR-001, FR-013, FR-018 |
| Run | Run a simple built-in evaluator on labelled supplied answers | Real Foundry result, with example provenance and purpose | FR-020, FR-022 |
| Understand | Inspect scores and explanations before rubric generation | Explanation of what the check establishes and what it leaves open | FR-002, FR-022 |
| Generate and review | Generate a rubric from supplied priorities and policy; review its criteria | Reviewed criteria and rubric results compared with built-ins | FR-004, FR-005 |
| Customize | Add one supplied requirement and test a revised rubric | Revised criteria and explanation of changed measurement | FR-021 |
| Improve | Evaluate a live agent, make a guided change, and rerun checks with held-back validation | Comparable live-agent evidence of at least one quality improvement and any regressions | FR-003, FR-006, FR-007, FR-008 |
| Investigate | Evaluate synthetic live deployed-agent activity and inspect a quality failure | Result linked to supporting conversation or trace and a next investigation step | FR-009, FR-010, FR-011 |
| Explain and reuse | Explain the feature value, limits, and repeat-run process | Reasoned decision and reusable lab evaluation assets | FR-012, FR-019 |

Supplied priorities reduce domain-discovery work; they do not remove human review of generated criteria. A hosted-agent description must not be assumed to contain internal code or all quality priorities. Supply explicit context when needed. Official generation support is documented in S8; the selected lab path still requires verification.

The saved-answer opening makes inputs available for introductory practice. It does not make model-judge scores deterministic. Do not promise that built-ins will accept an unacceptable answer, that a rubric will disagree with a built-in, or that a new requirement will change every score. Do not retry until a desired failure appears, alter thresholds just to force a lesson, or silently substitute saved evidence for live work.

**Recommendation, not an accepted exercise detail:** Score unchanged supplied answers under both rubric versions, with the same judge settings. This can help separate changed measurement from agent behavior. Record the actual rubric and settings in either design. A rubric change is not an agent improvement. Weighted averages do not automatically enforce critical-failure gates. Small case sets do not establish population-level performance, and evaluations do not replace integration, load, or security testing.

Exact evaluator selection, the supplied additional requirement, module count and titles, execution surfaces, and time allocations remain open. Relevance, Groundedness, Tool Call Accuracy, and Tool Output Utilization are candidate examples, not a mandated evaluator list. Select representative quality and agent checks only after their input needs and learning fit are verified. Groundedness checks support in supplied context, not independent truth; tool-use checks need the relevant interaction evidence.

The earlier implementation plan's module structure and the 119-minute activity budget remain proposals. Provisioning is required pre-work; the agent readiness check, evaluation waits, and contingency count toward the less-than-120-minute core. Proposed optional-depth cuts are not approval to remove Optimizer, red teaming, or the GitHub Actions deliverable.

## Success Metrics

| Goal | Candidate measurement | Baseline and target | Window and source |
|---|---|---|---|
| GOAL-001 | Learners who can explain evaluation value/limits and justify a result-based decision | Unknown; target requires requester agreement | Representative learner walkthrough and explanation review; timing open |
| GOAL-002 | Learners who verify one quality improvement and investigate one live-activity failure | Unknown; per-learner evidence defined by AC-007 and AC-010, cohort target open | Prototype/user-test results and learner evidence |
| GOAL-003 | Successor can repeat the supplied process; optional workflow executes against an existing deployment | Unknown; no measured handover result | Handover walkthrough and optional workflow evidence |
| GOAL-004 | Learners who can use Foundry evaluation features and explain their value and limits for a customer quality need | Unknown; proposed per-learner evidence in AC-019, cohort target open | Hands-on results and learner explanation review |

Do not treat satisfaction with the lab idea as measured capability gain. No claim is made about increased sales or production incident reduction.

## Risks and Assumptions

### Key Assumptions

| ID | Assumption | Evidence status | Impact if false | Mitigation | Source |
|---|---|---|---|---|---|
| A-001 | Intended learners may have limited practical evaluation experience | Partially supported, not population-validated | Wrong pace or prerequisites | Representative learner review | S1, S2 |
| A-002 | The flight scenario makes evaluation differences understandable | Untested | Domain detail distracts from learning | Fixed, reviewed fixtures and early example walkthrough | S1, S4 |
| A-003 | A supplied Python hosted agent can support the primary path | Untested end to end | Core path may require redesign | Verify runtime, SDK, tools, identity, and judge together | S1 |
| A-004 | Production evaluation can yield actionable evidence within a workshop session | Untested | Core exercise stalls or cannot be completed | Measure latency and verify result-to-conversation/trace navigation | S1 |
| A-005 | The built-in-first journey makes the distinction between general checks and domain criteria understandable | Requester-selected, learner understanding untested | Learners follow steps without understanding the evidence | Method 6 rough walkthrough and later representative learner testing | S5, S7 |
| A-006 | All required core work fits below 120 minutes after provisioning pre-work | Untested; proposed budget only | Required outcomes cannot fit the session | Timed end-to-end walkthrough with expected waits and contingency; review scope with requester | S1, S5 |

### Research Finding Dispositions

No formal bounded RPI research report was consumed. Contextual findings are handled as follows:

| Finding | Disposition | Affected scope | Limit |
|---|---|---|---|
| Two differing practitioner approaches and prompted interest in formal learning | Incorporated as limited problem evidence | GOAL-001, GOAL-003 | No industry-wide maturity or customer-value claim |
| Documented evaluator definitions match proposed examples | Retained suitability assumption pending live test | FR-004, FR-005 | No scored fixtures verified |
| Existing flight/knowledge assets are not an aligned fictional-policy evaluation dataset | Incorporated as setup work | FR-001, FR-006 | Do not reuse rights content unchanged or include claim tool |
| Existing workflow patterns provide authentication and artifact examples | Retained design input | FR-017 | Not proof of sufficient Foundry permissions or safe fork operation |
| Requester selected Run Understand Customize and supplied-answer introductory practice | Incorporated as learning-design decisions | FR-004, FR-005, FR-020, FR-021, FR-022 | Not evidence of comprehension, reliable score contrasts, or completion time |
| Official guidance supports rubric generation followed by review and refinement | Incorporated as the guided rubric approach | FR-005 | Hosted context and complete input mappings still need verification |
| Method 6 contains a plan but no test observations | Retained validation gap | A-005, Sign-Off | No concept-validated Solution Space exit or implementation readiness |

### Risk Register

| ID | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| R-001 | Judge scores do not distinguish intended failures reliably | Unknown | High | Compare known good/bad cases and rubric revisions; inspect reasons and criterion scores |
| R-002 | Hosted runtime, SDK, permissions, or tool mappings block core evaluation | Unknown | High | Small integrated technical test before documenting a runnable path |
| R-003 | Production evaluation delay, trace availability, or permissions prevent the core investigation | Unknown | High | Verify live activity scoring and navigation; do not silently substitute prerecorded-only evidence |
| R-004 | Optimizer access or remote MCP red-team coverage differs by environment | Unknown | Medium for secondary scope | Explicit readiness and coverage reports; preserve primary completion |
| R-005 | Forked CI setup exposes credentials, permits unintended paid triggers, or targets shared resources incorrectly | Unknown | High | Review identity scope, triggers, inputs, artifacts, and run limits before enabling |
| R-006 | Scope exceeds available workshop time or budget | Unknown | High | Keep the core below 120 minutes after provisioning pre-work; validate elapsed timing, agree spend limits, and separate optional execution without dropping core outcomes |

### Open Decisions and Verification

| ID | Question or test | Required before |
|---|---|---|
| Q-001 | Detailed pacing below 120 minutes after provisioning pre-work, meaning of approximately 80% feature coverage, expected learner cohort, spend limits, and release horizon | Baseline approval and module sizing |
| Q-002 | Hosted-agent implementation, SDK version, supported model roles, quota, runtime/tool identity | Primary-path implementation commitment |
| Q-003 | Production evaluation mechanism, repeat cadence, sampling, retention, latency, and navigation | Production module implementation and live verification |
| Q-004 | Supplied-answer fixtures, the additional quality requirement, rubric criteria, thresholds, critical-failure gates, and judge calibration | Claiming evaluator-example reliability |
| Q-005 | Optimizer access and actual applied configuration, runtime cost measurement | Claiming secondary exercise support |
| Q-006 | Ordinary agent scan support versus tool-mediated coverage for custom MCP | Claiming red-team coverage; backend security remains separate |
| Q-007 | Fork onboarding, identity setup, variables/secrets, safe triggers, shared-environment target, and gate exit behavior | Optional workflow implementation |
| Q-008 | Maintainer, technical, quality, and representative learner review ownership | PRD approval |
| Q-009 | Exact first built-in evaluator and representative quality/agent checks, required input evidence, and portal versus supplied-script steps | Runnable exercise instructions |
| Q-010 | Learner comprehension and independent review of the selected journey, including whether to resume the incomplete Method 6 tests | Claiming learning-design validation |

Plan the small live evaluator comparison in Method 7 technical feasibility work, or an explicitly approved bounded research test if needed earlier. Method 6 can review the clarity of examples; Method 8 tests learner use. None is authorized by writing this draft.

### Required validation evidence

All rows below are pending. Suggested review roles are not confirmed assignments. These evidence needs are not permission to run cloud work.

| Area | Evidence needed | Intended review role | Current limit |
|---|---|---|---|
| Opening comprehension | Observed explanation of built-in versus domain checks using a rough walkthrough | Representative learner and facilitator | Method 6 incomplete; no participants or observations |
| Primary-path feasibility | Integrated built-in/rubric runs, input mappings, live-agent change, and a production result linked to supporting evidence | Technical reviewer | Documentation reviewed; no integrated test |
| Timing and cost | Full core elapsed time, waits and contingency, bounded sample sizes, runtime/evaluation cost drivers, and agreed spend limits | Maintainer and requester | Proposed 119 minutes only; spend cap unknown |
| Requirement quality | Formal standard findings and quality report, with findings resolved or retained as blockers | PRD quality reviewer | Validate not entered; no report or gate clearance |
| Scope and accountability | Accepted detailed scope cuts, feature-coverage denominator, release horizon, review owners, and acceptance detail | Requester and maintainer | Decisions remain open; no PRD sign-off |

## Glossary

| Term | Meaning in this PRD |
|---|---|
| Evaluation | A check of agent behavior against defined expectations using supplied evidence |
| Rubric | Explicit quality criteria scored by a judge, with reasons and possible weights |
| Quality gate | An agreed rule for deciding whether evidence is acceptable for a particular action |
| Production evaluation | Evaluation of live deployed lab-agent activity, using synthetic requests here |
| Handover | Transfer of reusable assets and processes to the team responsible for subsequent work |
| Secondary activity | Optimizer or red teaming; support may be limited without blocking primary completion |

## Sign-Off

### Approval Checklist

- [ ] Requester reviews the consolidated scope and proposed acceptance detail.
- [ ] Maintainer confirms fit with repository structure and delivery capacity.
- [ ] Technical reviewer verifies primary-path feasibility and dispositions secondary limitations.
- [ ] Quality reviewer assesses requirement quality and representative learner evidence.
- [ ] Privacy and safety review confirms synthetic-data, read-only, and artifact boundaries.

No document approval or approval date is recorded. User permission to draft is not final sign-off.

### Waivers

None granted. Evidence gaps are recorded, not waived or reported as validated.

### Handoff Readiness

Draft only. The 2026-11-11 authorization permits PRD refinement while Method 6 stays incomplete. This draft can support requirements discussion; it is not a validated Solution Space exit or an approved implementation baseline. Formal PRD quality-review payloads and Validate/Finalize gates have not been completed. No approved release hash or implementation handoff is issued. All acceptance tests remain unexecuted.

## Disclaimer

This planning draft uses limited practitioner evidence and unverified technical assumptions. It is not approval to deploy, spend, change permissions, or release a production solution. Supplied fictional policy is not legal advice.

> [!CAUTION]
> **Disclaimer:** This agent is an assistive tool only. It does not provide product management approval, technical feasibility validation, or business sign-off and does not replace product managers, engineering leads, business stakeholders, or other qualified human reviewers. The output consists of suggested requirements, acceptance criteria, and product specifications to support a user's own product planning and decision-making. All Product Requirements Documents, functional requirements, non-functional requirements, and constraint definitions generated by this tool must be independently reviewed and validated by appropriate product and engineering reviewers before adoption. Outputs from this tool do not constitute product approval, requirements sign-off, or engineering commitment.

## Document Metadata

- Template Version: 1.0.0.
- Canonical Template: `requirements-author/templates/prd/prd-full.md`.
- License: CC-BY 4.0 (Microsoft HVE-Core).
- Attribution: Microsoft HVE-Core Team.
- Source synthesis: [insights](method-03-synthesis/insight-statements.md), [problem definition](method-03-synthesis/problem-definition.md), and [how-might-we questions](method-03-synthesis/how-might-we-questions.md).
- Revision 0.2.0: integrated Method 5 selection and later requester corrections on 2026-11-11. Existing IDs are preserved. Added FR-020 through FR-022 and AC-020 through AC-022; all acceptance statuses remain Not Started.
- PRD session state: [builder state](../../prd-sessions/foundry-evaluation-learning.state.json) and [local authoring summary](prd-state.md). The existing PRD path is retained to preserve DT evidence links.
