# Divergent learning-experience ideas

## Status

Fifteen rough ideas: thirteen coach seeds and two user ideas. The numerical target is met, but breadth and readiness for convergence have not been agreed. Target: ideas across 4-6 distinct approaches before evaluation. IDs identify ideas, not priority or module order. Nothing is selected.

## Learning-lab boundary

The user clarified that this is a learning lab like the existing repository labs, not a real customer delivery. Exercises give learners practical knowledge and experience with Foundry tooling. Customer priorities explain why rubrics matter; do not require a customer agreement meeting, role-play, or separate handover simulation. Reusable assets remain useful learning outputs and professional context.

## Round 1: Coach seeds for discussion

| ID | Rough idea | Perspective or constraint | Origin |
|---|---|---|---|
| IDEA-001 | Predict which of two flight-advice answers is acceptable, then compare that judgment with Foundry evaluation results. | Consultant; first-run value explanation without airline expertise | Coach seed |
| IDEA-002 | Make one supplied agent change and rerun Foundry evaluations to see what improved and what regressed. | Delivery engineer; local feedback without Python authoring | Coach seed |
| IDEA-003 | Follow a failed evaluation from synthetic live lab activity to its conversation or trace and explain the next investigation step. | Operator and architect; hands-on production evidence without customer production access | Coach seed |

These are learning ideas, not verified exercise designs. Generated behavior, scoring, and result-to-trace navigation still require later technical verification.

## Round 2: User idea - early rubric agreement

| ID | Rough idea | Perspective or constraint | Origin |
|---|---|---|---|
| IDEA-004 | Turn customer priorities into an agreed rubric early, create and run a Foundry rubric evaluation hands-on, and use the evidence to discuss alignment before delivery. | Consultant, architect, and delivery engineer; practical customer agreement before delivery | User |

The user wants learners to experience straightforward rubric creation and how early rubric agreement can make customer priorities explicit and support trust. Ease of creation, improved alignment, and trust are intended learning benefits, not measured outcomes. Rubric agreement alone does not prove solution quality or guarantee customer trust. Customer priorities can be supplied as learning inputs; no customer role-play is required.

## Round 3: User idea - changing the rubric

| ID | Rough idea | Perspective or constraint | Origin |
|---|---|---|---|
| IDEA-005 | Adjust the rubric for a changed customer priority and implement that change in the hands-on evaluation exercise. | Consultant and delivery engineer; evolving customer expectations | User, tentative |

A coach extension for later exploration is to evaluate the same saved responses under both rubric versions before changing the agent. This would help distinguish changed criteria from changed agent behavior; scores from different rubric versions are not directly comparable evidence of agent improvement. This comparison is not yet a user-approved exercise design or a verified product workflow.

## Round 4: Coach seeds - learning through Foundry tools

| ID | Rough idea | Perspective or constraint | Origin |
|---|---|---|---|
| IDEA-006 | Inspect individual evaluation results to find a failed response that an overall average can hide. | Consultant and architect; interpreting evidence rather than accepting a headline score | Coach seed |
| IDEA-007 | Evaluate the same cases more than once and inspect whether results vary. | Delivery engineer; learning the limits of repeatability without assuming variation will occur | Coach seed |
| IDEA-008 | Turn an observed failed response into a new evaluation case and rerun the expanded set. | Delivery engineer and operator; learning to maintain evaluation coverage | Coach seed |

These are rough tooling experiences, not a module sequence or confirmed product workflows. Exact result detail, supported inputs, and execution steps require later feasibility checks. The user corrected the handover framing; that correction is not an additional idea or a rejection of reusable evaluation assets.

## Round 5: Documentation-informed coach suggestions

The user asked the coach to read Foundry evaluation documentation and suggest further hands-on activities. The following suggestions use official documentation read on 2026-11-05. Documented capability is not proof that the exercise works with the proposed hosted agent, installed SDK, models, permissions, or workshop duration.

