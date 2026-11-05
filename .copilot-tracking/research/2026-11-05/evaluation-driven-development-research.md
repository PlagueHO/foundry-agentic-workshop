# Task Research: evaluation-driven-development

| Field | Value |
|---|---|
| Date | 2026-11-05 |
| Researcher / agent | rpi-research, direct research |
| Output mode | research-only |

## Executive Summary

The early-evaluation perspective is shared in published engineering guidance from OpenAI, Anthropic, and Microsoft. OpenAI explicitly recommends evaluation-driven development and checks on every change. Anthropic recommends defining capability evaluations before agents can meet them. A CSIRO/Data61-affiliated research paper explicitly builds on TDD and BDD while explaining why these methods need adaptation for agents.

Research completed for this bounded question. Confidence is high that this is a shared engineering recommendation. These sources do not establish an industry adoption rate or prove that every team should use strict TDD. Evaluations support verification of both functional behavior and non-functional quality requirements; they do not replace whole-system testing or establish universal compliance.

## What You May Not Know

There is a stronger source than a loose TDD analogy: Anthropic explicitly recommends defining planned capabilities through evaluations before the agent can fulfill them. However, the current research paper also warns that TDD/BDD alone do not address stochastic behavior and post-deployment change.

The retrieved OpenAI page carries an Evals platform retirement notice. Its methodology is useful evidence here, not a recommendation to use that platform or API.

## Findings

### Early and repeated evaluation is an explicit engineering recommendation

OpenAI's "Evals tips" recommends evaluating early, writing scoped checks at every stage, and treating evaluation as a continuous process. Its "Design your eval process" section calls for running evaluations on every change. Anthropic's "Step 0. Start early" says product requirements translate into test cases early in development. Its account of Claude Code describes evaluations guiding changes and regression detection.

Practical implication: the lab can teach evaluation as feedback during construction, not only a final release gate.

- Questions: Q1.
- Evidence state: Evidence-backed finding.
- Evidence: W1, W2.
- Confidence and limits: High for published recommendations. Anthropic reports practical examples, but these are provider-reported experience, not a representative industry survey.

### The TDD analogy has direct support, with important differences

Anthropic's "Step 8" recommends defining evaluations for planned capabilities before agents can fulfill them and then iterating. The current EDDOps paper's introduction explicitly builds on TDD and BDD. Its earlier v2 abstract also states that inspiration directly.

Practical implication: "evaluation-driven development, with a TDD-like feedback loop" is supported wording. It is not necessary to claim that LLM evaluation is identical to conventional TDD.

- Questions: Q2.
- Evidence state: Evidence-backed finding.
- Evidence: W2, W4, W5.
- Confidence and limits: High for the existence of the analogy and test-before-capability recommendation. The paper is a research proposal informed by a literature review, not an industry standard. Its abstract page says the submission is under review. Its characterization of traditional TDD is the authors' position, not a universal definition.

### Quality requirements need evidence, not just a passing score

Microsoft recommends baselines, metrics aligned with business goals, continuous monitoring, and decision gates. Anthropic describes tracking latency, token usage, cost per task, and error rates, alongside task and behavior checks.

Practical implication: evaluations can provide evidence for agreed non-functional quality requirements. The workload still needs functional, integration, load, reliability, and security testing appropriate to the requirement. Evaluations are not exclusively non-functional: tool selection and task correctness also assess functional behavior.

- Questions: Q3.
- Evidence state: Evidence-backed finding.
- Evidence: W1, W2, W3.
- Confidence and limits: High for the need to combine quality measures and other tests. A representative dataset, reliable grading, repeated trials where needed, and human calibration determine what the evidence can support. No source establishes that a single judge score proves compliance.

### Shared guidance is not proof of universal adoption or complete coverage

Anthropic describes teams adopting evaluations at different stages, including later at scale. It recommends combining automated evaluation with production monitoring, user feedback, A/B tests, transcript review, and human evaluation. It also describes grading and environment errors that can produce misleading results.

