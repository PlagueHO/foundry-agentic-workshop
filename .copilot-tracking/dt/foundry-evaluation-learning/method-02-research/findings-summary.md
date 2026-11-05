# Method 2 findings summary

## Status and evidence boundary

The user accepted these Method 2 outputs as sufficient to start Method 3. This summary consolidates the requester's decisions, repository observations, and documented technical constraints. It does not establish validated partner needs, measured learning outcomes, or a working end-to-end lab.

After Method 3 began, the requester supplied two practitioner conversation excerpts. Anonymous evidence and the user-approved gap are recorded in `..\method-03-synthesis\practitioner-evidence.md`. No observed learner sessions or direct customer evidence are recorded.

## Current learning priorities

The user's latest direction supersedes the earlier requirement that every learner must execute Optimizer and red-team exercises to complete the core:

> The primary goal is learning to use/run evals. Secondary is Agent Optimizer and red-team evals. So, as long as we can achieve primary, but can tell the lab user when secondaries are blocked because of some lab deployment condition then I think this is ok

- Primary: learn to use and run evaluations. Retain the agreed evaluation interpretation, rubric creation, failure investigation, and quality-improvement goals.
- Secondary: use Agent Optimizer and run red-team evaluations when the environment supports them. These remain planned learning activities, not removed content.
- A blocked secondary activity must identify the condition and a useful next action. It must not block primary completion or be reported as successfully executed.
- Completion reporting must separate primary outcomes from each secondary activity's completed, blocked, unverified, or failed state.
- An unknown capability is unverified, not automatically unsupported. An execution error is a failure, not automatically a deployment limitation.

## Evidence and confidence

Confidence describes the evidence available, not a measured probability.

| Area | Evidence and source | Confidence | Limit |
|---|---|---|---|
| Learning intent | Requester quotations and decisions in `..\coaching-state.md` | High for requester intent | Does not establish partner skill gaps |
| Learner prerequisites | Basic Foundry knowledge; no prior track completion; supplied Python permitted | High for agreed boundaries | Practical evaluation experience is assumed limited, not observed |
| Scenario | Passenger-facing flight disruption, read-only tools, fictional airline policy; legal advice excluded | High for selected direction | Teaching effectiveness is not tested |
| Deployment context | Wizard, Bicep profiles, quota checks, identity preparation, hooks, and onboarding inspected | High for inspected repository behavior | Proposed multi-track changes are not implemented or tested |
| Reusable flight assets | MCP exposes status and rebooking-option lookups; claim submission is outside scope | High for code observations | Fixtures need a fixed clock and review; booking ownership and eligibility are not validated |
| Evaluation and rubric path | Official evaluation and rubric guidance reviewed | Moderate for the proposed complete path | Intended SDK, judge, permissions, data shape, and hosted runtime need verification together |
| Optimizer | Hosted workflow documented; access guidance differs across pages | Moderate for documented capability | Actual subscription access and complete integration are unverified |
| Red-team execution and coverage | Hosted targets documented; custom remote MCP handling remains unclear | Partial | Basic agent scans, tool-mediated coverage, and backend security must remain distinct |
| Partner workflows and learner difficulty | Two requester-supplied practitioner excerpts, summarized in Method 3 | Limited practitioner evidence | Differing reported practices; no inspected suites, observed learners, or direct customer evidence |

Detailed evidence and official references are in `constraint-catalog.md`. Older ACL and prompt-agent observations are research history, not current scenario choices.

## Established constraints

- Reuse workshop provisioning and support independent and organizer-led use.
- Do not assume another lab has created the agent, knowledge assets, or connections.
- Keep core completion possible without Python authoring.
- Keep track requirements data driven and maintained; support multiple selected tracks if setup stays simple.
- Recommend East US 2 for new environments while preserving explicit regions and existing deployments.
- Report module-specific limitations without relocating resources or blocking unrelated exercises.
- Do not start paid jobs merely to determine readiness.
- Keep model identity, versions, evaluator configuration, datasets, and tool configuration visible in comparisons.

## Assumptions and deferred evidence

| Assumption or question | Current status | Revisit trigger |
|---|---|---|
| Intended learners have little practical evaluation experience | Working assumption; requester is checking | Partner reply or practitioner access |
| Evaluation evidence improves customer confidence or sales decisions | Requester hypothesis, not a causal finding | Concrete project example |
| Flight is an effective teaching scenario | Selected working scenario, not validated learning evidence | Representative learner walkthrough |
| A supplied Python hosted agent keeps mechanics manageable | Preferred technical direction | Authorized feasibility work and learner feedback |
| Post-handover users can interpret results and identify next actions | Desired outcome | Operator or learner walkthrough |

Practitioner input now partly addresses the deferred research. Wider validation remains open. Do not infer a general lack of evaluation capability from the two excerpts.

## Later verification gates

These are verification objectives, not authorization to implement or run cloud jobs.

| Gate | Evidence needed | Effect if unresolved |
|---|---|---|
| Primary evaluation path | Supplied setup creates the needed assets; an evaluation runs and produces interpretable per-case results with the intended agent, tools, judge, and permissions | Primary completion cannot be claimed |
| Rubric learning | Learner creates or revises a rubric, inspects criterion-level results, and can explain a failure and an improvement | Core rubric outcome remains unverified |
| Optimizer exercise | Candidate configuration is actually applied; quality and cost evidence can be compared under approved settings | Mark the secondary activity blocked, unverified, or failed as appropriate; retain primary access |
| Red-team exercise | Verify agent acceptance separately from the supported risk categories and tool-mediated coverage; inspect scored results and exclusions | Report the specific secondary limitation; do not claim full coverage or backend security |
| Readiness reporting | Catalog evidence and observed prerequisites produce explicit, actionable activity statuses in individual and organizer modes | Do not promise that secondary activities will run |

## Remaining design decisions

Detailed flight tasks, fictional policy text, rubric criteria, acceptance thresholds, module order, runtime-cost method, and operational automation depth remain open. These are not all missing research findings; some belong to later design and feasibility work.

## Method 2 assessment

The user approved starting Method 3 using the recorded scope and environmental evidence with explicit assumptions. We do not have validated learner needs or a proven implementation. Approval to synthesize does not authorize implementation or declare the research gaps resolved.