| ID | Rough idea | Perspective or constraint | Origin and source |
|---|---|---|---|
| IDEA-009 | Generate a rubric from the lab agent's context or fictional policy, then inspect and refine its criteria. | All learners; experience generation rather than receive a finished rubric | Coach; [rubric evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators#generate-a-rubric-evaluator) |
| IDEA-010 | Score a few prepared responses yourself, compare with the rubric judge's reasons, and revise ambiguous criteria. | Consultant and architect; learn to check the evaluator, not blindly trust its score | Coach; [rubric review](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators#review-and-adjust-the-rubric) |
| IDEA-011 | Evaluate the same response with a domain rubric and a relevant built-in evaluator to see which question each answers. | All learners; distinguish domain quality from broader checks | Coach; [rubric and built-in evaluator use](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators) |
| IDEA-012 | Inspect a correct tool call whose result the agent misuses, comparing tool-call accuracy with tool-output utilization. | Delivery engineer and architect; separate successful execution from correct use of returned facts | Coach; [agent process evaluation](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators#process-evaluation) |
| IDEA-013 | Evaluate a prepared flight conversation at turn and conversation level to investigate a missed passenger requirement across turns. | All learners; experience evaluation beyond one answer | Coach; [conversation datasets](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations#choose-an-evaluation-level) |
| IDEA-014 | Generate a small set of synthetic scenarios and conversations, then inspect whether they cover useful flight-disruption cases. | All learners; learn test-data creation without Python authoring | Coach; [synthetic conversations](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-synthetic-conversations#how-synthetic-conversation-evaluation-works) |
| IDEA-015 | Generate cluster analysis of prepared evaluation results and check a suggested failure pattern against its individual samples. | Consultant, engineer, and architect; learn failure-pattern analysis without treating generated diagnosis as fact | Coach; [cluster analysis](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cluster-analysis) |

## Documentation-backed extensions of existing ideas

These are refinements, not extra ideas added to meet the numerical target.

- IDEA-002: Use the portal's baseline and side-by-side run comparison after a supplied change. Keep the evaluation dataset, criteria, and judge settings fixed. A small lab sample may produce an inconclusive statistical comparison; do not promise significance. See [evaluation results and comparison](https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluate-results#compare-the-evaluation-results).
- IDEA-003: Configure a bounded live-traffic evaluation rule against synthetic lab activity and inspect its results. Continuous evaluation samples live traffic; scheduled evaluation runs on a fixed schedule. Do not equate them or promise immediate results. Core production evaluation remains required, not optional. See [agent monitoring](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard#set-up-continuous-evaluation).
- IDEA-005: Change a dimension weight or pass threshold while leaving responses unchanged. Explain that this changes the scoring policy, not the agent. A weighted rubric does not automatically implement a critical-failure rule. See [rubric adjustments](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators#review-and-adjust-the-rubric).
- IDEA-008: Use the portal's **Add to dataset** action on selected synthetic lab traces, then inspect the resulting evaluation data. This gives a concrete tooling route for reusing an observed failure. See [traces to datasets](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/traces-to-dataset#manually-add-traces-to-a-dataset-portal).

## Support and learning limits

- Rubric auto-generation can use a hosted agent's description, not its source code or full internal implementation. Add supplied instructions or fictional reference files when the description is incomplete. Traces cannot be the only generation input.
- Calibrating a rubric against learner judgment is a learning activity supported by the rubric guidance; no separate built-in human-annotation workflow is assumed.
- Tool-call accuracy measures selection and parameters, not correct use of returned seat counts. Groundedness assesses support in supplied context, not independent source truth.
- Turn and conversation evaluators have different support. An unsupported evaluator can be skipped without the evaluation run failing. A completed run does not mean every requested evaluator produced evidence.
- Synthetic data is generated test material, not representative customer research. The example uses a prompt agent; verify the proposed hosted target and read-only tool behavior separately. Generation and simulation consume model usage.
- Cluster analysis requires a model and incurs token usage. The documentation identifies preview features and says the analysis is not stored; download it to retain a copy. Use enough prepared examples for a useful pattern without promising a minimum size not stated by the service.
- Trace workflows require working Application Insights ingestion, user/service access, and supported regions. Trace dataset SDK guidance requires `azure-ai-projects>=2.8.0`; the previously examined repository lock resolves 2.7.0. No dependency change is made here. Keep private-content redaction on and use synthetic lab data.
- Monitoring and selected evaluators include preview features. Verify availability, cadence, costs, and cancellation for a bounded exercise. No evaluation rule or cloud job has been created.
- Model-target estimated inference cost shown in evaluation results is not an end-to-end hosted-agent cost. It excludes evaluator usage and evaluation runtime, and can be partial.
- Optimizer, controlled red teaming, and optional CI/CD remain in the existing plan. These suggestions do not change their priority or make them new core prerequisites.

The [evaluation overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview) links these workflows. The proposals remain rough learning experiences, not a feature-complete syllabus. No convergence or Method 5 transition is inferred from reaching 15 ideas.
