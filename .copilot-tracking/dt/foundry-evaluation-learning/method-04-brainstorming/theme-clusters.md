# Method 4 candidate learning themes

## Status

The user accepted Method 4 closure for concept development and explicitly approved Method 5 on 2026-11-06. These themes are handoff inputs, not an approved full syllabus or evidence of technical feasibility. Current concept work is in `../method-05-user-concepts/`.

The user resumed Method 4 on 2026-11-05. These are coach-proposed groups of the 15 ideas by learning approach, not approved concepts, module order, or a Method 5 handoff. The user subsequently accepted supplied good/bad examples for the introduction, with an explanation of their purpose. This selects an introductory approach, not a complete lab concept or sequence.

The three themes can inform different lab concepts or be combined after discussion. Each must preserve practical rubric work, a comparable improvement cycle, and live lab evaluation. They are not three separate full-length paths to implement.

## Theme A: Learn by seeing a mismatch

- **Core approach:** Start with a plausible answer, expose a gap between appearance and evidence, and use that gap to motivate evaluation.
- **Representative ideas:** IDEA-001 (predict acceptability), IDEA-006 (inspect individual failures), IDEA-010 (check evaluator judgments), IDEA-011 (compare different checks), IDEA-012 (tool call versus tool-result use).
- **Grouping rationale:** These ideas teach through comparison and disagreement, not through an evaluator catalogue.
- **Constraint integration:** Use one supplied flight example and visible returned facts. No airline expertise, customer role-play, or Python authoring is required. Reuse the example in later rubric and improvement work.
- **Stakeholder value:** Consultants gain a concrete value explanation; engineers inspect the failure mechanism; architects see why one metric is insufficient.
- **Concept entry point:** A failure-first lab opening, followed by criteria creation, improvement, and live activity investigation.
- **Question to test later:** Does the example make the value clear without suggesting every evaluation failure is obvious to a person? If a live response is used, does a realistic baseline actually produce the intended failure often enough for a bounded lab?

## Theme B: Learn by making expectations explicit

- **Core approach:** Turn supplied quality expectations into criteria, then test whether those criteria produce useful judgments.
- **Representative ideas:** IDEA-004 (early rubric alignment), IDEA-005 (implement a rubric change), IDEA-009 (generate and refine criteria), IDEA-010 (compare with known judgments).
- **Grouping rationale:** These ideas teach evaluation as an explicit definition of quality, rather than a score selected after delivery.
- **Constraint integration:** Supply fictional policy and passenger requirements. Keep rubric creation, checking, and one revision inside the proposed 25-minute activity budget; no simulated customer meeting.
- **Stakeholder value:** Consultants can explain alignment; architects connect requirements to checks; engineers have criteria to use while building.
- **Concept entry point:** A rubric-first opening, followed by scoring, diagnosis, agent improvement, and live evaluation.
- **Question to test later:** Can a learner with limited practical evaluation experience write useful criteria before seeing a scored example?

## Theme C: Learn through a controlled change and feedback

- **Core approach:** Establish a baseline, change one thing, evaluate again, and use evidence to decide what to do next.
- **Representative ideas:** IDEA-002 (agent change), IDEA-003 (live failure investigation), IDEA-007 (repeated runs), IDEA-008 (failure-derived case).
- **Grouping rationale:** These ideas teach evaluation as a repeatable feedback process across development and operation, not a one-off report.
- **Constraint integration:** Supply scripts and cases. Keep scoring settings fixed for agent comparisons, separate rubric-change experiments, and retain a small held-back set. A separate variability study and dataset-building workflow are not needed in the timed core.
- **Stakeholder value:** Engineers experience evaluation while building; architects see development-to-operation continuity; consultants can explain the value using actual before/after evidence.
- **Concept entry point:** A change-first opening with a supplied baseline, followed by investigation and refinement of what the checks measure.
- **Question to test later:** Does starting with a supplied baseline hide too much rubric reasoning for the introductory outcome?

## Deferred feature depth

IDEA-013 (turn/conversation comparison), IDEA-014 (synthetic scenario generation), and IDEA-015 (cluster analysis) remain available for optional depth. They are not discarded, and they are not required to distinguish these learning approaches. The proposed placement of Optimizer, controlled red teaming, and CI/CD outside the timed core remains subject to scope review.

## Reliability challenge and revised recommendation

The user challenged whether an agent will reliably produce bad flight advice without being explicitly told to fail or given bad instructions/tools. No live test has established a repeatable failure. The earlier recommendation was too confident about a live failure-first opening.

For the introductory rubric exercise, the coach now recommends supplied good/bad response examples, with provenance labelled accurately: hand-authored teaching examples or captured model outputs, as applicable. Learners still create or revise a rubric and run actual Foundry evaluations, but a fresh agent response need not fail on demand. A saved answer is not evidence that the current live agent produced it.

The user accepted this supplied-example introduction and an explicit explanation of the choice. The precise order of rubric creation and example comparison remains open. The trade-off is less live-agent realism in the introduction in exchange for predictable teaching inputs.

The live improvement and production exercises remain separate feasibility gates. A supplied baseline with an explicit, realistic limitation might expose a failure without an instruction to answer incorrectly, but that behavior is unverified. A generic prompt may still succeed, and faulty tool data can create a data-quality failure rather than an agent reasoning failure. Test the actual baseline, corrective change, held-back cases, and evaluator judgments before promising this experience. Do not retry until a failure appears, tighten criteria merely to force a fail, or count recorded answers as completion of live requirements.

Explain to learners that these inputs are supplied so they can compare known acceptable and unacceptable behavior without waiting for a particular model mistake. Their Foundry evaluation is real; the inputs are not claimed to be freshly generated by their agent. Keep this explanation separate from the evaluator's own possible scoring variation.

The introductory decision is accepted. Do not ask for it again. The subsequent Method 5 approval accepts these themes as sufficient concept-development inputs. Live exercise design and retained scope remain open.

## Limits

The proposed 119-minute budget is untested. Feature coverage has no agreed denominator. No group proves learning effectiveness, hosted-agent support, or production-scoring latency. The explicit Method 5 approval closes Method 4 for concept development, not as approval of every scope cut or technical claim. No automatic deck offer follows from this draft.
