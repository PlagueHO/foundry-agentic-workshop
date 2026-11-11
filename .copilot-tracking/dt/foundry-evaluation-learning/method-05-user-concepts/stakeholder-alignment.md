# Method 5 learner-journey comparison

## Status and purpose

**Current disposition:** The requester approved bounded Method 5 closure and progression to Method 6 on 2026-11-07. Run Understand Customize is selected. See `method-06-handoff.md` for the selection rationale and three-lens assessment. Earlier pending-selection entries below are historical. The comprehension, learner-validation, and technical limits remain open.

The user explicitly approved closing Method 4 and starting Method 5 on 2026-11-06. These began as two rough coach-drafted concepts for review, not selected lab designs. Subsequent requester feedback combines their opening approaches: run a simple built-in evaluator before generating a rubric from supplied priorities. The original ordering distinction has converged; retain the cards as design history, not as two distinct current options. No comprehension test, independent learner review, simulated stakeholder feedback, or three-lens validation has been completed.

The concepts combine the Method 4 themes of visible mismatch, explicit expectations, and controlled change/feedback. They compare the opening interaction rather than invent different feature sets or three separate labs. The controlled-change theme remains in both because evaluating while building is a required learning outcome.

## Shared constraints

- Teach practical Foundry tooling, not a customer delivery simulation.
- Keep simple built-in evaluators and custom rubrics in the core. Relevance, Groundedness, and Tool Output Utilization are proposed examples, not a finalized evaluator list.
- Use clearly labelled supplied good/bad responses for introductory practice and explain why. Do not rely on a fresh agent producing a particular mistake.
- Keep actual live-agent improvement and production evaluation separate from supplied-response practice. Include a small held-back validation set and keep scoring settings fixed for agent comparisons.
- Target less than two hours after required infrastructure provisioning pre-work. The proposed 119-minute budget is untested; no new timing allocation is asserted here.
- Require no Python authoring or third-party evaluation platform. Supplied scripts are allowed.
- Keep the working flight scenario synthetic, read-only, and grounded in fictional policy.
- Preserve optional-depth proposals without claiming that all cuts or extensions are approved. Approximately 80% feature coverage remains an unmeasured breadth goal.

## Concept A: Evidence First

**Core idea:** Start with something learners can inspect, then let evaluation results motivate explicit quality criteria.

```text
Supplied answers -> Built-in checks -> Create/check/change rubric
                                      |
                                      v
Explain evidence <- Live activity <- Agent change and comparison
```

Text equivalent: Evaluate supplied answers with built-in checks; create, check, and change a rubric; evaluate an agent change; evaluate synthetic live lab activity; explain the results and limits.

**Purpose:** Make evaluation value concrete early without requiring a live model mistake.

**Validation target:** Can learners explain why a response can pass one check but fail a domain requirement, and use that distinction when creating a rubric?

**Constraint integration:** Reuses the same supplied examples and scripts; no customer role-play. Tool-use examples must include tool calls and outputs, not just final answers.

**Main trade-off:** Learners see scores before explicitly defining all quality expectations. The lab must not teach them to treat built-in defaults as complete acceptance criteria.

## Concept B: Criteria First

**Core idea:** Run a simple built-in check, define domain quality through a generated rubric, then compare what the checks measure.

```text
Introduce/run built-in check -> Inspect results and limits
                                          |
                                          v
Supplied priorities -> Generate/review rubric -> Compare checks
                                                     |
                                                     v
Explain evidence <- Live activity <- Refine rubric and compare agent change
```

Text equivalent: Introduce built-in evaluators; run a simple built-in check on supplied answers and inspect the results; use Foundry to generate a rubric from supplied requirements and policy; review its criteria against the lab's suggested priorities; evaluate supplied answers with that rubric and compare with built-in checks; refine the rubric; compare an agent change; evaluate synthetic live lab activity; explain the results and limits.

**Purpose:** Make early quality alignment explicit while keeping the task a tooling exercise rather than a customer meeting.

**Validation target:** Can learners with limited evaluation practice use an initial built-in result to understand evaluation, then generate and review domain criteria against supplied priorities without excessive facilitator help?

**Constraint integration:** Supplies requirements, policy, and examples rather than requiring domain expertise or test-data authoring. Keeps generation and manual review visible.

**Main trade-off:** The first built-in result gives practical context but must not be presented as complete coverage of the supplied requirements. Automatic rubric generation reduces manual authoring, but learners must still review its criteria.

## Three-lens review plan

| Lens | Evidence First question | Criteria First question | Current evidence |
|---|---|---|---|
| Desirability: learner usefulness and clarity | Does seeing results first help learners understand evaluation value? | Does defining criteria first make the purpose clearer? | Requester objectives support both; learner preference and comprehension are untested |
| Feasibility: tools and time | Can built-in results and rubric creation fit the budget with required input mappings? | Can rubric generation and review fit without early results for guidance? | Documentation supports relevant capabilities; integrated execution and timing are unverified |
| Viability: workshop value and maintenance | Can one example set teach both feature value and evidence limits without extra setup? | Can supplied requirements remain simple and maintainable while teaching alignment? | Both reuse the same agent/assets; delivery effort, spend, and facilitator load are unmeasured |

