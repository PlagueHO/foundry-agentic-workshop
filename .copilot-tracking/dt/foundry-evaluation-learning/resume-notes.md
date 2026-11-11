# Resume Foundry Evaluation Learning

## Current checkpoint

The user explicitly approved bounded Method 5 closure and progression to Method 6 at 2026-11-07T16:43:57.048+13:00. Methods 1-5 are complete for progression; Method 3 and Method 5 validation limits remain. Run Understand Customize is the selected combined journey: introduce/run a built-in check, inspect results, generate/review a rubric from supplied priorities, evaluate supplied answers, add a supplied requirement, then separate live-agent improvement and production evaluation. Do not repeat the original opening-order choice.

On 2026-11-11 the user explicitly requested: "Ok, you're now the PRD builder - proceed leaving Method 6 incomplete." Current work is PRD Builder, in Build with source integration. Method 6 is paused and incomplete, not passed or replaced by a validated DT/RPI handoff. Its three rough formats have not been built or tested; no participants are confirmed. No new implementation, cloud activity, or PR is authorized.

At 2026-11-11T16:24:57.496+13:00 the user requested: "Commit all changes and push". This authorizes one checkpoint of all current changes on `plagueho-foundry-rubric-evaluators` and its push. Verify the result in Git. It does not approve the PRD, complete Method 6, or grant permission for later commits.

The existing [PRD](prd.md) is now draft 0.2.0 with 22 FRs, 22 ACs, four goals, 12 NFRs, and eight constraints. It records the selected journey, labelled supplied answers and their purpose, generated rubric review from supplied priorities/policy, and testing one supplied new requirement. Live-agent improvement and production investigation remain separate core requirements. Comparing unchanged answers across rubric versions remains a recommendation. All acceptance tests are Not Started. Timing, budget, exact evaluators, the additional requirement, learner understanding, integrated feasibility, review ownership, and final acceptance remain open. Formal Validate/Finalize have not been entered.

Read [PRD Builder state](../../prd-sessions/foundry-evaluation-learning.state.json) for PRD recovery and [legacy state](prd-state.md) for the DT-side summary. The JSON state points to the existing PRD; no duplicate was created in `docs\project-planning`. The PRD disclaimer was displayed and its timestamp persisted. Load `requirements-author` and its Build section before continuing. Review confirmed decisions before asking questions. Load the formal quality contracts and dispatch the PRD Quality Reviewer before entering Validate; document checks alone do not clear that gate.

Four Markdown entries remain under `canonical`. On 2026-11-11 the user rejected the customer-card PowerPoint and requested its removal. The deck, generated slide definitions, and deck validation reports were removed. The user prefers HTML for a future visual summary; no replacement was created. Do not regenerate or re-offer PowerPoint in this DT run.

## Historical context

The paragraphs below preserve earlier decisions and pending states. The current checkpoint and coaching state take precedence where later approvals supersede them.

The user resumed Method 4 on 2026-11-05 from local commit `aba1446` on `plagueho-foundry-rubric-evaluators`. That checkpoint's commit request is complete; it was not pushed. Current work is local coaching only. `method-04-brainstorming\theme-clusters.md` records three learning approaches: see a mismatch, make expectations explicit, and use a controlled change/feedback loop. After challenging live-failure reliability, the user accepted clearly labelled supplied good/bad responses for initial rubric practice, separate from live-agent exercises, with an explanation of why. Do not ask for that decision again. The introductory approach and concept-development transition are accepted, but the complete concept, retained scope, and sequence are not. Live failure/improvement feasibility is still unverified.

The user confirmed infrastructure provisioning as required pre-work excluded from a lab target of less than two hours, with the agent readiness check inside the lab. Do not ask for that boundary again. The draft PRD records this and the requested approximately 80% feature coverage; the feature denominator remains undefined. `method-04-brainstorming\session-notes.md` proposes a 105-minute activity budget plus 14-minute contingency, totaling 119 minutes, and cuts extra generation, multi-turn comparison, clustering, and trace-dataset creation from the timed core. Optimizer, red teaming, and CI/CD are proposed as optional follow-ons, not removed track deliverables. Core live production evaluation is retained. The scope cuts and actual timings are not yet approved/verified.

The latest user correction is explicit: this is a hands-on learning lab like the existing repository labs, not a real customer delivery. The user confirmed continuing with tooling-focused learning. Do not restart the handover-simulation discussion or require customer role-play or agreement meetings. Customer priorities and reusable evaluation assets explain professional value; the learner's practical use of Foundry remains central.

The user then requested suggestions from the Foundry evaluation docs. Nine official pages were read; `method-04-brainstorming\divergent-ideas.md` now contains 15 rough ideas, source links, extensions of existing ideas, and feature/feasibility limits. The user next asked which activities support the desired outcomes. `method-04-brainstorming\session-notes.md` records a proposed six-group core versus optional-depth assessment linked to draft requirements. No selection, cloud verification, fixed module sequence, or Method 5 transition is approved. Do not turn every suggestion into a mandatory feature checklist.

The user explicitly approved bounded Method 3 closure and a cautious move to Method 4: Brainstorming. Methods 1-3 are recorded complete for this design round; Method 3 is not fully validated research. Wider learner/customer/operator validation and live feasibility remain unresolved. The first five ideas included three coach seeds and user ideas about early rubric agreement and implementing rubric changes; the current idea register adds three tooling-focused coach seeds. The user wants practical creation and early agreement to expose customer priorities, support alignment, and help build trust before delivery; these benefits remain unmeasured. Rescoring unchanged responses under both rubric versions is a coach extension, not an agreed design. No idea evaluation or concept selection has occurred. No validated RPI handoff is recorded.