Practical implication: use this research to support the teaching principle, not to label all partners as immature or to claim the proposed lab is validated.

- Questions: Q1, Q2, Q3.
- Evidence state: Evidence-backed finding.
- Evidence: W2, W3, W4.
- Confidence and limits: High for these cautions. The prevalence of early evaluation in the wider industry remains unmeasured by this research.

## Recommendation and Alternatives

Decision state: the user requested evidence, not an implementation choice. The sources support the early-evaluation principle. They support a qualified TDD analogy rather than equivalence.

| Framing | Benefit | Risk | Evidence | Disposition |
|---|---|---|---|---|
| Evaluation-driven development with a TDD-like feedback loop | Describes early criteria and repeated change assessment | Must explain stochastic results and grading limits | W1, W2, W4 | Evidence-supported wording |
| Evaluations are simply TDD for AI | Familiar shorthand | Conceals differences in grading, sampling, and runtime oversight | W2, W4 | Too broad |
| Evaluate only at release | Simple phase boundary | Misses development feedback and regression detection | W1, W2, W3 | Contrary to cited guidance |

No product or workflow is selected. Further adoption studies could change claims about prevalence, not the verified existence of this recommendation.

## Scope and Questions

Goal: find independently published evidence for or against the requester's view of evaluation as an early, repeated engineering capability throughout product development.

Audience: consultants, delivery engineers, and solution architects designing a Foundry learning track.

In scope: primary industry engineering guidance, explicit TDD analogies, lifecycle integration, quality-requirement links, and limitations of these comparisons.

Out of scope: implementation, cloud runs, paid jobs, updating the PRD or DT state, and claims about measured industry adoption.

Criteria: verify primary pages; distinguish recommendations from adoption evidence; separate repeated evaluation from strict test-first development and from statistical proof of requirement satisfaction.

| ID | Question | Source | Status |
|---|---|---|---|
| Q1 | Do industry sources recommend starting evaluation early and repeating it while building? | User request | Answered; W1, W2, W3 |
| Q2 | Do sources explicitly compare this to TDD or describe evaluation-driven development? | User analogy | Answered; W1, W2, W4, W5 |
| Q3 | What supports using evaluations to verify quality requirements, and what are the limits? | User framing | Answered; W1, W2, W3, W4 |

## Decisions and Feedback

| Group | Item | Status | Owner | Rationale and effect |
|---|---|---|---|---|
| D1 | Find evidence for and against the perspective | Confirmed | User | Completed; no clarification was necessary |
| D2 | Use the evidence to revise the PRD or close DT validation | Deferred | User / DT coaching | Not requested in this research; source evidence does not validate learner outcomes |

No unresolved material research decision requires a walkthrough. No source, PRD, or coaching-state file was changed during this bounded research.

## Risks and Open Questions

| Priority | Risk or gap | Effect | Smallest useful next evidence |
|---|---|---|---|
| High | Generalizing provider guidance to industry-wide adoption | Unsupported maturity claims | Representative independent adoption study, if that claim becomes necessary |
| High | Treating a judge score as proof that an NFR is met | False assurance | Requirement-specific measurement and calibrated evaluation with adequate cases and trials |
| Medium | Assuming this validates the workshop | Unsupported learning claim | Representative learner testing, separately authorized |
| Low | Using OpenAI methodology as current platform-selection advice | Obsolete implementation guidance | Recheck product documentation if implementation is later considered |

## Planning Readiness and Next Step

| Field | Record |
|---|---|
| Research disposition | executed; bounded research completed |
| Decision participation | user-owned; standalone evidence request |
| Planning Readiness | Not applicable; research-only |
| Research depth and helpers | Wider, deeper, and contrarian waves completed; no helpers |
| Blockers | None |
| Output mode and planning support | research-only; no planning handoff |
| Continuation owner | User, current DT coaching conversation |
| Required gates or confirmations | Sources verified; no DT transition or implementation gate evaluated |
| Next action | No user action required; return evidence to the current conversation |
| Primary evidence file | .copilot-tracking/research/2026-11-05/evaluation-driven-development-research.md; date from user-supplied local date |

