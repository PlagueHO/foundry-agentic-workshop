# PRD authoring state

```yaml
prd_id: "PRD-FOUNDRY-EVALUATION-LEARNING"
artifact: ".copilot-tracking/dt/foundry-evaluation-learning/prd.md"
status: "draft"
version: "0.2.1"
phase: "build"
builder_session_state: ".copilot-tracking/prd-sessions/foundry-evaluation-learning.state.json"
last_updated: "2026-11-11"
disclaimerShownAt: "2026-11-11T15:42:34.5639260+13:00"
phaseSkillsLoaded:
  - "prd-author#assess"
  - "prd-author#discover"
  - "prd-author#create"
  - "prd-author#build"
  - "prd-author#integrate"
created: "2026-11-05"
upstream:
  brdHandoff: null
  feasibilityHandoff: null
  context: "Requester-approved decisions and anonymous DT evidence, not a validated handoff contract."
draft_scope: "Separate evaluation track; explicit Microsoft Foundry hands-on capability and product-value awareness; no required third-party evaluation platform for core completion; core production evaluation; optional GitHub Actions; conditional secondary Optimizer and red teaming."
selected_journey: "Run Understand Customize: actual simple built-in run and result review before rubric generation from supplied priorities/policy, comparison, and revision against one supplied new requirement; separate live-agent improvement and production investigation."
design_evidence: "Requester selected the concept with bounded Method 5 closure. Method 6 remains incomplete; no prototypes built or tested, participants confirmed, or learner observations. This authoring transfer is not a validated DT/RPI handoff or implementation approval."
documentation_alignment: "CON-009: Current official Microsoft documentation for Foundry, evaluations/evaluators, Agent Optimizer, AI Red Teaming Agent, and related capabilities used MUST be consulted throughout Research, Plan, Implement, and review. Record source URLs/sections, dates checked, applicable versions/support limits, and unresolved differences. Recheck at phase transitions and before release. Documentation is not live feasibility evidence."
document_counts:
  functional_requirements: 22
  acceptance_criteria: 22
  product_goals: 4
  non_functional_requirements: 12
  constraints: 9
review:
  acceptance_detail: "proposed, requester review pending"
  acceptance_tests: "Not Started"
  document_checks: "Passed: repository Markdown lint (113 files), explicit hidden planning Markdown lint (27 files), YAML/JSON, stable IDs, Given/When/Then shape, 22/22 acceptance and goal links, local paths/links, cross-state consistency, portability, and git diff --check. Author checks only, not formal gate clearance."
  tooling: "Direct pnpm unavailable on PATH; pnpm run lint:md passed using cached tools through offline npm execution after checking the effective managed source. No package/dependency configuration changed."
  formal_quality_review: "not run; Validate and Finalize not entered"
  technical_feasibility: "unverified"
  approval: "not requested or granted"
delivery_target:
  session_limit_minutes_exclusive: 120
  source: "Requester confirmed less than two hours after provisioning pre-work on 2026-11-05; not a measured completion time."
  feature_coverage: "Requester aims for approximately 80%; catalogue scope and denominator are not agreed. Do not claim measured coverage."
  proposed_pacing: "105 minutes of readiness, exercises, and review plus 14 minutes contingency; 119 minutes total, unverified."
  provisioning_boundary: "Requester confirmed infrastructure provisioning is pre-work outside the session; agent readiness check remains inside."
  scope_cuts: "Recommended only: merge overlapping core activities and move synthetic generation, conversation-level comparison, clustering, trace-dataset creation, Optimizer, red teaming, and CI/CD execution outside the timed core."
next:
  - "Carry CON-009 into any Development RPI handoff and enforce current Microsoft documentation alignment throughout every stage."
  - "Review draft scope and proposed acceptance detail with requester."
  - "Resolve exact built-in selection and inputs, supplied additional requirement, and rubric edit workflow."
  - "Review proposed cuts and validate elapsed timing below 120 minutes after provisioning pre-work; define coverage scope."
  - "Resolve spend budget, release horizon, and technical/quality review owners."
  - "Retain technical gaps until separately authorized verification provides evidence."
  - "Load PRD quality contracts and dispatch the PRD Quality Reviewer before entering Validate; no formal gate is cleared."
  - "Leave Method 6 incomplete. Resume its tests only when requested."
authorization:
  draft_documents: true
  implementation: false
  cloud_jobs: false
  access_changes: false
  commit_push: true
  commit: true
  push: true
  request: "Ok, you're now the PRD builder - proceed leaving Method 6 incomplete."
  requested_at: "2026-11-11T15:41:15.697+13:00"
  commit_push_request: "Commit all changes and push"
  commit_push_requested_at: "2026-11-11T16:24:57.496+13:00"
  commit_push_scope: "One checkpoint of all current changes on plagueho-foundry-rubric-evaluators. Verify the commit and push in Git. Method 6 remains incomplete; no PR creation, final sign-off, implementation, cloud jobs, or access changes are authorized."
```

Use the [PRD Builder session state](../../prd-sessions/foundry-evaluation-learning.state.json) for PRD recovery. This file keeps the DT-side summary and existing evidence links. Neither state file records formal approval.