The user subsequently accepted closing the synthesis round as a working design baseline with evidence limits, subject to including delivery engineers and solution architects as equal audiences to consultants. The problem statement and PRD now distinguish these roles. Detailed role-specific problems are working interpretations, not new research findings. Do not treat this bounded agreement as full Method 3 validation or approval of PRD acceptance criteria.

The user clarified the delivery-engineer need: adopt evaluations early and evaluate while building, using a TDD-like feedback cycle to assess changes against non-functional requirements throughout product development. This is confirmed requester intent, not independent research evidence. Draft FR-003/AC-003 now connect a quality requirement, criteria, baseline, repeat local runs, and a development decision. CI/CD remains optional.

The user added an explicit Microsoft product-learning objective: practical use of Foundry evaluation features and the ability to communicate their value and limits in customer solutions. Core completion must not require a third-party evaluation platform. GOAL-004, FR-019, and AC-019 capture this; the draft now has 19 FRs, 19 ACs, and four goals. This does not establish a partner awareness gap or universal platform sufficiency. The PRD remains draft 0.1.0, not approved for implementation.

This checkpoint saves planning and research only. It does not authorize lab implementation, infrastructure changes, paid evaluations, optimization jobs, or red-team scans. No cloud feasibility run has been completed.

The earlier checkpoint was committed and pushed as `6d099f6`; the subsequent pause checkpoint was committed locally as `aba1446`. The current resume request does not authorize another commit, push, PR, final PRD approval, or implementation.

Industry evidence is saved in [evaluation-driven-development research](../../research/2026-11-05/evaluation-driven-development-research.md). OpenAI, Anthropic, Microsoft, and a research paper support early repeated evaluation and a qualified TDD analogy. This adds external support for the engineering principle, not proof of industry-wide adoption or workshop effectiveness. Evaluations can assess functional and non-functional requirements; they do not replace all system testing. Read this evidence before asking the user to justify the analogy again.

## Read these files first

1. `coaching-state.md`: YAML state in a fenced block, user quotations, decisions, method history, and remaining questions.
1. `method-04-brainstorming\session-plan.md`, `divergent-ideas.md`, and `session-notes.md`: ideation structure, rough ideas, and phase tracking; all are within `method-04-brainstorming`.
1. `method-04-brainstorming\theme-clusters.md`: three proposed learning approaches and the pending opening-experience question.
1. `prd.md` and `prd-state.md`: draft requirements, proposed acceptance criteria, evidence limits, technical gates, and review state.
1. `method-03-synthesis\problem-definition.md`, `insight-statements.md`, and `how-might-we-questions.md`: consolidated synthesis and five-dimension assessment; paths are all within `method-03-synthesis`.
1. `method-03-synthesis\affinity-clusters.md`: working evidence groups, tensions, source strength, and the next discussion. These are not final validated themes.
1. `method-03-synthesis\practitioner-evidence.md`: anonymous practitioner evidence, its limits, and the user-approved learning gap. Omit people and company names from repository notes.
1. `method-03-synthesis\input-inventory.md`: evidence sources, coverage gaps, synthesis approach, and the first candidate for discussion.
1. `method-02-research\findings-summary.md`: consolidated evidence, confidence, deferred questions, and revised primary/secondary completion priorities.
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
- Prioritize learning to use/run evaluations, including rubric creation. Retain Agent Optimizer and hands-on red-team evaluations as secondary activities.
- Deployment blocks to secondary activities must not prevent primary completion. Report each affected activity's actual status, cause, and next action.
- Prioritize lower agent runtime cost while matching or exceeding baseline quality. Any quality reduction needs explicit customer acceptance.
- Support independent and facilitated learning, including reusable evaluation assets for handover and operations.
- Treat handover as reusable quality-assurance assets and processes for future customer, internal, or partner teams. The intended practice covers local development, CI/CD build/deployment, and regular production runs. Production evaluation is hands-on in the core: identify a quality failure in live activity, inspect the supporting conversation or trace, and explain what needs investigation. Use the deployed lab agent and synthetic passenger requests, not a customer production system. Exact mechanics remain open.
- CI/CD execution is optional extra credit, not a core prerequisite. Provide a real repository GitHub Actions evaluation workflow targeting the lab-deployed agent. Fork setup, environment settings, authentication, permissions, and quality-gate behavior require further exploration; initial workflow observations are in `implementation-plan.md`. Core production evaluation must not depend on this extension.
- Reuse existing provisioning. Support multiple tracks through maintained, data-driven requirements, with individual and organizer behavior.
- Recommend East US 2 for new environments. Preserve existing regions and organizer choices, and report module-specific limitations.

## Preferred technical direction, not a final architecture

Investigate one supplied Python hosted Responses agent, prepared for optimization, throughout the track. The earlier prompt-agent portal recommendation is suspended. Unknown Optimizer access must not by itself force a prompt-agent fallback.

The existing .NET travel track supplies scenario and tool ideas; it is not a requirement to adopt .NET or a multi-agent design.

## Open technical question

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
- Build on the two anonymous practitioner summaries without generalizing them to all partners. Beginner evaluation experience remains a design assumption, not a verified partner finding.
- Agree detailed tasks, rubric criteria, module sequence, and operational automation depth before implementation.

## Resume protocol

Resume PRD Builder from the JSON session state and the existing draft. Read the recorded next actions and unresolved decisions. Keep Method 6 incomplete unless the user asks to resume its tests. If DT coaching resumes, load the foundation and Method 6 references, selected-concept handoff, and prototype plan; preserve one assumption per rough variation. No timed comprehension test, learner session, or technical feasibility run has passed. Preserve the built-in-first hands-on opening, guided rubric generation/change, provisioning pre-work, and sub-two-hour target. Do not re-ask confirmed decisions, claim wider research validated, or treat the draft PRD as implementation approval.