## Research Record

### Method and Boundaries

| Field | Record |
|---|---|
| Research posture and provenance | balanced, default; adjacent limits and requirement-verification claims may affect the answer |
| Helper lane effort | Not applicable; no helpers |
| Completion basis | All three questions answered by verified primary sources; contrarian checks qualify rather than overturn the result |
| Explicit limits or deadline | No deadline supplied; evidence only |
| Codebase and external scope | Existing conversation supplies the hypothesis; public industry guidance supplies evidence |
| Initial candidate areas | OpenAI, Anthropic, Microsoft, independent engineering guidance, and evaluation methodology |
| Evidence root | .copilot-tracking/research; default root |
| Constraints and excluded sources | No private conversations sent to search; no source or DT artifact edits |
| Prior knowledge | Early evaluation is plausible, but the TDD analogy and industry agreement require fresh verification |

### Extensions and Participation

#### Extension Registry

| Kind | Candidate | Provenance and scoped contract | Selected or skipped reason |
|---|---|---|---|
| Instruction | Repository Markdown instructions and AGENTS.md | Markdown format and required lint | Selected; apply to this evidence artifact |
| Skill | evaluation-design | Evaluation methodology | Skipped; no dataset, metric, or experiment is being designed |
| Skill | microsoft-foundry | Foundry implementation and evaluation | Skipped; cross-industry conceptual research, not a Foundry version or configuration decision |
| Skill | dt-methods | Active Method 3 context | Existing context retained; this bounded evidence check does not transition methods |

#### Direction and Participation Log

| Checkpoint | Direction | Answer or no-interaction reason | Effect |
|---|---|---|---|
| Intake | Verify whether industry shares the early-evaluation/TDD perspective | Topic and scope are explicit; no clarification needed | Research-only; do not assume consensus or modify requirements |

### Research Cycle Log

#### Cycle 1

##### Wave 1: Wider

Search found direct OpenAI advice to evaluate early and on every change, Anthropic guidance to start evaluation early, and a research paper explicitly describing inspiration from TDD and BDD.

Reflection: these are candidate sources, not yet verified evidence. Prioritize direct page reads. The paper may support the analogy, but a proposed process model cannot establish industry adoption. Investigate quality-attribute guidance separately before equating evaluation with verification of non-functional requirements.

##### Wave 2: Deeper

Verified OpenAI's evaluation best practices, Anthropic's agent-evaluation article including its maintenance guidance, Microsoft's Well-Architected testing guidance, and both v2 and current v3 of the EDDOps paper.

Reflection: direct guidance strongly supports early and repeated evaluation. Anthropic explicitly recommends defining capability evals before the agent can fulfill them. The current research paper both uses and limits the TDD analogy. Microsoft distinguishes model evaluation from full-system testing. These differences require qualification rather than a blanket equivalence between evals, TDD, and all non-functional verification.

##### Wave 3: Contrarian

Targeted search for limits of unit-test analogies, judge reliability, and quality-attribute scope returned secondary pages. Do not rely on those unverified pages. Stronger counter-evidence is already directly available in the primary sources: Anthropic's grading and nondeterminism cautions, Microsoft's model/system distinction, and the current paper's explicit limits of TDD/BDD.

Reflection: the shared engineering recommendation holds. Equivalence with TDD and evaluation-only NFR assurance do not. No additional search is required to answer these questions; adoption prevalence is a separate, unrequested empirical question.

##### Synthesis and Re-entry

