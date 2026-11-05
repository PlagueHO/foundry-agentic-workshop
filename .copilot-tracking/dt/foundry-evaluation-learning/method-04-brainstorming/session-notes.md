# Brainstorming session notes

## Entry decision

On 2026-11-05, the user confirmed bounded closure of Method 3 and entry to Method 4. Carry forward evaluation principles, early development feedback, Microsoft Foundry capability/value awareness, production investigation, and reusable handover.

The normal Method 3 exit is only partly met. The user accepts a cautious design exploration from the working baseline, not a claim of full validation.

## Phase tracking

Ideation planning is recorded in `session-plan.md`. Divergent execution began with three labelled coach seeds in `divergent-ideas.md`. The user then contributed IDEA-004: hands-on early rubric creation and agreement to expose customer priorities, support alignment, and build trust before delivery. The user tentatively added IDEA-005: adjust the rubric and show how the change is implemented. Three further coach seeds explore inspecting individual results, repeated runs, and adding a failure-derived case. There are eight rough ideas; no ranking or clustering has occurred.

Ease of rubric creation and trust benefits are user objectives, not verified product or learner outcomes. Keep the practical experience central rather than reduce this idea to an explanation or demonstration.

The user next requested suggestions from the Foundry evaluation docs. The coach read nine official pages and added seven source-linked suggestions plus documented extensions of existing ideas. There are now 15 rough ideas. The numerical target is met, but no breadth assessment, theme clustering, or agreement to converge has occurred.

Documented features remain distinct from lab feasibility. Noted hosted-target uncertainty in synthetic conversation examples, evaluator-level skips, SDK 2.8.0 requirements for trace datasets, trace permissions/ingestion, preview features, and model usage costs. No live run verified these exercises.

The user then explicitly asked which suggestions would help learners reach the desired outcomes. This invites an outcome-fit assessment, not automatic approval of a syllabus or Method 5 transition. No ideation stall or other session-energy observation is inferred.

## Proposed outcome-fit assessment

These are coach recommendations for discussion, not approved scope or separate required modules. Several activities can share the same small dataset and supplied agent.

| Proposed core activity group | Desired learner evidence | Draft requirement links |
|---|---|---|
| Run supplied cases with built-in and domain checks | Explain what an evaluation checks, why it matters, and why different checks can disagree | FR-002, FR-004, FR-019 |
| Create/refine a rubric and calibrate it on known answers | Inspect criteria, scores, and reasons; explain a disagreement and refine ambiguous criteria | FR-005, FR-019 |
| Apply a rubric change to unchanged saved responses | Explain how changed expectations affect judgment without calling it an agent improvement | FR-005; user's IDEA-005 |
| Investigate tool-result use and fictional-policy grounding | Distinguish tool execution, use of returned facts, and domain quality; locate the relevant evidence | FR-004, FR-008 |
| Change the agent, rerun locally, and compare with the baseline | Demonstrate an improved quality aspect, check regressions, use separate held-back cases, and justify the next decision | FR-003, FR-006, FR-007, FR-008 |
| Evaluate synthetic live lab activity and investigate a failure | Obtain actual evaluation evidence linked to live activity, inspect its conversation/trace, and explain the next investigation step and repeat-run process | FR-009, FR-010, FR-011 |

Use the documented side-by-side comparison inside the improvement activity rather than create a separate module. Keep dataset, rubric, and judge settings fixed when assessing agent changes; do not require statistical significance from a tiny lab set. Include a short feature/value/limit explanation based on actual results across the core.

Trace-to-dataset can be a short extension of live investigation if its setup and runtime are practical. Reusable supplied cases, rubrics, commands, and guidance meet the reuse learning purpose without requiring a separate handover simulation or that specific data-generation feature.

Synthetic conversation generation, explicit turn-versus-conversation comparison, and cluster analysis provide useful optional depth. They are not necessary for the agreed introductory and primary practical outcomes and add data, evaluator, time, or model-use requirements. This is a proposed fit judgment, not a measured learning benefit.

