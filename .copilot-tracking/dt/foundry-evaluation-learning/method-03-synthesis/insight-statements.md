# Synthesis insights

## Status and source use

These insights consolidate the discussion for draft requirements authoring. They do not establish training effectiveness or a production-ready solution. Source labels are anonymous. Repeated excerpts and derived notes do not count as additional independent sources.

## INS-001: Evaluation needs a customer-value explanation

Practitioner A describes customer judgment in pilots. Practitioner B describes adoption, time saved, and correction effort. The requester wants learners to explain what evaluation provides and why it matters before requiring independent diagnosis.

Insight: learners need to connect evaluation evidence to a customer expectation, not simply report a score.

Implication: the initial outcome should include explaining what was checked, why it matters, and what the result cannot establish.

Source: `practitioner-evidence.md`, evidence register; `input-inventory.md`, first-run outcome.

Confidence: supported by both practitioner perspectives and requester intent. No direct customer evidence or measured link between scores and customer value.

## INS-002: Repeatable checks complement human judgment

Practitioner A reports semantic comparisons and informal pilot feedback, without a formal suite, and expresses interest in a more formal approach. Practitioner B identifies lifecycle checks and rejects arbitrary percentage targets.

Insight: the learning opportunity is to translate expectations into repeatable checks with understandable reasons and limits, not to replace every human judgment with a number.

Implication: learners should inspect known good and bad cases, revise rubric criteria, investigate failures, and distinguish tool-call correctness from use of tool results. The lab must not assume a high weighted average cancels an important failure.

Source: `practitioner-evidence.md`; `affinity-clusters.md`, Cluster 2 and teaching candidates.

Confidence: differing practitioner approaches support the problem framing. The specific teaching method and evaluator behavior remain untested.

## INS-003: Handover transfers a capability, not a historical score

Practitioner B recommends evaluation creation and handover. The requester explicitly expects reusable assets and processes, comparable to test automation, for future customer, internal, or partner teams.

Insight: evaluation evidence must remain usable when the original project team is no longer responsible.

Implication: cover development, changes, and production. Hands-on production evaluation is core; CI/CD execution is optional extra credit with a real repository GitHub Actions workflow. These scope choices are requester requirements, not additional practitioner findings.

Source: `practitioner-evidence.md`; `affinity-clusters.md`, Cluster 3; `..\implementation-plan.md`, confirmed decisions.

Confidence: one practitioner perspective plus an explicit requester requirement. Consistent handover practice and customer/operator capability are unverified.

## Requester requirement: Evaluate while building

Delivery engineers need evaluations early in delivery so they can repeatedly assess how their changes affect the system. The requester compares this feedback cycle to TDD and places evaluation capability throughout the product development lifecycle.

Design implication: connect an explicit non-functional quality requirement to evaluation criteria, establish a baseline early, and rerun checks as the solution changes. Evaluation provides evidence about meeting the requirement; a score alone does not establish compliance.

Source: requester clarification recorded in `..\coaching-state.md`. This is a confirmed learning requirement, not a fourth independently validated research insight. Local execution must support the cycle without making optional CI/CD a prerequisite.

## Requester objective: Microsoft Foundry capability and awareness

The requester wants learners to understand evaluation principles and gain practical experience with how Microsoft Foundry implements them. Partner engineers, consultants, and architects should be able to explain the Microsoft features they used and their value in customer solutions.

Design implication: connect each core evaluation activity to the Foundry feature, actual result, and quality need it supports. Do not require a third-party evaluation platform for core completion. Feature awareness must come from hands-on use, not only product descriptions.

Source: requester objective recorded in `..\coaching-state.md`. This is a product-learning requirement, not an independently observed awareness gap or a claim that external platforms are never needed. Retain accurate feature, environment, and coverage limits.

## Cross-cutting delivery boundary

The flight assistant is a teaching vehicle with synthetic requests, read-only tools, and fictional policy. Do not require airline expertise, real-world legal advice, or a customer production system. Preserve core learning when secondary Optimizer or red-team activity is blocked by an evidenced deployment condition.

This boundary is confirmed requester intent, not a discovered industry pattern. The preferred hosted-agent path, production-evaluation mechanism, and complete SDK/model/identity integration remain feasibility questions.
