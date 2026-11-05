# Coaching state

```yaml
project:
  name: "Foundry Evaluation Learning"
  slug: "foundry-evaluation-learning"
  created: "2026-11-03"
  initial_request: |-
    Would it be better to make a standalone lab that explores evaluation and evaluators, moving into Rubric Evaluators and AI Red-teaming and then the Agent Optimizer?
    https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview
    https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators
    https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent
    https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-overview

    We could explore and use the different types of evaluators and how we can run them and use them in our development and operational workflows and then how to use them to improve our agents automatically.

    Let's explore that
  initial_classification: "frozen"

current:
  method: 3
  space: "problem"
  phase: "working synthesis baseline; early evaluation and explicit Microsoft Foundry capability objective captured; closure decision pending"
  disclaimerShownAt: "2026-11-03T11:37:26.065+13:00"

methods_completed: [1, 2]

transition_log:
  - from_method: null
    to_method: 1
    rationale: "User explicitly requested Method 1 before further lab design."
    date: "2026-11-03"
  - from_method: 1
    to_method: 2
    rationale: "User explicitly confirmed moving to Method 2. Intended learners, learning outcomes, and boundaries are scoped. Research must now test partner-practice and customer-confidence hypotheses; those are not validated findings."
    date: "2026-11-03"

  - from_method: 2
    to_method: 3
    rationale: "User confirmed starting Input Synthesis using requester decisions, repository observations, and official documentation. Method 2 outputs are sufficient for this transition; partner validation and live feasibility remain unresolved and are not marked validated."
    date: "2026-11-04"

hint_calibration:
  level: 1
  pattern_notes: "User wants discussion of learning needs before technical decisions. Ask one open question at a time."

session_log:
  - date: "2026-11-05"
    method: 3
    summary: "User requested persistence, commit, and push of all current session work. Save the draft PRD, synthesis, anonymous practitioner evidence, industry research, and recovery notes on the existing branch. Latest agreed objective includes hands-on Microsoft Foundry capability and product-value awareness. Industry sources support early repeated evaluation and a qualified TDD analogy, not universal adoption or learner effectiveness. This checkpoint does not approve Method 4, implementation, cloud jobs, or access changes."
  - date: "2026-11-05"
    method: 3
    summary: "User added an explicit objective: introduce evaluation principles and practice through hands-on Microsoft Foundry feature use, increasing partner engineer/consultant awareness and their ability to communicate Microsoft product features and solution value. Core completion must not depend on a third-party evaluation platform. Added GOAL-004, FR-019, AC-019 and traceability to the draft PRD, plus synthesis framing. This does not claim universal Foundry coverage, partner awareness gaps, or platform superiority. Method 3 closure and Method 4 transition remain pending; no implementation authorized."
  - date: "2026-11-05"
    method: 3
    summary: "User clarified delivery-engineer needs: adopt evaluations early and evaluate while building, like TDD feedback, to assess how changes affect the system and verify non-functional requirements throughout product development. Recorded as requester intent, not independent practitioner evidence. Updated synthesis and draft FR-003/AC-003 to link a quality requirement, criteria, baseline, repeated local runs, and decisions. CI/CD remains optional. No implementation or method transition."
  - date: "2026-11-05"
    method: 3
    summary: "User accepted the working design baseline and evidence limits, subject to including delivery engineers building solutions and architects designing solutions as equal audiences to consultants. Updated the problem statement and draft PRD role descriptions. Role-specific difficulties remain design interpretations pending clarification, not new practitioner evidence. This closes the synthesis round only as a working baseline; full validation, a Method 4 transition, and implementation are not claimed."
  - date: "2026-11-05"
    method: 3
    summary: "User authorized consolidating Method 3 and creating a draft PRD. Added evidence-linked insights, problem definition with five-dimension assessment, HMW questions, PRD 0.1.0, and PRD authoring state. Synthesis documentation is consolidated, but missing direct learner/customer/operator evidence prevents claiming full Method 3 validation. Remain in Method 3; no Method 4 or validated RPI handoff. PRD acceptance detail is proposed, not signed off. No implementation or cloud jobs."
  - date: "2026-11-05"
    method: 3
    summary: "User accepted the production-evaluation learning outcome: identify a quality failure in live agent activity, inspect the supporting conversation or trace, and explain what needs investigation. Accepted use of the deployed lab agent with synthetic passenger requests; no real customer production system is required. This is an agreed outcome, not verified exercise behavior. Method 3 remains active."
  - date: "2026-11-05"
    method: 3
    summary: "User explicitly requires hands-on production evaluation in the core. Updated current planning and synthesis notes; optional CI/CD must not gate this exercise. Exact production-evaluation outcome, execution mechanism, and cadence remain open. No deployment, monitoring configuration, evaluation run, or method transition occurred."
  - date: "2026-11-05"
    method: 3
    summary: "User excludes CI/CD execution from core completion because it adds another technology. Requires an optional extra-credit module and real GitHub Actions evaluation workflow against the lab-deployed agent, with fork/environment setup to explore. Inspected existing smoke, provisioning, and E2E workflow patterns; recorded bounded setup and feasibility questions without implementing a workflow, changing access, or running jobs. Production-evaluation hands-on depth remains open."
  - date: "2026-11-05"
    method: 3
    summary: "Requester clarified their Microsoft Solution Architect role and the intended partner practice: hand over reusable evaluation assets and processes, like test automation, so customers, internal teams, or another partner can check later changes against quality gates. Methods should support local development, CI/CD build/deployment, and regular production runs. Recorded as a requester requirement, not evidence that these practices are consistently delivered. Workshop hands-on depth across the three contexts remains open. Method 3 continues."
  - date: "2026-11-04"
    method: 3
    summary: "User clarified this is a teaching lab, not a production flight service, and accepted the proposed examples after reviewing documented evaluator fit. Recorded provisional examples and limitations in the clusters. The small live scoring test fits Method 7 technical feasibility; Method 6 can review example clarity and Method 8 tests learner use. Remain in Method 3 and clarify the desired customer capability after handover. No live test or method transition is authorized."
  - date: "2026-11-04"
    method: 3
    summary: "Requester supplied a follow-up from Practitioner A expressing interest in a lab showing a more formal evaluation approach. Recorded anonymously as perceived value in response to a suggested lab, not measured learning benefit or a third independent source. Updated the repeatable-checks cluster. The pending question about unacceptable flight advice remains open."
  - date: "2026-11-04"
    method: 3
    summary: "User requested continuing Method 3. Organized working clusters around customer value, repeatable checks without arbitrary targets, and evidence use after handover. Marked source strength and tensions separately; lifecycle handover has only one practitioner source plus requester intent. Next discussion clarifies essential customer expectations without selecting metrics or implementing a rubric."
  - date: "2026-11-04"
    method: 3
    summary: "Requester supplied two practitioner conversation excerpts and approved capturing the gap with people names omitted. Saved anonymous paraphrases without company names or full transcripts. Evidence shows differing practices, not a general lack of evaluation knowledge. User approved the gap of turning customer expectations into repeatable checks, explaining evidence limits, and handing checks over for later changes. No WorkIQ verification, Method 4 transition, or implementation occurred."
  - date: "2026-11-04"
    method: 3
    summary: "User clarified the first-run outcome: Have a general idea of what an evaluation is and be able to explain what it provides for a customer and agentic AI solution and why it's important to provide. Recorded this as a requester requirement, not partner validation. Independent diagnosis remains a later track goal rather than a required first-run outcome."
  - date: "2026-11-04"
    method: 3
    summary: "User approved Method 3. Created an input inventory with source types, coverage gaps, and a synthesis approach. Beginning candidate-theme discussion without treating requester requirements as validated partner findings. No Method 4 transition, lab implementation, or cloud jobs are approved."
  - date: "2026-11-04"
    method: 2
    summary: "Resumed from the repository checkpoint. User requested the findings summary and clarified that using/running evaluations is primary; Optimizer and red-team evaluations are secondary and may be blocked by deployment conditions without preventing primary completion. Partner outreach continues with no replies recorded. Updated active requirements while retaining historical quotations. No method transition or implementation is approved."
  - date: "2026-11-03"
    method: 2
    summary: "User requested persistence, commit, and push before pausing. All five DT assets and the working plan are now stored in the repository with a resume note. This authorizes saving planning documents only, not lab implementation, deployments, paid jobs, or a method transition."
  - date: "2026-11-03"
    method: 2
    summary: "User challenged conflation of agent red teaming with testing a tool server. Re-read the full official support/limitations sections and searched for explicit clarification; no source settled custom remote MCP handling. Corrected the broad blocker framing: distinguish response-level agent scans, tool-mediated simulation/coverage, and backend service security. The matrix concerns agents with tool calls, but does not state whether an unsupported tool rejects an entire run or limits specific tests."
  - date: "2026-11-03"
    method: 2
    summary: "User asks how to establish cloud red-team support. Rechecked official concept matrix and cloud SDK guide. Proposed precise product-team clarification plus a later authorized incremental feasibility test: hosted baseline, flight MCP, then knowledge/toolbox. A completed job alone is insufficient; verify tool coverage, skipped cases, and synthetic versus real execution. No cloud requests or paid jobs were submitted."
  - date: "2026-11-03"
    method: 2
    summary: "User confirmed fictional airline policy and exclusion of real-world legal-entitlement advice. The working scenario is passenger-facing, read-only flight-disruption advice. Existing rights-focused knowledge is not assumed suitable. Continue Method 2 with fixture and technical feasibility gaps; no implementation or method transition is authorized."
  - date: "2026-11-03"
    method: 2
    summary: "User chose passenger-facing advice for the working flight-disruption scenario. Read-only scope remains unchanged. Next clarification is whether policy grounding should use reviewed fictional airline policy rather than real-world legal entitlements. Method 2 remains active; implementation is not authorized."
  - date: "2026-11-03"
    method: 2
    summary: "User selected flight disruption as the working scenario for now. General retail remains a parked alternative, not a second implementation. Continuing Method 2 to clarify the agent's intended user and task boundary; no repository implementation, deployment, or method transition is authorized."
  - date: "2026-11-03"
    method: 2
    summary: "User requested exploration of flight disruption while retaining general retail without ACL as a comparison. Inspected both MCP implementations and retail fixtures; passenger knowledge contains 12 rights-focused documents. Compared observable correctness, tool use, domain rubric value, ambiguity, cost-quality decisions, and preparation effort. Flight has a provisional advantage for the complete evaluation journey; retail has a simpler entry point. Neither is selected, and no dataset or cloud run was created."
  - date: "2026-11-03"
    method: 2
    summary: "User asks whether another existing agent would be preferable to the Australia-centric ACL scenario. Inspected Trip Disruption Concierge and Contoso Outdoors examples. Travel has reusable flight MCP fixtures but also passenger-rights scope and a claim-submission tool; Contoso Outdoors is a lightweight retail prompt rather than a complete grounded agent. Comparing scenario suitability only; no replacement has been approved."
  - date: "2026-11-03"
    method: 2
    summary: "Continued hosted knowledge/tool research. Official FoundryToolbox integration provides a documented authentication route but not verified custom MCP red-team support. Read-only fixture parsing found 100 Search products, 50 Search policies, and zero Search-ID matches for three primary MCP products. Sample Search data uses USD grocery context while MCP uses AUD electronics. Existing assets cannot be assumed to form an evaluation-ready scenario."
  - date: "2026-11-03"
    method: 2
    summary: "User says subscription Optimizer access cannot be known in advance and may require partner/customer requests. They note possible future GA or stale docs. Rechecked overview: no allowlisting statement there, unlike hosted quickstart. Recorded access uncertainty as dynamic readiness evidence rather than a reason to force prompt agents; no future release is assumed."
  - date: "2026-11-03"
    method: 2
    summary: "User paused the prompt-agent proposal and asked to decide hosted-agent suitability first, citing product investment direction. Reviewed official hosted optimization, runtime integration, evaluator, and hosting guidance plus existing Modules 09 and 10. Hosted rubric/model optimization is documented; subscription allowlisting, runtime/tool identity, and custom MCP red-team support are feasibility gates. Architecture is not yet confirmed."
  - date: "2026-11-03"
    method: 2
    summary: "User agreed to focused rubric-to-Optimizer and cloud red-team desk research. Official portal docs support rubric selection/creation and model comparison for prompt agents without the Copilot harness. Confirmed judge/optimizer model-role differences and locked SDK 2.7.0 versus rubric example >=2.8.0. Custom MCP red-team compatibility remains unresolved; no cloud jobs were run. Partner validation remains deferred."
  - date: "2026-11-03"
    method: 1
    summary: "Starting Scope Conversations. Earlier module proposals are not validated learner needs. Learner role, current difficulties, and stakeholder evidence remain to be established."
  - date: "2026-11-03"
    method: 1
    summary: "User identified technical builders and operators of Azure agentic solutions, often at Microsoft Systems Integrator partners. User reports customer quality gates are often poorly defined and rely on informal testing. Exploring the resulting uncertainty before defining the learning problem."
  - date: "2026-11-03"
    method: 1
    summary: "User clarified their Microsoft Partner team perspective. They hypothesize that unclear evaluation reduces customer confidence and delays release or commitment. They have asked partners about evaluation in solution proposals; actual partner practice and responses are not yet established."
  - date: "2026-11-03"
    method: 1
    summary: "User supplied their outreach question and requested a question for other partners. Proposed an experience-based prompt about a recent project, with a follow-up about a difficult quality decision. No partner responses have been supplied."
  - date: "2026-11-03"
    method: 1
    summary: "User confirmed partner questions have been sent and no responses have arrived. User requested continued exploration. Continuing active coaching within Method 1; partner needs and commercial impact remain hypotheses. Exploring the desired change in the learner's customer conversation."
  - date: "2026-11-03"
    method: 1
    summary: "User defined the desired consultant capability: propose evaluation of solution quality and reliability as part of normal software quality practice. User suggested an evaluation suite as a delivery handover artifact, usable during development, after updates such as model changes, and for continuous production evaluation. Exploring who would use and interpret that suite after handover."
  - date: "2026-11-03"
    method: 1
    summary: "User identified multiple operating models: SI-managed operations, enterprise customer product or delivery managers and operations teams, and smaller customer outsourced IT or a solution-owning SME. No single post-handover role should be assumed. Exploring the expected response to an evaluation failure."
  - date: "2026-11-03"
    method: 1
    summary: "User stated that evaluation should help the responsible person know what to change in the agent, or at least where to investigate. This establishes diagnosis and actionability as desired outcomes beyond quality scores. Clarifying whether learners must complete and verify a correction within the lab."
  - date: "2026-11-03"
    method: 1
    summary: "User requires learning how to improve at least one quality aspect, not exhaustive coverage. They suggested groundedness and representative quality and agent evaluator examples. Reviewed the supplied official agent-evaluation guide and evaluator references. Exact examples remain proposals; exploring prior learner testing and evaluation experience."
  - date: "2026-11-03"
    method: 1
    summary: "User clarified learners understand evaluation in principle but likely lack practical experience. They understand Foundry, agents, and app design/building, but may be presales or solution architects rather than engineers. Exploring whether every core exercise must be completable without writing Python."
  - date: "2026-11-03"
    method: 1
    summary: "User confirmed no Python authoring is required for core completion. Supplied Python scripts may be required to run evaluations or create assets, and their source must remain visible for engineers. This is not a portal-only constraint. Exploring facilitated versus independent delivery needs."
  - date: "2026-11-03"
    method: 1
    summary: "User confirmed both facilitated and independent delivery must be supported. Preparing a conversational scope recap for confirmation, without finalizing module design or claiming partner needs are validated."
  - date: "2026-11-03"
    method: 1
    summary: "User clarified mandatory progression to rubric evaluator creation and use with Agent Optimizer. Desired optimization outcome is lower agent cost while maintaining quality, not merely a higher score. Clarifying whether cost means agent runtime cost, evaluation cost, or both."
  - date: "2026-11-03"
    method: 1
    summary: "User identified cost reduction as the primary optimization goal, with quality and rubric-adherence improvements as secondary outcomes. Treat this as the desired workshop priority, not a claim that the product ranks by cost. Clarifying what maintaining quality means for candidate acceptance."
  - date: "2026-11-03"
    method: 1
    summary: "User set the default to matching or exceeding baseline quality, while allowing a customer to accept a slight quality reduction for a large cost reduction. Capture this as an explicit customer decision, not an automatic relaxation of thresholds. Exploring required red-team participation depth."
  - date: "2026-11-03"
    method: 1
    summary: "User requires each learner to run a small red-team exercise and supplied local and cloud documentation. Official local guide states incompatibility with the new Foundry portal and SDK. Cloud is the recommended candidate path, pending region and target/tool compatibility verification. Returning to Method 1 scope confirmation; no method transition has occurred."

artifacts:
  - path: ".copilot-tracking/dt/foundry-evaluation-learning/method-03-synthesis/insight-statements.md"
    method: 3
    type: "synthesis-insights-with-evidence-limits"
  - path: ".copilot-tracking/dt/foundry-evaluation-learning/method-03-synthesis/problem-definition.md"
    method: 3
    type: "problem-definition-and-readiness-assessment"
  - path: ".copilot-tracking/dt/foundry-evaluation-learning/method-03-synthesis/how-might-we-questions.md"
    method: 3
    type: "how-might-we-questions"
  - path: ".copilot-tracking/dt/foundry-evaluation-learning/prd.md"
    method: 3
    type: "draft-prd"
  - path: ".copilot-tracking/dt/foundry-evaluation-learning/prd-state.md"
    method: 3
    type: "prd-authoring-state"
  - path: ".copilot-tracking/dt/foundry-evaluation-learning/method-03-synthesis/affinity-clusters.md"
    method: 3
    type: "working-affinity-clusters"
  - path: ".copilot-tracking/dt/foundry-evaluation-learning/method-03-synthesis/practitioner-evidence.md"
    method: 3
    type: "anonymous-practitioner-evidence-and-agreed-gap"
  - path: ".copilot-tracking/dt/foundry-evaluation-learning/method-03-synthesis/input-inventory.md"
    method: 3
    type: "synthesis-input-inventory"
  - path: ".copilot-tracking/dt/foundry-evaluation-learning/method-02-research/findings-summary.md"
    method: 2
    type: "findings-summary"
  - path: ".copilot-tracking/dt/foundry-evaluation-learning/resume-notes.md"
    method: 2
    type: "session-handoff"
  - path: ".copilot-tracking/dt/foundry-evaluation-learning/implementation-plan.md"
    method: 2
    type: "working-plan"
  - path: ".copilot-tracking/dt/foundry-evaluation-learning/method-02-research/constraint-catalog.md"
    method: 2
    type: "constraint-catalog"
  - path: ".copilot-tracking/dt/foundry-evaluation-learning/method-01-scope/stakeholder-map.md"
    method: 1
    type: "stakeholder-map"
  - path: ".copilot-tracking/dt/foundry-evaluation-learning/method-01-scope/scope-boundaries.md"
    method: 1
    type: "scope-boundaries"
  - path: ".copilot-tracking/dt/foundry-evaluation-learning/method-01-scope/assumptions-log.md"
    method: 1
    type: "assumptions-log"

confirmed_context:
  - "Use clearly labelled fictional airline policy for the passenger-facing flight-disruption scenario. Real-world legal-entitlement advice is outside the lab's scope."
  - "The flight-disruption agent should advise passengers directly, rather than serve airline support staff."
  - "User selected the flight-disruption scenario for now. Treat this as a provisional scenario decision; general retail is a parked alternative and ACL is no longer the active scenario."
  - "Separate track with focused modules; preserve existing introduction-track numbering."
  - "Target capability: Run evaluations and use the evidence to make an agent release decision."
  - "Assume basic Foundry agent skills; attendees need not complete the introduction track."
  - "Core scope includes grounded advice and read-only MCP tool use."
  - "User wants existing lab environment provisioning reused."
  - "User suggested attendees create their agent, possibly through Python, then try it."
  - "User selected a focused HVE DT Coach session and explicitly requested Method 1."
  - "User describes learners as application software engineers, architects, AI engineers, and people building and operating agentic AI solutions on Azure, often at Microsoft Systems Integrator partners."
  - "User describes informal customer testing as a possible weakness in quality gates; actual partner practices remain unverified."
  - "User works on the Microsoft Partner team and has asked partners about evaluation in solution proposals."
  - "Desired learner capability includes proposing how a customer can evaluate the quality and reliability of the agent or AI solution, alongside normal application quality and automated testing practices."
  - "User proposes a reusable evaluation suite as a solution handover artifact, supporting development, updates such as model rollouts, and day-to-day continuous production evaluation."
  - "User identifies SI-managed operations when customers delegate operation or lack the capability or wish to operate the solution."
  - "User identifies enterprise handover recipients as product managers, delivery managers, or operations teams who receive guidance."
  - "User identifies smaller-organization recipients as outsourced IT or a solution-owning SME."
  - "User expects evaluation results to help the responsible person identify what to change in the agent, or at least where to investigate."
  - "Learners must learn how to improve at least one particular quality aspect; exhaustive improvement across all possible rubric criteria is not required."
  - "User suggested groundedness and examples from both quality and agent evaluators."
  - "Learners know evaluation is how agentic or AI solutions are tested, but likely have no practical evaluation experience."
  - "Learners have basic Foundry, agent, and application design or building knowledge."
  - "The audience includes presales and solution architects, not only engineers. Python authoring skill must not be assumed without agreement."
  - "Core exercises must be completable without writing Python."
  - "Running supplied Python scripts for evaluations and asset creation is acceptable in the core."
  - "Python source must be shown or available so engineers can inspect the implementation."
  - "Both facilitated and independent completion must be supported."
  - "Evaluation learning, including rubric creation, is primary. Agent Optimizer is a secondary learning activity; a deployment block must be reported without preventing primary completion. This supersedes its earlier unconditional core requirement."
  - "Learning must build toward optimizing agent cost while maintaining quality as measured by evaluations."
  - "User prioritizes cost reduction for optimization, with improved quality and rubric adherence as secondary outcomes."
  - "Default optimization acceptance should match or exceed baseline quality."
  - "User allows explicit customer acceptance of a slight quality reduction for a large cost reduction. No numerical trade-off rule has been agreed."
  - "A small hands-on red-team exercise remains in scope as a secondary activity. Deployment blocks must not prevent primary completion. Do not label blocked, unverified, or failed secondary work as executed."
  - "No previous lab completion or previously created agent, knowledge base, or connection may be assumed. The track must create its required assets from the provisioned workshop starting state."
  - "Reuse setup patterns from existing labs, not their presumed deployed end state."
  - "Notify learners when their deployed region does not support a module or feature, but do not block the whole track."
  - "The organizer may require a particular region; do not assume relocation is permitted."
  - "Allow deployment of a smaller model for cost comparison; automatic deployment remains a possibility to decide."
  - "Plan for ongoing maintenance as models are released and updated."
  - "User agrees with organizer-controlled comparison-model provisioning."
  - "Self-hosted individual setup should work with simple defaults and reuse the current deployment process."
  - "Support multiple lab tracks in one environment and later additions if the process and requirement management can remain simple. Requirements must be data driven."
  - "The track catalog must stay current and its use must distinguish individual self-organized labs from organizer-run multi-user labs."
  - "User confirms East US 2 as the recommended default as part of the planned work. Other regions remain selectable, with module-specific limitations documented through data-driven catalog guidance. Existing environments must not be relocated automatically."
  - "User recommends Global Standard model deployments for labs; feature-region and model/quota checks remain separate."
  - "User proposes a configuration-script post-deployment summary of module availability. Recommended design uses catalog requirements and observed prerequisites, with explicit limitations and no claim that exercises have been completed."
  - "User asks to pause prompt-agent design and determine whether the entire new track should use hosted agents first. User reports product investment moving toward hosted agents; public deprecation has not been established."
  - "Target subscription Optimizer access is unknown and may require partner/customer requests. Possible future GA or stale documentation is not confirmed. Do not block hosted-agent planning solely on this uncertainty."

stakeholder_evidence:
  - source: "User's revised priorities and handling of secondary deployment blocks; supersedes earlier unconditional Optimizer and red-team completion requirements."
    quote: |-
      The primary goal is learning to use/run evals. Secondary is Agent Optimizer and red-team evals. So, as long as we can achieve primary, but can tell the lab user when secondaries are blocked because of some lab deployment condition then I think this is ok
  - source: "User's assessment of likely partner practice, not verified evidence."
    quote: |-
      will be difficult to achieve as I don't think any/many or our partners are even running evaluations - but I'm checking with them.
  - source: "User confirmation of the policy-grounding boundary."
    quote: |-
      Yes. Let's avoid real-world legal-entitlement advice.
  - source: "User selection of the flight-disruption agent's intended user."
    quote: |-
      I think it should advise passengers
  - source: "User's provisional scenario selection."
    quote: |-
      Yes, let's use the flight disruption scenario for now.
  - source: "User account of intended learners and current release practice; not independently validated."
    quote: |-
      They are an application software engineer, architect, AI engineer or someone operating and building Agentic AI solutions on Azure. They will often be at a Microsoft Systems Integrator partner. They will decide to release when it meets some customer defined quality "gate" (that is often not defined well - it's just "the customer tested it and it looks OK".).
  - source: "User explanation of expected business impact and limits of their knowledge."
    quote: |-
      I expect it's the customer having confidence in the agent and therefore will delay release or possibly delay commitment to the solution. E.g. if the customer doesn't know how to evaluate an agent then they might not have enough confidence to buy into the solution. So including the evaluation methodology in the solution may also facilitate the sale and deliver a higher quality outcome. But I am on the Microsoft Partner team, so I don't know exactly what/whether all partners include evaluations as part of a solution proposal (e.g. "Agent will meet this quality metric based on these evaluations"). I've asked.
  - source: "User's outreach question to a partner; this is a question, not evidence of partner practice."
    quote: |-
      Hey [name omitted], I'm working on building out a lab to show Rubric evaluators and Agent Optimizer and was thinking about the problem: Is providing agentic evaluations/quality milestones & gates part of your typical sales/delivery? E.g., would it be useful for your consultants to include Agentic quality/evaluation metrics in sales proposals/RFPs to win the deal?
  - source: "User statement of desired learner capability and proposed delivery outcome, not observed partner practice."
    quote: |-
      They should be able to propose how the customer can evaluate the quality and reliability of the agent/AI solution - just as they'd do with traditional quality/automated testing of a typical application being delivered. Evaluation suite might be considered an artefact that is handed over as part of the delivery so and can be run in both day to day operations (continuous production evaluation) as well as when updates are made (e.g. a new model is rolled out) and during development
  - source: "User description of expected operating and handover models; specific partner examples remain pending."
    quote: |-
      In some cases it will still be the systems integrator because the customer might not wish to or have the capability to do this and the operation of the system will be delegated to the Systems Integrator. But other cases, if the solution is handed to the customer, it will depend ont he size of the customer. A large enterprise customer might have a product manager or a delivery manager or operations team who will be shown how to do this. Smaller organizations this might come down to an outsourced IT team or to a SME owning the solution.
  - source: "User statement of desired response to an evaluation failure."
    quote: |-
      They should know what to change on the agent to fix it. Or at least know what they need to look at.
  - source: "User statement of minimum improvement depth and suggested representative evaluator coverage."
    quote: |-
      The learner should at least learn how to improve a particular quality aspect - not every possible one (given that rubric evaluators are unlimited in what they can evaluate). But perhaps show a few common/built in ones like groundedness. Maybe a quality evaluator and an agent evaluator example: https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluate-agent?tabs=python
  - source: "User description of intended learner prerequisites and role diversity."
    quote: |-
      They have awareness that "Evaluation" is how we test Agentic/AI solutions, but unlikely to have any practical experience with it. But they should have basic understanding of Foundry, Agents and building/designing apps - but they might not be engineers (e.g. could be a presales architect or solution architect).
  - source: "User confirmation of the core coding boundary and source visibility."
    quote: |-
      Yes, but the Python should be shown/available if neccessary so that an engineer can see what it looks like. But it would be acceptable for python scripts to be run to run evaluations or create asssets that might be required.
  - source: "User clarification of mandatory rubric and optimization outcomes."
    quote: |-
      We do need to ensure we cover creation of Rubric evaluators and how we'd use them with Agent optimizer. So the lab should build up the learning to eventually get to Rubric evalators and then how we'd optimize an agent for cost while maintaining evaluation quality.
  - source: "User statement of optimization priorities for the learning scope."
    quote: |-
      Reducing cost is usually the main goal of agent optimizer - but secondary outcomes can be to imrpovve quality and adherance to the Rubric.
  - source: "User clarification of the default quality constraint and customer-approved trade-offs."
    quote: |-
      It should always match or exceed the baseline - but never say never. It's possible a customer would accept a slight reduction in quality for a large reduction in cost.
  - source: "User confirmation of required hands-on red teaming and candidate official workflows."
    quote: |-
      Should run a small red-team exercise with https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-scans-ai-red-teaming-agent
      or
      https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-ai-red-teaming-cloud?tabs=python
  - source: "User condition for supporting additional tracks in an existing environment."
    quote: |-
      This should be supported if the process can be made simple and it will be simple to manage the lab track requirements. These would have to be data driven.
  - source: "User requirement for catalog upkeep and mode-aware setup."
    quote: |-
      We would need to ensure the track catalog is kept up-to-date. Also, we'll need some intelligence around how the track catalog is used/implemented in a self-organized lab vs a multi-user lab run by a lab organizer.
  - source: "User proposal for region and model deployment defaults."
    quote: |-
      I wonder if we should change the recommended default region to be EastUS2 or SwedenCentral (hero regions for Foundry) instead of AustraliaEast (which has limitations). Use of global standard model deployments would generally be recommended for a lab (as we don't really need to worry about data processing limitations).
  - source: "User confirmation of East US 2 default and data-driven regional guidance."
    quote: |-
      We should as part of this work update the default region to recommend EastUS2, but note that although other regions are supported certain modules won't be available/work. We might need to document this in the track catalog so it can also be data driven. Consider this.
  - source: "User proposal for post-deployment module availability reporting."
    quote: |-
      Perhaps after deployment the configuration script should produce a summary of which modules can be completed within the lab?

proposed_partner_questions:
  status: "User supplied excerpts from two practitioner responses and one follow-up, recorded anonymously in Method 3. Wider validation remains open. Nothing was sent by the assistant."
  primary: "Thinking about your most recent agentic AI customer project, how did you and the customer agree what acceptable quality meant, and what evidence, if any, did you use to decide whether to move forward?"
  follow_up: "Can you describe a point where that decision was difficult and how you handled it?"
  rationale: "Ask about actual practice before suggesting evaluation tools or sales benefits. Allow evidence of no gap as well as a gap."

current_exploration:
  objective: "Carry evaluation principles, early development feedback, and explicit hands-on Microsoft Foundry capability/value awareness into design for engineers, consultants, and architects. Core completion must not require a third-party evaluation platform. Review proposed PRD acceptance detail and retain evidence and feasibility limits before closure or implementation."
  pending_question: null
  evidence_limit: "Two practitioner excerpts supplied by the requester are summarized anonymously. No independent WorkIQ verification, observed learner sessions, or direct customer evidence. Do not generalize to all partners."

research_deferral:
  requested_by: "user"
  rationale: "No partner responses during a public holiday. User asks to proceed and revisit partner evidence later."
  working_assumption: "Design for no or limited practical evaluation experience."
  confidence: "Unvalidated assumption, not a finding about all partners."
  revisit_when: "Partner replies or access to a practitioner become available."
  status: "Partially addressed by two requester-supplied practitioner excerpts. Wider learner and customer validation remains open. See method-03-synthesis/practitioner-evidence.md; earlier no-reply log entries are historical."

working_problem_statement:
  status: "User-approved learning gap, informed by two limited practitioner perspectives; not validated across the intended learner population."
  text: "Consultants, delivery engineers, and solution architects need practical ways to define, run, and interpret repeatable evaluations from the start of development and throughout the product lifecycle so they can agree quality requirements, design and build agentic solutions, assess changes against those requirements, and hand over checks and processes for continued use."

prd_authoring:
  status: "draft"
  path: ".copilot-tracking/dt/foundry-evaluation-learning/prd.md"
  state_path: ".copilot-tracking/dt/foundry-evaluation-learning/prd-state.md"
  authorization: "User approved drafting and explicitly requested persistence, commit, and push of all current session work. No final PRD signoff, implementation, cloud jobs, access changes, or PR creation authorized."
  synthesis_disposition: "Requester accepted a working baseline with evidence limits and equal consultant, delivery engineer, and architect scope. Full Method 3 validation remains incomplete. Methods 1 and 2 remain the only fully completed methods; no Method 4 transition."
  canonical_checkpoint: "Not yet available as an automatic exit offer: the validated Method 3 exit has not been reached. No snapshot or rendering generated."

external_research_references:
  - path: ".copilot-tracking/research/2026-11-05/evaluation-driven-development-research.md"
    purpose: "Verified industry guidance for early repeated evaluation and a qualified TDD analogy; also covers functional/non-functional verification limits."
    limit: "Not evidence of universal adoption, partner maturity, technical feasibility of this lab, or learner effectiveness."

working_hypotheses:
  - "Earlier ACL-agent proposal is superseded by the user's provisional flight-disruption selection."
  - "Python agent creation and portal-first delivery may reduce setup effort. Not selected."
  - "A release recommendation may provide an appropriate completion exercise. Exact assessment not agreed."
  - "Learners may need help agreeing measurable acceptance criteria with customers, not only running evaluators."
  - "Unclear evaluation may reduce customer confidence and delay solution commitment or release. This is the user's expectation, not an observed causal finding."
  - "Including an evaluation methodology in a solution proposal may support customer commitment and better quality. Partner and customer evidence is needed."
  - "Running evaluations, interpreting business significance, and authorizing action may be separate responsibilities. Allocation is not yet established."
  - "Groundedness, Tool Call Accuracy, and a domain-specific rubric may provide complementary representative examples. Exact evaluator selection and full improvement exercise are not agreed."

technical_reference_notes:
  - source: "https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-scans-ai-red-teaming-agent"
    note: "The local Azure AI Evaluation SDK guide explicitly states the local AI Red Teaming Agent is not compatible with the new Foundry portal and SDK. Do not treat it as an interchangeable fallback for this track."
  - source: "https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-ai-red-teaming-cloud?tabs=python"
    note: "Cloud red teaming uses the Foundry projects SDK and supports prompt and container agents as targets. Recommend it for technical feasibility assessment, not yet as an approved working configuration. Supported region, risk category, and tool compatibility must still be checked for the chosen agent."
  - source: "https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-costs"
    note: "Optimization job costs include agent execution, judge scoring, and candidate generation. These are distinct from the runtime cost of the agent ultimately selected. Portal estimates are modeled, not spending caps or final bills."
  - source: "https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-overview"
    note: "The optimizer ranks candidates by composite evaluation score, not a guaranteed minimum runtime cost. Cost-aware candidate selection must compare costs alongside quality evidence."
  - source: "https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluate-agent?tabs=python"
    note: "The current guide recommends a rubric as the primary domain measure with complementary built-ins. It demonstrates evaluation of versioned agent targets and retrieval of results. Its Python examples require azure-ai-projects>=2.8.0; the repository currently declares >=2.4.0, so implementation must verify the resolved SDK version."
  - source: "https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators"
    note: "Groundedness assesses alignment with supplied context. It does not independently establish that source information is correct."
  - source: "https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators"
    note: "Tool Call Accuracy assesses tool choices and parameters as process evaluation. Final-answer quality alone does not establish correct tool use."

constraints:
  fixed:
    - "Planning documents may be persisted, committed, and pushed as requested. Lab implementation, resource provisioning, and paid service jobs still require approval."
    - "Reuse the workshop setup approach rather than create a separate deployment system."
    - "Core MCP use is read-only."
    - "Core completion must not require Python authoring; running supplied scripts is allowed, and source must remain available."
    - "Support facilitated and independent completion."
    - "Teach evaluation use and rubric creation as primary outcomes. Retain Agent Optimizer as secondary; cost reduction must be assessed against required quality."
    - "Retain a small hands-on red-team exercise as secondary. Deployment blocks must not prevent primary completion; report each secondary activity's actual status and reason."
    - "No prior lab completion or previously created agent and knowledge assets are prerequisites."
    - "Respect organizer region selection; warn for unsupported modules without blocking the whole track."
  open:
    - "Differences in needs across the identified learner roles."
    - "Automated testing experience beyond evaluation awareness is not established."
    - "Customer acceptance authority and other affected stakeholders."
    - "Allocation of evaluation execution, interpretation, and decision authority across the identified operating models."
    - "How much lifecycle automation the lab must implement versus demonstrate; lifecycle use is desired, but production integration depth is not agreed."
    - "Observed learner problems and available stakeholder evidence."
    - "Partner inquiry questions, responses, and examples of evaluation commitments in proposals."
    - "Detailed flight-disruption tasks, agent configuration, and module sequence. Passenger-facing advice and fictional airline policy are selected."
    - "Portal and Python balance."
    - "Required operational automation depth."
    - "Exact quality-preservation criteria, runtime cost measurement, and handling of cost-quality trade-offs."
    - "Cloud red-team supported region, applicable risks, and target/tool compatibility for the selected agent."
    - "Who provisions smaller comparison models and whether any automatic deployment is permitted."
    - "Session objectives and desired reflection points."

storage:
  root: ".copilot-tracking/dt/foundry-evaluation-learning"
  reason: "User requested repository persistence and branch push for cross-machine recovery. Repository copies are authoritative on resume."

canonical_deck:
  snapshots: []
  last_offered_at: null
  last_offered_response: null
  last_generated_at: null

customer_card_render:
  last_offered_at: null
  last_offered_response: null
  last_generated_at: null
  decline_final: false
  output_path: null
```
