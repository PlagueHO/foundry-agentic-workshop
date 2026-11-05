# Method 3 input inventory

## Transition and scope

The user approved moving from Method 2 to Method 3: Input Synthesis. Method 2 is sufficient for this agreed transition, not complete validation of learner needs or technical feasibility. The requester has since supplied excerpts from two practitioner conversations; wider learner and customer validation remains open.

The transition uses the exit signal "Multi-source evidence; environmental context documented." Available source types are requester decisions, repository observations, and official product documentation. These do not constitute multiple independent learner perspectives.

## Available inputs

Paths are relative to the project directory.

| Input | Source type | Coverage | Limit |
|---|---|---|---|
| `coaching-state.md` | Requester quotations and decisions | Audience, learning goals, scenario, priorities, and constraints | One requester perspective; repeated quotations are not independent evidence |
| `method-01-scope\stakeholder-map.md` | Requester-described stakeholders | Builders, architects, operators, and acceptance owners | No direct interviews with these groups |
| `method-01-scope\scope-boundaries.md` | Confirmed scope | Coding limits, delivery modes, read-only flight advice, primary and secondary outcomes | Scope choices are not discovered learner behaviors |
| `method-01-scope\assumptions-log.md` | Hypotheses | Learner capability, customer confidence, handover, and scenario suitability | Not validated findings |
| `method-02-research\constraint-catalog.md` | Repository observations and official documentation | Setup, models, identity, data alignment, hosted evaluation, Optimizer, and red-team limits | No complete live workflow verification; historical choices are superseded by later decisions |
| `method-02-research\findings-summary.md` | Consolidated evidence register | Confidence, deferred evidence, primary completion, and later verification gates | Derived summary, not an additional independent source |
| `implementation-plan.md` | Working proposals | Possible learning sequence and deployment approach | Do not treat proposed modules or architecture as research findings |
| `resume-notes.md` | Recovery notes | Decision history and continuation context | Derived notes, not additional evidence |
| `method-03-synthesis\practitioner-evidence.md` | Anonymous summaries of requester-supplied conversation excerpts | Pilot assessment, evaluation uses, handover views, and the user-approved gap | Two practitioner perspectives; no direct customer evidence, observed workflows, or independent WorkIQ verification |

## Derived synthesis and requirements

The user authorized consolidation and a draft PRD. These outputs are derived from the inputs above, not new independent evidence:

| Output | Purpose | Status |
|---|---|---|
| `method-03-synthesis\affinity-clusters.md` | Group evidence and record tensions and teaching candidates | Source strength remains uneven; evaluator behavior unverified |
| `method-03-synthesis\insight-statements.md` | Explain three evidence-linked insights and their limits | Consolidated for review |
| `method-03-synthesis\problem-definition.md` | Define the problem and assess all five synthesis dimensions | Full Method 3 validation remains incomplete |
| `method-03-synthesis\how-might-we-questions.md` | Frame later design questions without selecting implementation | Draft for review |
| `prd.md` and `prd-state.md` | Capture requirements, proposed acceptance criteria, traceability, and authoring state | Draft 0.1.0; no final approval or formal quality review |

## Synthesis approach

1. Separate requester requirements, observed constraints, and unvalidated hypotheses.
1. Group related evidence into candidate themes with exact source pointers.
1. Identify supporting and conflicting evidence. Do not count a summary and its underlying source twice.
1. Review one candidate theme at a time with the user before developing insight statements.
1. Preserve gaps in learner representation and technical verification. Do not turn a preference for a feature into evidence of learning benefit.
1. Later assess research fidelity, stakeholder completeness, pattern robustness, actionability, and team alignment before proposing a move to Method 4.

## First candidate for discussion

Candidate framing: running an evaluation is a necessary step; the intended capability is using its evidence to decide what to investigate or change.

Source pointers: the requester's original release-decision outcome, their quotation about knowing what to change or investigate, and their latest priority of learning to use/run evaluations in `coaching-state.md`.

Status: requester-grounded interpretation, not a validated cross-partner theme. The user's answer below sets an earlier learning outcome than independent diagnosis or change selection. Those remain later track goals.

### First-run outcome clarified by the requester

In response to what learners should explain or decide after their first evaluation run, the user said:

> Have a general idea of what an evaluation is and be able to explain what it provides for a customer and agentic AI solution and why it's important to provide.

Confirmed requirement: learners should first understand what an evaluation is, explain its value to a customer and an agentic AI solution, and explain why it should be provided.

Candidate interpretation: understanding and explaining evaluation value comes before independent diagnosis. Do not require the first run to demonstrate all later track capabilities.

The subsequent practitioner discussion led to the user-approved gap in `practitioner-evidence.md`: turn customer expectations into repeatable checks, explain evidence and its limits, and hand checks over for later changes. This is a more specific gap than a general lack of evaluation knowledge. No single customer misunderstanding has been established.
