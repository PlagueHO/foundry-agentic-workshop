# Plan: Evaluate and improve Foundry agents

## Status

Learning-design draft. No lab implementation is approved. The user accepted Methods 1 and 2 as sufficient to start Method 3: Input Synthesis. Partner validation and live feasibility remain unresolved; limited practical evaluation experience is a design assumption, not a confirmed finding about all partners.

The user has now authorized a draft PRD. `prd.md` consolidates current requirements, proposed acceptance criteria, and open verification gates. This file remains earlier planning context; its proposed module sequence and architecture are not approved. Method 3 documentation is consolidated in `method-03-synthesis`, with validation limits recorded in `problem-definition.md` there.

The latest user decision makes learning to use/run evaluations the primary goal. Agent Optimizer and red-team evaluations remain secondary activities. Deployment conditions that block them must be explained without preventing primary completion. This supersedes earlier unconditional execution requirements. See `method-02-research\findings-summary.md`.

The user has paused the prompt-agent proposal to determine whether the entire new track should use hosted agents. Hosted agents are now the preferred option to investigate, not a confirmed architecture decision. The earlier recommendation to use the portal prompt-agent Optimizer is suspended.

Coaching state and research assets are stored in `.copilot-tracking\dt\foundry-evaluation-learning\`. The user authorized saving, committing, and pushing these planning documents before pausing. Lab implementation, infrastructure changes, and paid service jobs remain unapproved. Start with `resume-notes.md` when resuming.

The selected working scenario is passenger-facing, read-only flight-disruption advice using clearly labelled fictional airline policy. Real-world legal-entitlement advice is out of scope. Historical ACL and prompt-agent observations below are retained as research context, not current scenario choices.

## Problem and approach

Issue #65 proposes a rubric-evaluator module in the introduction track. The user has expanded the direction to a separate track that covers evaluation, rubric evaluators, AI red teaming, development and operational workflows, and Agent Optimizer.

Teach learners to use evidence to decide whether an agent is ready, what needs to change, and whether a change helped. Organize the track into focused modules. Do not make portal navigation or tool coverage the main measure of learning.

## Confirmed decisions

- Create a separate track with focused modules.
- Keep the introduction track's existing numbering.
- Target practical judgment: learners must run evaluations and use the evidence to make an agent release decision.
- Start with learning outcomes. Detailed module assets and implementation choices remain open.
- Assume basic Foundry agent skills; do not require completion of the introduction track.
- Do not assume completion of any other lab or the existence of an agent, knowledge base, or project connection created by another lab.
- Provide creation of this track's required agent and assets from the provisioned workshop starting state. Reuse existing setup patterns, not an earlier lab's end state.
- Include grounded advice and read-only MCP tool use in the core scope.
- Reuse the existing workshop provisioning approach.
- Include engineers, presales architects, and solution architects who know Foundry and agents but may have no practical evaluation experience.
- Do not require Python authoring. Running supplied scripts for asset creation and evaluation is acceptable; keep source available for engineers.
- Support facilitated and independent completion.
- Teach repeatable evaluation as a delivery and handover capability for development, model or agent changes, and production monitoring.
- Teach partner handover of reusable evaluation assets and processes that customers, internal teams, or another partner can continue using to check changes against quality gates. Include hands-on production evaluation in the core. CI/CD execution remains optional extra credit.
- In the core production exercise, learners identify a quality failure in live lab-agent activity, inspect the supporting conversation or trace, and explain what needs investigation. Use synthetic passenger requests against the deployed lab agent, not a real customer production system. Monitoring mechanics and verification remain open.
- Keep CI/CD execution outside core completion. Provide an optional extra-credit module and a runnable GitHub Actions evaluation workflow in this repository, targeting the agent already deployed through the lab. Explore fork setup, configuration, authentication, and permissions before implementation. Do not require Azure DevOps or another CI platform in the core.
- Teach investigation and improvement of at least one quality aspect, rather than exhaustive evaluator coverage.
- Require creation and use of rubric evaluators in the primary evaluation learning path. Include their use with Agent Optimizer as a secondary activity.
- Make agent cost reduction the primary optimization objective for this lab, with improved quality and rubric adherence as additional outcomes.
- Match or exceed baseline quality by default. Allow an explicit customer decision to accept a slight quality reduction for a large cost reduction.
- Include a small controlled hands-on AI red-team exercise as a secondary activity. Report deployment blocks without preventing primary completion.
- Respect the organizer's selected region. Warn when a feature or module is unsupported there; do not block the entire track or automatically relocate resources.
- Allow deployment of a smaller model for comparison. Automatic provisioning is a possibility, not yet a selected requirement.
- Expect ongoing maintenance as supported models and versions change.
- Keep self-hosted setup simple. Use the existing individual deployment mode with suitable defaults, not a manual series of extra model-deployment steps.
- Keep organizer control over comparison-model provisioning. Do not require each workshop attendee to deploy models.
- Support multiple tracks in one environment and adding tracks later, provided setup and requirement maintenance remain simple. Track requirements must be data driven.
- Keep the track catalog current. Its use must distinguish individual self-organized environments from organizer-run multi-user environments.
- Change the recommended default region to East US 2 as part of this work. Explain that other regions can be used but some modules or exercises may be unavailable. Keep region guidance data driven through the track catalog.

## Proposed learning outcomes

1. Define success. Translate business requirements into observable quality and safety criteria. Choose response-level, tool-level, or conversation-level evidence.
1. Build useful test data. Include representative requests, edge cases, and known failures. Keep improvement data separate from held-back validation data.
1. Choose evaluators. Compare built-in metrics, deterministic checks, custom prompts, rubric evaluators, and human review. Explain the evidence and limits of each.
1. Make domain-specific judgments. Define weighted rubric criteria, scoring guidance, and thresholds. Inspect criterion-level scores and reasons. Calibrate results against human judgments.
1. Assess adversarial risk. Distinguish routine evaluation from AI red teaming. Run a controlled test in an approved test environment. Interpret attack success rates and coverage limits.
1. Use evaluation throughout delivery. Apply development checks, pre-release regression checks, and sampled operational evaluation. Use failed cases and traces to guide changes.
1. Improve an agent safely. Run Agent Optimizer, inspect candidate changes, and compare quality, safety, and cost. Check held-back cases before a promotion decision.

## Proposed module sequence

| Module | Learning focus | Observable evidence |
|---|---|---|
| 01. Define success and establish a baseline | Evaluation units, business criteria, representative data, and human labels | A small test dataset and an explained baseline |
| 02. Select and combine evaluators | Built-in evaluators, deterministic checks, custom prompts, and complementary signals | Results that show why one metric is not enough |
| 03. Design and calibrate rubric evaluators | Domain-specific dimensions, weights, thresholds, applicability, and judge limits | Criterion-level results for strong and weak responses, followed by a justified rubric revision |
| 04. Test adversarial behavior | Authorized test scope, AI red teaming, attack success rates, mitigations, and limits | An interpreted risk report and a justified mitigation choice |
| 05. Use evaluation in development and operations | Regression checks, release criteria, sampled traffic, traces, and dataset feedback | A reusable release check and an operational evaluation design |
| 06. Optimize and make a release decision | Baseline selection, candidate generation, independent validation, and human review | A supported promote-or-keep decision |

This sequence is proposed, not confirmed. The track needs its own asset-creation starting point. Local, CI/CD, and regular production execution are required contexts for the partner practice being taught. Production evaluation is hands-on core work; CI/CD execution is optional extra credit. Exact production-evaluation mechanics, model-provisioning responsibility, and hosted-agent coverage remain open. Modules must identify their prerequisites and regional limits so that supported independent work can continue.

### Optional CI/CD extension: exploration scope

The user selected an optional extra-credit module with a real repository GitHub Actions evaluation workflow, not only illustrative YAML. It should evaluate the agent deployed through the lab. Learners who choose this extension would fork the repository and configure the required environment settings and access. Skipping it must not prevent primary completion.

Initial repository observations:

- `.github/workflows/smoke-test.yml` already uses a GitHub environment, federated Azure login, environment settings, and result artifacts. These are potential patterns, not proof of sufficient Foundry evaluation permissions.
- `.github/workflows/provision-infrastructure.yml` uses federated authentication and resolves environment configuration for provisioning. Evaluation should target the existing lab deployment rather than require provisioning again.
- `.github/workflows/e2e-test.yml` orchestrates provisioning and cleanup. Do not reuse that whole lifecycle for an evaluation-only run against an attendee's existing deployment.

Questions for later design and feasibility work: fork onboarding and workflow activation; explicit target project and agent version; required variables versus protected credentials; federated identity setup and least-privilege evaluation access; sharing evaluation definitions with local runs; safe triggers and cost controls; result artifacts and quality-gate failures versus setup or execution errors; and handling shared organizer environments.

No workflow has been created or executed. No identity or permission changes are authorized by recording this requirement. Production evaluation is hands-on in the core and must not depend on completing this optional extension.

## Completion criteria

The final exercise must require the learner to make a decision, not just complete a successful run. Evidence should include:

- The baseline and candidate identities, dataset versions, and evaluator configurations.
- Aggregate results plus individual failures and criterion-level reasons.
- Independent checks on held-back cases.
- Safety regressions, deterministic failures, and cost or token trade-offs.
- A reasoned decision to promote a candidate or keep the baseline.
- An explicit record of any customer-approved cost-quality exception; do not silently lower thresholds.
- Limits of the evidence and required human review.

Do not require an optimizer improvement or a passing red-team scan for completion. An informed decision not to release is a valid result. A higher average must not override a critical failure.

Primary completion must be demonstrated through actual evaluation work, not depend on execution of the two secondary activities. Where optimization is blocked, base the primary decision on the evaluation evidence available; do not require a generated optimization candidate. Report secondary completion separately, with the specific cause and next action for blocked work. Unverified capability and execution failure must not be presented as confirmed deployment blocks or successful runs.

## Technical facts and limits

- The repository currently has 13 introduction-track modules, including an optional extension. Some guidance still describes 12 core modules.
- Module 05 already introduces portal evaluations. Module 11 introduces monitoring and optional continuous evaluation and red teaming. The new track should link to these without depending on the full introduction sequence.
- The docs generator discovers numbered modules and can discover another track. It has explicit track ordering and title entries. The front-matter validator currently lists only two tracks. Both need inspection and scoped updates during implementation.
- Rubric evaluators produce normalized overall scores and per-dimension scores, applicability, weights, and reasons. They use an LLM judge and require calibration.
- Current prompt-agent optimization starts in the portal and excludes agents using the Microsoft Copilot harness. Hosted-agent optimization needs code integration.
- The optimizer portal requires evaluator-compatible dataset column names and does not provide column mapping.
- Red-team support varies by region, target, tool, and risk category. Do not imply that every agent or tool path is supported.
- An unsupported regional feature must produce a clear module-specific warning. Distinguish unsupported, prerequisite unavailable, execution failure, and completed states; do not present skipped work as a successful run.
- Do not require a supported-region redeployment to access the rest of the track. Any alternative deployment requires an explicit organizer decision.
- Optimization can execute external tools repeatedly. Use test resources and prevent changes to real customer data.
- The exact portal/script balance and flight-agent name remain proposals. Hosted-agent optimization is the preferred secondary path under investigation; its execution does not gate primary completion when deployment conditions block it. No Python authoring is required, but supplied scripts may be part of the core path.
- Existing Module 07 has Python setup for knowledge sources over seeded product and policy indexes, a knowledge base, a project connection, and a prompt-agent version. Reuse its setup approach where suitable; never assume those resources already exist for a new attendee.
- Existing retail MCP tools include purchase, product, policy, and replacement lookups plus a simulated case-creation operation. The new core scope must restrict the agent to read-only tools rather than attach the full tool set unchanged.
- The workshop profile's `chat` and `gpt54mini` deployments use the same model/version. Different names do not establish different model costs.
- Use the existing model profile or override mechanism to investigate a suitable smaller model and eligible optimization model. Exact model choices and provisioning behavior remain open.
- Keep deployment names, actual model identities and versions, and pricing assumptions visible in comparisons. Review model availability and the exercises when model versions change.
- The existing wizard defaults to individual mode, region `australiaeast`, and the `default` model profile; it does not select configuration by lab track. The manual Bicep parameter fallback uses `EastUS2`.
- Both individual and organizer modes share `azure.yaml` and Bicep. Individual preparation resolves the deploying identity and suppresses the facilitator project; onboarding writes `.env` automatically.
- Existing quota validation blocks provisioning when the selected deployment set is unavailable or exceeds quota. Any optional comparison-model behavior must be designed explicitly without weakening required-model checks.
- Re-provisioning rewrites the individual `.env`. Required new settings must be generated or derived, rather than depend on manual edits alone.
- A single-track-only selector is not suitable. The user conditionally supports multiple-track selection and later additions, with simple, data-driven requirement management.
- The current portal quickstart explicitly supports custom rubric selection or creation in the prompt-agent Optimizer. It requires a prompt agent without the Copilot harness.
- The portal supports comparing candidate model deployments, but tool-description optimization is limited to function tools and does not evaluate their client-side execution. Do not describe the exercise as optimization of MCP tool schemas.
- Rubric-judge support and optimization-model support differ. The documented lists allow `gpt-5.4-mini` as a rubric judge but do not list it as an optimization model.
- `uv.lock` resolves `azure-ai-projects` 2.7.0. The current agent-evaluation guide uses >=2.8.0 for its rubric-generation example. Check and update compatible dependencies during implementation if that path is selected.
- Evaluation model inference requires account-scope permission; trace-based and continuous evaluation add workflow-specific identity requirements.
- The cloud red-team support matrix does not establish support for this track's custom retail MCP and knowledge MCP configuration. A separate safety-test configuration is a possible fallback that needs user agreement, not an approved replacement for testing the full agent.

## Proposed data-driven track setup

This is a planning direction, not an approved schema or implementation.

- Use a small declarative track catalog as the source for track identities and environment requirements. Do not scatter track-specific conditions through the wizard, quota hook, and onboarding generator.
- Let the wizard select one or more tracks and persist the selected set in the azd environment.
- Resolve the combined requirements once. Reuse shared services and compatible model deployments instead of duplicating them for each track.
- Keep model identity, version, deployment alias, and mode-appropriate capacity explicit. Use the existing profile and inline-override mechanisms where practical; do not introduce a general dependency-management framework.
- Describe module-specific feature and region constraints in data. An unavailable feature must retain its warning and incomplete-module status, not silently exclude the module or block unrelated work.
- Respect explicit organizer configuration. Report incompatible deployment aliases, model requirements, or overrides rather than silently selecting a winner.
- For an existing environment, show the proposed additions and quota implications before provisioning. Verify compatibility before changes; do not remove resources or learner assets merely because a track is deselected.
- Preserve existing configuration and learner assets when adding tracks. Account explicitly for the current `.env` rewrite and for rerun behavior of affected provisioning hooks.
- Keep the initial implementation focused on the requirements needed by the selected tracks. Do not make a full conversion of all existing infrastructure into per-track conditional deployment a prerequisite.

Next desk-research task: test this approach against the existing model-profile, quota, hook, and onboarding paths. Determine whether the manifest and additive update can remain small enough to maintain without duplicated requirement definitions.

### Catalog maintenance and deployment modes

The user requires catalog maintenance and mode-aware behavior. The following mechanisms are proposals to verify:

- Keep track requirements in one catalog. Resolve them against explicit individual or organizer mode rather than maintaining two independent catalogs.
- Individual mode should supply a low-capacity default and prepare configuration for the deploying learner. Organizer mode should share environment services while preserving existing per-attendee projects and isolated learner assets.
- Separate model identity and compatibility requirements from sizing. Shared capacity needs an explicit concurrency assumption; multiplying individual capacity by roster length is not automatically correct.
- In organizer mode, the organizer selects tracks and approves shared-resource changes. Attendee setup should validate assigned prerequisites and create permitted project assets, not silently change shared deployments.
- Assign catalog maintenance to the relevant track maintainer. A track change affecting prerequisites must update its catalog entry in the same change.
- Add focused CI checks for schema, track discovery, referenced modules, model-definition references, and supported mode settings. Tests should cover combined requirements, conflicts, mode-specific defaults, and additive-update behavior.
- Reuse canonical model definitions where possible instead of copying versions across the catalog, profiles, and scripts.
- Validate current model availability, quota, and known feature-region constraints at setup. Static CI cannot prove live subscription eligibility or service availability.
- Persist selected tracks and the applied catalog version or content fingerprint. On rerun, show relevant requirement changes before applying them; a catalog update is not permission to replace a working deployment.
- Avoid a general policy engine, background updater, or automatic model substitution. Keep the resolver deterministic and its decisions visible.

### Region and model deployment defaults

The user has confirmed changing the recommended default to East US 2 as part of this work. This does not authorize implementation during planning or relocation of existing environments. Global Standard remains the proposed preference for supported lab models.

- Recommend `eastus2` for new environments, subject to the selected tracks' full resource/model compatibility and quota checks. It is listed by both inspected official red-team references.
- Keep `swedencentral` as a candidate alternative. The conceptual red-team guide lists it, but the evaluation regional reference does not. Do not promise full red-team compatibility without further verification.
- Preserve explicit user or organizer regions and existing environment locations. Never relocate resources on rerun.
- Prefer `GlobalStandard` for supported lab models using synthetic or non-sensitive training data. Existing inspected model profiles already use this SKU.
- Explain that Global Standard can process inference data outside the resource region. It does not remove Foundry project-feature regional limits or model availability/quota requirements.
- During implementation, align wizard defaults, quickstart examples, and parameter fallbacks for new environments. Preserve instructions showing how to select another region.
- Official evidence: [evaluation regional reference](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-regions-limits-virtual-network), [red-team concept](https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent), and [deployment types](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types).

### Data-driven regional guidance

- Store the recommended new-environment region once, rather than repeat it independently for each track.
- Have track modules or exercises reference their required regional features. Keep feature-region evidence and documentation references in shared catalog data, so multiple tracks do not maintain conflicting copies.
- Distinguish documented support, documented lack of support, and unknown or conflicting evidence. Do not equate omission from an incomplete list with a verified unsupported status.
- Resolve regional guidance for the selected tracks and mode. Show affected modules or exercises and the reason in setup and documentation; distinguish required activities from optional extensions.
- An unknown feature status should prompt a verification warning. An unsupported feature should mark the affected activity unavailable; neither should prevent unrelated supported work.
- Unsupported or skipped activities must retain their actual status. Primary outcomes may be completed while a secondary Optimizer or red-team activity is blocked; do not claim that every activity was executed.
- Preserve explicit environment regions and deployment overrides. Suggest East US 2 without silently selecting it for an existing environment.
- Prefer producing documentation tables and setup warnings from the same regional data. Validate module and feature references in CI. The exact catalog format and documentation generation approach remain open.

### Post-deployment module readiness summary

The user proposes a post-deployment summary showing which modules can be completed in the environment. Recommend adding it to the existing configuration-script summary, using catalog requirements and observed deployment results rather than a separate hard-coded checklist.

- Show deployment mode, selected tracks, actual deployed region, and module or exercise readiness.
- Use clear statuses: prerequisites met, unavailable in this region, prerequisite missing, and unverified. Report failed checks explicitly with the cause; do not convert check failures into unsupported status.
- Identify required versus optional activities and provide a specific reason and next action for each limitation.
- Check relevant deployed services, model deployments, and project configuration where read-only inspection is possible. Separate catalog-based regional evidence from observed deployment evidence.
- Do not label a module completed, or guarantee that every exercise will run, merely because its prerequisites appear to be met. No automatic evaluation, optimization, or red-team jobs should be started to produce the summary.
- Individual mode should report readiness for the deploying learner. Organizer mode should report shared readiness and project-level setup gaps where checked, without claiming that every attendee's effective access has been validated.
- Reuse the same requirement checks for initial setup, later track additions, and a read-only readiness rerun where practical.
- Produce a terminal summary and consider a generated local report linked from onboarding. Exact output format remains open.
- Place readiness reporting after prerequisites are created. If a provisioning hook fails before the summary, retain the original failure and label any partial report as incomplete.

## Agent-type decision under investigation

The user reports that prompt-based agents are being deinvested in and hosted agents are the recommended direction. Treat this as user-provided roadmap context. The inspected public Agent Service overview still documents and recommends prompt agents for fast starts; do not state public deprecation or retirement without evidence.

### Hosted-agent evidence

- The official hosted-agent Optimizer workflow supports custom rubric evaluators, model comparison, and a held-out validation dataset. It uses supplied code, CLI, Toolkit, or SDK rather than the prompt-agent portal creation wizard.
- Hosted-agent optimization requires the Responses protocol and optimizer-ready runtime code using `azure-ai-agentserver-optimization`, a baseline configuration, and `load_config()`. Loaded candidate instructions and model settings must actually be used at runtime.
- The hosted optimization quickstart explicitly mentions subscription allowlisting, while the main Optimizer overview does not. Actual access is unknown. Treat this as a changing access condition to verify, not a confirmed universal restriction or a reason to require prompt agents. Models and region alone cannot establish readiness.
- The repository's Module 09 provides Python Agent Framework, Responses hosting, remote source-code build/deployment, and bounded activation polling. Reuse these patterns without requiring earlier lab completion.
- Module 09 does not implement Foundry IQ knowledge access, read-only MCP restriction, or optimizer runtime configuration. It is not a ready-made new-track baseline.
- Module 10 provides a toolbox integration reuse candidate. Current official hosted-agent guidance recommends `FoundryToolbox` with Microsoft Agent Framework instead of a generic MCP client. Check the current SDK and identity requirements rather than copying the older integration unchanged.
- Hosted-agent identity is distinct from the project managed identity. Protected knowledge access must be prepared by setup or the organizer; attendees must not need to grant themselves access to shared services.
- Hosted-agent compute is billed in addition to inference and tools. Runtime cost comparisons must include or explicitly bound compute effects, rather than equate cheaper tokens with cheaper overall operation.
- The hosted workflow lacks the prompt portal's pre-run cost estimate. Provide explicit bounded job settings and visible cost assumptions; do not promise a portal spending limit.
- Cloud red teaming supports container-agent targets, but hosted-agent selection does not prove support for custom MCP or remove tool-specific restrictions.
- The current toolbox integration documents downstream authentication and per-request context forwarding. It is a candidate route for hosted knowledge and MCP access, not yet a tested new-track configuration.
- Toolbox consumer endpoints follow the mutable default version. Evaluation records must identify the actual tool configuration as well as the agent, model, dataset, and evaluator versions.
- The existing Search fixtures contain 100 products and 50 policies; none of the three primary retail MCP product IDs occurs as a Search product ID. Sample Search and MCP content use different product/currency contexts. A small aligned evaluation fixture set is recommended instead of assuming existing retail assets are coherent.
- User selected flight disruption as the working scenario for now and confirmed passenger-facing advice grounded in clearly labelled fictional airline policy. Real-world legal-entitlement advice is out of scope. General retail without ACL is a parked alternative, not a second implementation. Existing rights-focused knowledge is not an approved source for this scenario. Aligned reviewed fixtures and custom MCP cloud red-team compatibility remain unresolved. No implementation or cloud execution is approved.
- Red-team uncertainty must be scoped precisely: basic agent response testing, tool-mediated simulation/indirect-injection coverage, and MCP backend security are separate concerns. The support matrix does not establish that a custom MCP dependency blocks all agent scans. Verify whole-agent acceptance separately from the supported tool-level test coverage; do not treat either outcome as proof of backend security.

### Researcher recommendation

Prefer one supplied Python hosted agent using Responses throughout the track, already wired for optimization. Learners can run prepared setup, evaluation, and optimization scripts without writing Python. Keep source visible for engineers. Unknown Optimizer eligibility should not by itself force a prompt-agent architecture. Verify actual access and the intended knowledge/MCP path before claiming end-to-end readiness.

The user cannot know target subscription access in advance. A partner or customer may need to request access. Potential GA at Ignite and stale documentation are possibilities, not confirmed service changes or release commitments.

- Catalog data should identify the Optimizer capability and its documented access uncertainty, with official guidance references. Do not encode universal allowlisting as a permanent requirement.
- Use a supported read-only capability check if one is available. If no such check exists, report access as unverified. Do not create a paid optimization job just to classify readiness.
- If an authorized run fails, report its actual error. Distinguish access restrictions from permissions, regional support, model configuration, and quota failures; do not infer allowlisting from any generic 403.
- Explain the request/verification path in current official guidance where applicable. Permit the rest of the track to continue while access is unresolved.
- Report an unexecuted Optimizer exercise separately from primary completion. A sample report is not evidence that the learner executed the secondary activity; a deployment block must include its cause and next action.
- Recheck availability guidance before publishing the lab, especially after service announcements. Do not depend on a future launch to make the plan valid.

Sources: [Agent Service overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview), [hosted-agent concepts](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents), [hosted optimization quickstart](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-optimize-hosted-agent), [optimizer-ready runtime](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/make-agent-optimizer-ready), [optimizer datasets and rubrics](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/create-optimizer-dataset), and [optimization targets](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/optimize-agent-targets).

## Todos

1. Preserve the completed Method 1 scope and the open partner-research questions.
1. Continue Method 2 desk research. Revisit partner validation when replies or practitioner access become available.
1. Finalize the module learning objectives and observable completion criteria.
1. Select the scenario, portal and Python balance, supported agent type, and live-service boundaries.
1. Verify current official SDK and portal procedures, model requirements, permissions, per-module region support, and costs. Do not treat a regional limit as a whole-track blocker.
1. Produce a file-level implementation plan for the new track and its docs integration.
1. After approval, implement the module READMEs, Python starter and solution assets, datasets, and focused checks.
1. Validate module metadata, Markdown, Python behavior, and docs generation. Verify required cloud behavior where authorized access is available. Report missing live evidence explicitly.

## Out of scope unless selected

- Renumbering or rewriting the existing introduction track.
- Automatic production promotion or deployment.
- Red teaming against production systems or systems without authorization.
- A full production CI/CD or monitoring platform.
- A requirement to complete another workshop track before starting.
- Automatic region changes or unconditional model deployment by attendees.
- Exhaustive coverage of every evaluator.
- Treating judge scores, generated explanations, or a clean red-team report as ground truth.
- Rewriting existing shared retail datasets for unrelated tracks. Prefer track-owned evaluation fixtures unless a shared correction is explicitly scoped.

## Official references

- [Evaluation overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview)
- [Built-in evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators)
- [Rubric evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators)
- [AI Red Teaming Agent](https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent)
- [Agent Optimizer overview](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-overview)
- [Optimize a prompt agent](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-optimize-prompt-agent)
