# Working evidence clusters

## Status

These clusters organize the user-approved learning gap. Consolidated insights are in `insight-statements.md`; the five-dimension assessment is in `problem-definition.md`. The user authorized a draft PRD, not a declaration that all themes are validated. Source labels remain anonymous.

The two practitioner perspectives are distinct, but both are available only through requester-supplied excerpts. The requester, the excerpts, and their summaries must not be counted as extra independent practitioner sources.

## Cluster 1: Explain quality through customer value

Evidence:

- Practitioner A describes customer judgment during pilots.
- Practitioner B describes adoption, time saved, and correction effort as quality signals.
- The requester says the first-run outcome is understanding evaluation and explaining its value to the customer and solution.

Source pointers: `practitioner-evidence.md`, evidence register; `input-inventory.md`, first-run outcome.

Working interpretation: an evaluation score needs a clear connection to what matters to the customer. Technical checks do not replace understanding whether the solution helps users.

Tension: perceived usefulness and acceptable behavior may differ. The excerpts do not establish which failures customers consider unacceptable even when the agent otherwise saves time.

Evidence strength: supported by both practitioner perspectives and requester intent. No direct customer validation or measured relationship between scores and user benefit.

## Cluster 2: Make expectations repeatable without arbitrary targets

Evidence:

- Practitioner A reports semantic comparisons for relatively predictable outputs, customer judgment in pilots, and no formal suite.
- In a follow-up, Practitioner A expresses interest in a lab showing a more formal approach. This is prompted feedback from the same source, not independent evidence or measured learning benefit.
- Practitioner B identifies evaluations for model and instruction changes, and encourages investigating failures rather than using arbitrary percentages.
- The requester approved translating customer expectations into repeatable evaluation checks and explaining evidence limits.

Source pointer: `practitioner-evidence.md`, evidence register and user-approved gap.

Working interpretation: learners need to connect an expectation, a check, and the meaning of its result. A numerical target alone does not explain the importance or consequences of a failure.

Tension: repeatability should not imply that every response must be identical, or that all failures have equal importance. Specific acceptance rules are not yet agreed.

Evidence strength: both practitioners describe assessment approaches, but only one explicitly discusses arbitrary targets and lifecycle checks. Practitioner A expresses perceived value in more formal evaluation learning. The learning gap is requester-approved; the proposed approach has not been tested with learners.

## Cluster 3: Keep evidence useful after handover

Evidence:

- Practitioner B recommends creating evaluations during the project and handing them over, with failure investigation supported by a managed service when applicable.
- The requester wants reusable evaluation assets for development, changes, operations, and customer handover.
- The requester approved the gap of handing checks over for use after solution changes.
- The requester, a Microsoft Solution Architect helping partners build capability and successful customer solutions, clarified that evaluation should be handed over as reusable assets and processes, comparable to test automation and smoke tests.
- The requester expects a partner-provided method for local development runs, CI/CD build or deployment runs, and regular production evaluation. Customers, internal teams, or another partner should be able to continue checking changes against agreed quality gates.

Source pointers: `practitioner-evidence.md`, evidence register and user-approved gap; `..\resume-notes.md`, confirmed direction.

Working interpretation: handover should preserve a repeatable quality-assurance capability, not merely provide an earlier score. The customer need not personally maintain every check; the capability should remain usable by the team responsible for subsequent work.

Tension: the requester has specified the intended practice across three execution contexts. CI/CD execution is explicitly optional extra credit, to avoid adding a CI platform as a core learning requirement. A real GitHub Actions evaluation workflow against the lab-deployed agent is required for that extension, with fork and configuration setup to be explored. Production evaluation is explicitly hands-on in the core and must not depend on the CI/CD extension. Specific ownership, maintenance, production cadence, and decisions after a failed gate remain context-dependent.

Evidence strength: one practitioner perspective plus an explicit requester requirement. The requester's comparison with existing test-automation handover describes their expectation, not independently observed partner practice. Independent operator and customer evidence is missing.

## Constraints carried forward

The first evaluation run has an introductory outcome. Later learning covers interpretation, rubric creation, investigation, improvement, and reusable handover. These are requester requirements, not all independently discovered practitioner needs.

Primary evaluation learning must remain possible when secondary Optimizer or red-team activities are blocked by deployment conditions. Status reporting must distinguish blocked, unverified, failed, and completed activities. This is an agreed delivery constraint, not a practitioner theme.

## Teaching candidates and agreed outcomes

The requester clarified that this is a teaching lab, not a production flight-disruption service. They accepted the proposed examples and documented evaluator fit as a working direction. Airline expertise is not required: supplied fixtures, read-only scope, and fictional policy define the exercise expectations.

| Teaching candidate | Proposed evaluator fit | Evidence needed |
|---|---|---|
| Recommends two seats for four passengers without explaining the shortfall | Tool Output Utilization and a group-feasibility rubric | Passenger request, tool results, and explicit criterion |
| Claims a booking is confirmed despite read-only capabilities | Task Adherence (preview) and an unsupported-action-claim rubric | System instructions, tool definitions, and conversation including tool calls/results |
| Promises a hotel or refund unsupported by fictional policy | Groundedness and a policy-compliance rubric | Fictional policy supplied to the evaluator and response |
| Lists accurate options without explaining relevant trade-offs | Decision-support rubric, with Relevance as a broader check | Criteria for explaining relevant time, cabin, and group trade-offs |

This is documented suitability, not verified scoring behavior. Tool Call Accuracy checks tool choice and parameters; it does not replace checking use of tool results. A weighted rubric score must not be assumed to fail overall whenever one important criterion fails.

Official references:

- [Agent evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators)
- [RAG evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)
- [Rubric evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators)

The proposed small live evaluator test belongs in Method 7 technical feasibility work: compare known acceptable and unacceptable answers using the intended judge, inputs, and rubric. Method 6 can first review example clarity and expected judgments without a live integration. Method 8 tests whether representative learners can use the working lab. This placement does not authorize cloud jobs or a method transition.

Cluster 3 now has a clarified outcome: future teams can repeat evaluations and check changes against quality gates through local, CI/CD, and regular production execution. CI/CD execution is optional extra credit with a real repository workflow, not a core prerequisite. Production evaluation is hands-on core work. See `..\implementation-plan.md`, optional CI/CD exploration scope, for initial repository observations and open setup questions.

The user accepted the core production-evaluation outcome: learners identify a quality failure in live agent activity, inspect the supporting conversation or trace, and explain what needs investigation. Use the deployed lab agent with synthetic passenger requests; no real customer production system is required.

This defines the learner capability and safe exercise setting, not a selected monitoring implementation, verified detection result, or authorization to configure services. The consolidated insights and problem framing now inform `..\prd.md`; its scope and proposed acceptance detail need requester review.

The requester subsequently confirmed bounded Method 3 closure and the move to Method 4. Use these clusters as working design inputs, not fully validated themes or an approved module implementation. The closure assessment is in `problem-definition.md`.