## Stakeholder review sequence

Use the required sequence: silent review, understanding check, gap identification, then resonance assessment. Start with the requester; later include partner consultants, delivery engineers, architects, and a facilitator or independent learner. Requester feedback is not independent learner validation. Do not invent role-play feedback if representatives are unavailable.

1. Let the reviewer read both concepts without adding a feature tour.
1. Ask the reviewer to describe the practical difference in their own words.
1. Record missing steps, confusing assumptions, and conflicts with the agreed learning goals.
1. Discuss which approach fits the intended learners and why, then review all three lenses.

The 30-second comprehension target is not yet measured. Image filenames in `concepts.yml` are optional output targets; no images have been generated.

## First review prompt

After reading both journeys, what would learners do differently at the start of Evidence First versus Criteria First?

Do not select a concept or create a Method 6 handoff until review evidence and rationale have been recorded. No Method 6 transition is authorized.

## Requester review: 2026-11-07

The requester found the initial understanding-check question confusing. The coach simplified it to a choice between evaluating example answers first and writing a rubric first. The requester replied: "Maybe write a rubric first".

This is a tentative preference for Criteria First, not final concept selection. The original explanation needed clarification; do not mark the 30-second comprehension target as passed. No independent learner review has occurred.

The next gap to explore is beginner support before the first result. The coach recommends supplied requirements plus one worked rubric criterion, leaving the remaining criteria for learners to write. This recommendation is not yet accepted. Pending question: Would one worked rubric criterion help learners get started, with the remaining criteria left for them to write?

### Correction: guided automatic generation

The requester accepted support but clarified: "for the Lab, we want to suggest to them what matters" and "the rubric evaluations will actually take a good guess at this automaticallly".

The manual-authoring recommendation above is superseded. The lab supplies the scenario, quality priorities, and fictional policy. Learners use Foundry to generate a starting rubric, review it against those priorities, and refine it before evaluating the supplied responses. A worked criterion can explain the review task; writing all remaining criteria from scratch is not required.

[Official rubric guidance](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators) recommends automatic generation followed by review and manual refinement. Generation can use a Foundry agent, system prompt, or reference files. For a hosted agent, selecting the agent supplies its description; do not assume generation reads its code or knows unstated priorities. The documented capability is verified, but this lab flow has not been run.

The learning emphasis is generating, checking, changing, and using criteria, not independently discovering domain requirements. Generated criteria are a starting proposal, not proof of quality or customer agreement. Criteria First remains the tentative preference.

Next gap question: For the rubric-change exercise, should the lab introduce one additional quality requirement for learners to incorporate and test?

### Confirmed guided rubric change

The requester confirmed: "Yes, we should." The lab will supply one additional quality requirement for learners to incorporate into the rubric and test. Exact requirement wording and the edit workflow remain open.

The coach recommends keeping the supplied answers unchanged for this comparison, so learners can see the effect of changing the criteria rather than confuse it with an agent improvement. This comparison detail is a recommendation, not a separately approved exercise design. Do not promise that a new requirement will change every score or create a failure.

The working Criteria First journey is now: supplied priorities and policy, automatic rubric generation, human review, evaluation of supplied answers with rubric and built-in checks, a supplied additional requirement and rubric revision, then separate live-agent improvement and production evaluation. Final concept selection and three-lens validation remain open.

### Built-in introduction before rubric generation

The requester corrected the proposed sequence: introduce built-in evaluators before generating a rubric, so learners understand the built-in checks first.

This introduction comes before automatic rubric generation. It explains what the selected built-in evaluators measure and where domain-specific criteria add value. Learners still use built-in evaluators hands-on with the supplied answers; the requester has not specified that a scored run must precede rubric generation.

Criteria First now means establishing the domain rubric before the main supplied-answer comparison, not placing rubric generation before every introduction to evaluation. Evidence First still differs by using scored supplied-answer results to motivate the rubric. Neither concept is finally selected. The revised sequence does not add a separate module or increase the untested time budget.

### Simple built-in run before rubric generation

The requester then asked: "Shouldn't we try a simple built-in evaluator run before building the rubric?" The working journey now includes an actual built-in evaluation run on supplied answers and inspection of its result before rubric generation, not just a conceptual introduction.

This supersedes the introduction-only interpretation above. It combines the practical opening of Evidence First with the guided generation and review developed under Criteria First. The original ordering distinction has converged; do not ask the requester to choose between those original openings again.

Use the first result to explain what the selected built-in check measures and what it does not establish. Do not promise that it will pass a bad answer or fail a good answer to create a contrast. Learners then generate a domain rubric from the lab-supplied priorities and policy, review it, and compare its judgments with built-in results.

The initial run stays within the existing proposed first-run activity, not a new module. Exact evaluator selection, elapsed timing, technical execution, and final concept selection remain unverified. Earlier three-lens comparison questions about generating a rubric before any result are historical and need review against this combined journey.