Keep Agent Optimizer and controlled red teaming as already planned secondary activities. Keep CI/CD execution optional. No scope deletion or priority change is approved by this assessment.

## Two-hour target and proposed scope cuts

The user set a two-hour lab target and asked for approximately 80% feature coverage, then confirmed that infrastructure provisioning is pre-work excluded from a target of less than two hours. Duration and the pre-work boundary are requester constraints; the schedule and cuts below are coach recommendations. No feature denominator is agreed, so this is not a measured 80% catalogue-coverage claim.

| Time budget | Proposed activity | Scope control |
|---|---|---|
| 10 minutes | Check lab-agent readiness and run one sample request | Infrastructure provisioning is confirmed pre-work; the agent readiness check is inside the session. Verify actual timing. |
| 15 minutes | Run supplied cases and inspect built-in versus domain results | Use one compact dataset and a few representative evaluators, not an evaluator catalogue tour. |
| 25 minutes | Create/refine/calibrate a rubric and apply one criterion change | Combine rubric creation, human judgment comparison, and rubric revision; no separate customer-alignment simulation. |
| 25 minutes | Investigate one failure, apply one supplied agent change, rerun and compare | Fold tool-use diagnosis and baseline comparison into the improvement loop; preserve fixed scoring settings and a separate small held-back set. |
| 25 minutes | Generate and evaluate live lab activity, investigate a failure, and review the repeat-run process | Use a prepared traffic script and bounded evaluation configuration; do not require CI/CD or a long scheduled-run wait. |
| 5 minutes | Explain the evidence, Foundry features used, and one limitation | Check learning through the learner's own results rather than a separate delivery exercise. |
| 14 minutes | Contingency for expected service waits and learner recovery | Proposed total is 119 minutes, below the 120-minute limit; waits are included, not added afterwards. |

Move synthetic scenario generation, explicit turn-versus-conversation comparison, cluster analysis, and trace-to-dataset creation outside the timed core. Supply reviewed cases instead of asking learners to construct data or author Python. Defer a separate repeated-run variability study and exhaustive judge/model comparison. These are reductions in activity depth, not permission to hide missing evidence.

Keep Agent Optimizer, controlled red teaming, and CI/CD as optional follow-on activities outside the two-hour core. This recommends their placement; it does not remove previously agreed delivered-track assets or silently reclassify core production evaluation.

The budget totals 105 minutes of readiness, exercises, and review plus 14 minutes of contingency. It is an untested design budget. Verify agent readiness, evaluation queues, hosted support, trace ingestion, and production-scoring latency in Method 7 and learner pacing in Method 8. Infrastructure provisioning is required pre-work outside this session, not an optional or silently omitted prerequisite.

## User correction: learning lab, not customer delivery

The user asked what handover meant, then explicitly reminded the coach that the repository provides hands-on learning labs, not real customer deliveries. The coach acknowledged drifting too far into delivery and proposed keeping handover as context, not a separate exercise or simulation. The user confirmed continuing with this framing.

Preserve the professional value of reusable evaluations without requiring a successor role-play or customer acceptance activity. Existing lifecycle goals remain context for learning Foundry tooling. No new customer-delivery requirement is inferred.

## Boundaries

An initial outcome-fit recommendation is now recorded at the user's request. No approved idea selection, module sequencing, implementation, cloud runs, or external board writes occurred. The PRD remains a draft. These artifacts are local changes after the previous commit/push checkpoint.

## Next interaction

Review the proposed cuts against the target below two hours after provisioning pre-work. Do not ask for the confirmed pre-work boundary again or promise measured duration or 80% coverage before validation.

## Pause checkpoint

The user requested saving all method state, committing all session work on the existing branch, and continuing later. Method 4 remains active but paused. No theme clusters, selected concept, or Method 5 transition have been approved. The current commit is local only; no push is requested.