| Claim | Evidence | Disposition | Reason |
|---|---|---|---|
| Start early and rerun during development | W1, W2, W3 | Accepted | Direct independent provider guidance |
| TDD-like feedback and criteria before capability | W2, W4, W5 | Accepted with qualification | Explicit support, but not equivalence |
| Evaluations alone verify all NFRs | W1, W2, W3 | Rejected | Functional scope and additional system testing must be distinguished |
| Early evaluation is universally adopted | W2 | Unresolved; not claimed | Provider reports include late adoption; no representative survey |
| Lab effectiveness is validated | None | Deferred | Requires learner evidence |

Another complete cycle is not required. The material questions have direct support and credible limits; more similar advice would be redundant. Re-enter if a decision requires prevalence estimates, stronger causal outcome evidence, or requirement-specific assurance.

### Evidence Log

No helpers used. All sources were checked directly with web_fetch after web_search discovery. Retrieved 2026-11-05 using the user-supplied local research date.

| ID | Source and location | Evidence | Version or date | Confidence |
|---|---|---|---|---|
| W1 | [OpenAI: Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices), "Evals tips" and "Design your eval process" | Early and repeated evaluation, every-change checks, human calibration, functional checks | Live page retrieved 2026-11-05; no publication date established | High for stated guidance |
| W2 | [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents), "Why build evaluations?", "Step 0", "Step 8", and holistic-methods section | Early requirements, before-capability evals, reported practice, repeated trials, human calibration and complementary methods | Search metadata says 2026-01-09; body fetched directly on 2026-11-05 | High for stated guidance; reported outcomes not independently audited |
| W3 | [Microsoft: Test and evaluate AI workloads on Azure](https://learn.microsoft.com/en-us/azure/well-architected/ai/test), introduction, quality metrics, agent workflows, inference endpoint | Baselines, iterative development, metric gates, separate full-system and non-functional testing | Page metadata updated 2025-10-30; retrieved 2026-11-05 | High for architecture guidance |
| W4 | [Evaluation-Driven Development and Operations of LLM Agents](https://arxiv.org/html/2411.13768v3), abstract and introduction | TDD/BDD-inspired lifecycle loop, system-level quality attributes, limits of static tests and deterministic analogies | v3, 2025-11-17; retrieved 2026-11-05 | High for what the paper proposes; not an adoption study or standard |
| W5 | [Earlier Evaluation-Driven Development of LLM Agents abstract](https://arxiv.org/abs/2411.13768v2) | Explicit TDD and BDD inspiration | v2, 2025-03-27; retrieved 2026-11-05 | Historical corroboration only; same paper as W4, not independent evidence |

#### Contradictions and Conflicts

Microsoft uses a narrower distinction between model evaluation and whole-system testing. The research paper uses evaluation as a broader umbrella. Resolve this by stating the actual check and quality attribute rather than assuming consistent terminology.

OpenAI and Anthropic support development-time evaluation; this does not conflict with their cautions about nondeterminism and human judgment. The qualifications constrain the TDD analogy rather than disprove it.

### Artifact Self-Check

- [x] User-facing sections explain results, scope, findings, alternatives, decisions, risks, readiness, and next action.
- [x] Questions are answered; evidence states and limits are explicit.
- [x] Each finding keeps its evidence, implications, and qualifications together.
- [x] External evidence has stable W IDs, URLs, retrieval date, and available version metadata; no codebase findings claimed.
- [x] Wider, deeper, and contrarian waves ran in order with separate reflections and synthesis.
- [x] Posture, boundaries, extensions, participation, prior knowledge, and no-helper choice are recorded.
- [x] Research-only mode does not select an implementation or invoke another phase.
- [x] No unresolved material decision requires user acknowledgment.
- [x] Disposition, readiness, continuation, deferred evidence, and residual uncertainty are recorded.
- [x] Stop basis is evidence-led; no secrets recorded; writes stayed in the research root.

Checked sections: all. Limits: no adoption survey, independent audit of reported provider outcomes, or live validation. Markdown checks are recorded by the execution result, not inferred from this self-check.
