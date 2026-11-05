# Method 2 desk-research notes

## Evidence boundary

The consolidated current assessment is in `findings-summary.md`. The latest user priority makes evaluation learning primary and Optimizer/red-team work secondary. Deployment blocks to secondary activities must not prevent primary completion; earlier unconditional completion statements below are historical.

Partner replies are pending. The requester reports a public holiday and asks to proceed, then return to partner research. Limited practical evaluation experience is the user-directed design assumption. Silence does not establish that partners have never used evaluations.

This note records repository observations and official documentation. It is not a set of user-research findings. No cloud workflow has been executed.

The current working scenario is passenger-facing flight-disruption advice using read-only tools and clearly labelled fictional airline policy. Real-world legal-entitlement advice is excluded. Earlier ACL and prompt-agent notes remain as historical evidence. Later decision and clarification sections supersede earlier open questions.

## Repository observations

| Observation | Evidence | Planning implication |
|---|---|---|
| Workshop provisioning already creates attendee projects, roles, shared services, seeded indexes, MCP endpoints, and onboarding | `azure.yaml`; `docs\guide-organizer.md` | Reuse the deployment and onboarding mechanism |
| Module 07 can create knowledge sources, a knowledge base, a project connection, and a prompt-agent version | `labs\introduction-foundry-agent-service\07-foundry-iq\solution\create_knowledge_base_agent.py` | Candidate starting configuration; do not require completing all earlier modules |
| The retail MCP server reads fixtures and offers four business lookup tools | `shared\mcp-servers\retail-remedy-ops\src\server.py` | Candidate allowlist: `lookup_purchase`, `get_product_profile`, `search_store_policy`, `find_replacement_options` |
| Other tools draft a summary or simulate case creation; no data is persisted | Same server | Exclude tools outside the agreed read-only lookup scope even if their current implementation does not write data |
| Module 07 restricts knowledge retrieval by `allowed_tools` but attaches the retail MCP server without a tool restriction | Module 07 solution | Do not reuse the full agent configuration unchanged |
| Lookup tests cover known records and missing IDs | `shared\mcp-servers\retail-remedy-ops\src\test_retail_remedy_ops.py` | Useful deterministic fixture references; these tests were read, not run |
| Shared seeded retail products and policies already exist | `shared\data\retail-products.jsonl`; `shared\data\retail-policies.jsonl` | Reuse stable data where appropriate; alignment with MCP fixtures still needs checking |
| The workshop profile deploys `chat` and `gpt54mini` as the same model/version | `infra\model-deployments.workshop.json` | Different deployment names alone cannot demonstrate a cheaper model tier |
| The broad profile includes `gpt54`, `gpt54mini`, and `gpt54nano`, as well as other models | `infra\model-deployments.broad.json` | Model-tier comparisons are possible through existing configuration mechanisms; do not select the whole broad profile without need |
| Existing deployment supports a model override | `infra\main.bicep`; organizer guide | Investigate a focused model set rather than a new provisioning system |

## Official documentation

| Observation | Source | Implication |
|---|---|---|
| Australia East supports batch evaluation, but is absent from the listed cloud red-team regions | [Evaluation regions](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-regions-limits-virtual-network) | Do not assume the organizer guide's Australia East example can run the complete new track |
| The regional reference lists East US 2 and North Central US for AI red teaming; the conceptual red-team page lists additional locations | [Regional reference](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-regions-limits-virtual-network); [conceptual guide](https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent) | East US 2 is a common documented candidate; verify the full feature and model combination before selecting it |
| Local red teaming is documented as incompatible with the new Foundry portal and SDK | [Local guide](https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-scans-ai-red-teaming-agent) | Not an interchangeable fallback |
| Cloud red teaming supports Foundry agent targets, with constraints on supported tools and risk categories | [Cloud guide](https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-ai-red-teaming-cloud?tabs=python); [conceptual guide](https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent) | Custom retail MCP support for a selected risk scenario remains unverified |
| Optimizer ranks by evaluation score, and model selection can compare candidate deployments | [Optimizer overview](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-overview) | Learners must compare cost separately; a score winner is not necessarily the cheapest |
| Optimization model support differs from judge model support | Same overview | Verify that the deployment profile supplies an eligible optimization model, not only an agent and judge model |

## Research to revisit

- Partner practice: current checks, acceptance gates, and delivery or handover examples.
- Learner observations: can a non-coding architect interpret a failed criterion and locate useful evidence?
- Technical feasibility: rubric generation, cloud red-team risk/tool compatibility, model tiers, quota, and cost measurements.
- Dataset consistency: seeded knowledge and retail MCP facts should not produce accidental conflicting ground truth.
- Production evaluation depth: distinguish a runnable lab demonstration from a complete managed operations platform.

## Individual and organizer deployment trace

Inspected the existing deployment code. No Azure commands or deployments were run for this investigation.

1. `docs\quickstart-individual.md` directs learners to `scripts\configure-workshop.py`.
1. The wizard defaults to individual mode. It asks for environment, region, resource group, and model profile; checks Azure permissions and Docker; saves azd settings; and asks before provisioning.
1. `azure.yaml` runs the same Bicep provisioning and hook chain for individual and organizer modes.
1. The quota hook selects `default` for individual mode and `workshop` for organizer mode unless explicitly configured otherwise. An explicit `auto` profile chooses the largest existing profile that fits; it is not the normal wizard default. Availability or quota failures stop provisioning.
1. Individual attendee preparation resolves the deploying identity, writes one attendee entry, and disables the facilitator project. Organizer mode uses the attendee roster.
1. Post-provision hooks seed indexes, deploy MCP services, prepare identity-demo resources, generate onboarding, and invoke attendee-portal setup. Each failed hook prevents subsequent hooks from running.
1. Individual onboarding writes `.env` automatically. Organizer onboarding provides per-attendee configuration. Names such as `AGENT_NAME` and `KNOWLEDGE_BASE_NAME` are configuration values, not evidence that these assets have been created.

### Concrete setup constraints

- The wizard's region default is `australiaeast`; the Bicep parameter-file fallback is `EastUS2`. These are different entry points, not a feature-aware region selector.
- The default individual model profile contains `chat`, `embedding`, and `gpt54mini`. Both chat deployments are `gpt-5.4-mini` at the same model version.
- The wizard currently has no lab-track selection. Its model-profile choices are `default`, `minimal`, `workshop`, and `broad`.
- The existing model profiles and inline override are checked before Bicep deployment. A new track-specific model choice must be connected to both quota checks and provisioning.
- Individual onboarding rewrites `.env` on re-provision. Track settings must not depend solely on manual edits that this step discards.
- The existing shared service path requires Docker for MCP image builds. Reusing the setup does not remove its documented prerequisite.
- There is no demonstrated self-contained retail training-agent creation in the provisioning chain. The new track needs its own first-run agent and knowledge setup.

### Recommendation to confirm

Reuse the current wizard, provisioning, identity, quota, and onboarding flows. Consider a lab-track choice that applies evaluation-appropriate defaults for individual mode while preserving organizer overrides and existing-track behavior. Do not silently use the broad model profile or change every workshop's defaults to satisfy one track.

The user requires self-hosted setup to work with defaults. Here, self-hosted means the repository's individual deployment mode, not a Foundry hosted-agent runtime.

## Region-default proposal follow-up

Rechecked the official evaluation regional reference, red-team conceptual guide, and model deployment-type guide after the user proposed East US 2 or Sweden Central and Global Standard.

- East US 2 appears in both inspected red-team region lists and in the agent playground and batch evaluation lists.
- Sweden Central appears in the conceptual red-team guide but remains absent from the evaluation reference's red-team list. The documentation conflict remains unresolved.
- Microsoft recommends starting with Global Standard for most workloads. Its inference processing may occur in any Azure region. This is separate from project-feature regional availability.
- Existing inspected default and workshop model profiles already use `GlobalStandard`.
- Researcher recommendation: prefer East US 2 for new environments, keep Sweden Central as an alternative requiring feature verification, and preserve explicit region choices and existing deployments.
- No live model/quota, optimizer, cloud red-team, or complete infrastructure compatibility checks were performed.

## Rubric, Optimizer, and cloud red-team desk research

Evidence comes from current official documentation and repository dependency files. No service jobs were started.

### Documented capabilities and constraints

| Observation | Evidence | Confidence and limit |
|---|---|---|
| The portal prompt-agent Optimizer accepts existing custom evaluators and can create/select a custom rubric evaluator | [Prompt-agent quickstart](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-optimize-prompt-agent) | High for documented capability; not live-tested |
| The portal path requires a prompt agent without the Copilot harness, a judge deployment, and an eligible optimization deployment | Same quickstart; [Optimizer overview](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-overview) | High; full chosen model/region combination still needs verification |
| Candidate model deployments can be compared in the portal | Same quickstart | High; duplicate aliases for one model do not establish cheaper tiers |
| Function-tool description optimization does not execute or evaluate client-side function tools; other tool types are not supported for description optimization | Same quickstart | High; do not claim this optimizes custom MCP schemas or implementations |
| The wizard has no dataset column mapping and uses the same dataset to score baseline and candidates | Same quickstart | High; prepare compatible fields and use independent held-back evaluation for release checks |
| Rubric generation and scoring list `gpt-5.4-mini` as supported; the optimization-model list includes `gpt-5.4` but not `gpt-5.4-mini` | [Rubric reference](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators); Optimizer overview | High for documented lists; no quota or model-version selection performed |
| Optimizer results rank composite evaluation score, not minimum runtime cost | Optimizer overview | High; retain separate cost-quality acceptance decision |
| Optimization cost includes agent, judge, and improvement-generation activity; measured tokens are not an invoice and missing usage is not zero | [Cost guide](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-costs) | High; deployed-agent runtime costs require their own comparison |
| Cloud red teaming supports Foundry prompt and container agents, but its support matrix excludes function tools and non-Azure tools | [Red-team concept](https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent#supported-agents-and-tools) | High for matrix; custom retail MCP and knowledge MCP compatibility remains unresolved |
| Prohibited-actions testing requires review/confirmation of a generated taxonomy; results are synthetic and can include false positives | [Cloud SDK guide](https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-ai-red-teaming-cloud); red-team concept | High; a generated taxonomy is not customer policy or a compliance finding |
| The cloud example configures multi-turn depth, while the concept page labels some agentic risks single-turn | Same two red-team sources | Conflicting documentation; use a minimal verified risk/strategy combination rather than promise multi-turn coverage |
| The repository locks `azure-ai-projects` to 2.7.0; the current agent-evaluation guide requests >=2.8.0 for the shown rubric-generation path | `uv.lock`, `pyproject.toml`; [agent evaluation guide](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluate-agent) | High; compatible dependency update may be needed during implementation, not installed during planning |
| Model inference in evaluation needs account-scope access; trace and continuous workflows add identity-specific permissions | [Evaluation permissions](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-permissions) | High; project access alone is not evidence that every workflow is authorized |

### Researcher recommendations, not approved implementation choices

- Earlier recommendation, now suspended: use the portal prompt-agent path for the core rubric-to-Optimizer exercise. The user has asked to determine hosted-agent suitability first.
- Investigate a minimal model set with two genuinely different tiers. An eligible larger deployment might serve as both baseline and optimization model, while a smaller deployment might serve as judge and lower-cost candidate. Validate roles, rubric calibration, versions, and model support before selecting these defaults.
- Optimize instructions and compare models; keep MCP tool interfaces fixed. Inspect tool-call evidence separately and retain safety and deterministic release gates.
- Preserve the full read-only knowledge/MCP agent as a core learning requirement. If cloud red teaming cannot use its tools, ask whether a clearly labeled separate safety-test configuration is acceptable. Do not silently remove tools or imply that a reduced configuration validates the full agent.
- Bound red-team scope and optimization candidates for a controlled lab. Cost estimates remain estimates, not enforced budgets.

### Remaining feasibility evidence

- Verify one actual rubric creation and selection in Optimizer with the intended schema and judge.
- Verify custom MCP and knowledge-tool compatibility for the selected cloud red-team risk. If unsupported, confirm the alternate safety-test scope with the user.
- Verify actual available model versions, quota, runtime-cost evidence, and effective identity permissions.
- Partner observations remain deferred. Technical documentation does not validate learner difficulty or commercial impact.

## Hosted-agent architecture investigation

User statement:

> Hold up> Prompt Based agents are actually being deinvested in. Hosted Agents are the recommended path forward. So should we instead make this whole new module use Hosted agents instead? Let's explore and make that determiniation first.

### Observations

- [The public overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview) still recommends prompt agents for a first agent and documents hosted agents for custom-code control. It does not establish prompt-agent deprecation. The user's roadmap context and public lifecycle claims must remain separate.
- [The hosted optimization quickstart](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-optimize-hosted-agent) explicitly requires the subscription to be allowlisted for Agent Optimizer. This is a documented prerequisite, not a verified restriction on the user's actual subscription.
- On the user's follow-up, rechecked [the main Optimizer overview](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-overview). It lists supported agent types, regions, and the Responses protocol requirement, but does not state an allowlist requirement. Omission does not establish unrestricted access; the quickstart statement does not prove that every current subscription is gated.
- [Hosted evaluator guidance](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/create-optimizer-dataset) supports custom rubric evaluators, including an editable generated rubric registered through the evaluation update flow.
- [Hosted optimization configuration](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/optimize-agent-targets) supports candidate model deployments and a held-out validation dataset.
- [Optimizer-ready runtime guidance](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/make-agent-optimizer-ready) requires an optimization package, baseline files, and `load_config()`. Candidate settings must be used by the agent, not merely loaded.
- Existing Module 09 has a Python Agent Framework agent served through Responses and a supplied source-code deployment script. It does not require learner-authored Python. Its runtime includes web search and unrestricted retail MCP; it deliberately omits Foundry IQ.
- Existing Module 10 demonstrates hosted toolbox authentication. [Current hosted guidance](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents#toolbox-in-foundry) recommends the dedicated `FoundryToolbox` integration for Agent Framework rather than a generic MCP client.
- Hosted-agent model/tool access uses a dedicated agent identity; this differs from the project managed identity used by the prompt-agent knowledge recipe. Shared protected knowledge access is a setup/organizer concern.
- Hosted runtime adds CPU/memory consumption charges. Optimizer run usage and ongoing runtime costs remain separate. No prompt-portal pre-run estimate is documented for hosted optimization.
- Hosted container agents are supported red-team targets, but custom-tool support remains unverified. Container hosting does not remove that gap.

### Interpretation and open gates

Hosted agents appear compatible with the learning scope if a complete optimizer-ready agent and supplied scripts hide deployment mechanics from beginners. This is a recommendation, not an implemented or live-tested result. The important open gates are optimizer eligibility, protected knowledge/tool access, and cloud red-team compatibility. Do not select a prompt fallback without user agreement if these gates fail.

User follow-up establishes that subscription access will not be known in advance. Partners or customers may have to request it. A possible Ignite GA or outdated docs are hypotheses, not confirmed changes. Treat access as a dynamic readiness condition, not an architecture blocker. Preserve the hosted recommendation and mark required Optimizer work incomplete when access is not available. No verified read-only capability endpoint has been identified; readiness must not submit a paid job as an access probe.

## Hosted knowledge/tool integration and fixture observations

### Official integration evidence

- [Use a toolbox with a hosted agent](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/use-toolbox-hosted-agent) documents the Python Agent Framework `FoundryToolbox` integration. It authenticates to Foundry and forwards the runtime's per-request call ID; the project connection determines downstream identity.
- [Toolbox management](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox) lists Azure AI Search and MCP as toolbox tool types. This documents a general hosted knowledge/tool route, not proof that this track's particular knowledge-base MCP endpoint has been tested.
- The same guide distinguishes a version-specific testing endpoint from the consumer endpoint that follows `default_version`. Record the actual toolbox version for evaluation comparisons; an unchanged agent version alone does not freeze its tool configuration.
- Toolbox tool approval is enforced by the agent runtime, not by the MCP endpoint. An approval setting or prompt instruction alone cannot establish the agreed read-only scope. Verify the allowed tool list and executed calls.
- A failing toolbox source can prevent tool enumeration or readiness. Missing knowledge/MCP assets must be reported as prerequisites, rather than silently making the agent answer without grounding.
- Hosted-agent permissions distinguish the learner identity, project identity, and runtime agent identity. The earlier prompt-agent connection cannot be assumed to provide identical access when moved into hosted runtime code.
- The cloud red-team support matrix still does not explicitly settle custom MCP support. A toolbox is a documented integration route, not evidence that every wrapped tool is red-team compatible.

Confidence: high for the quoted documentation contracts; unverified for this track's end-to-end hosted-agent configuration.

### Repository fixture comparison

Read-only parsing of repository data found:

- `shared\data\retail-products.jsonl`: 100 product rows.
- `shared\data\retail-policies.jsonl`: 50 policy rows.
- `shared\mcp-servers\retail-remedy-ops\src\data\retail-operations.json`: three primary product records referenced by the sample receipts.
- None of the three MCP product IDs appears as a Search product ID.
- A sampled Search product is Honey Almond Granola priced in USD. MCP receipts reference laptops, phones, and headphones priced in AUD.
- Search policy samples include loyalty, store-brand warranty, and general refund documents. MCP policy fixtures concern ACL remedies. These files are not a demonstrated coherent source of truth for one evaluation scenario.

Confidence: high for counts, IDs, and sampled content. This is not a legal review or an exhaustive policy-conflict assessment.

### Researcher implication to discuss

Do not treat all existing retail assets as an evaluation-ready fixture set. Recommend retaining reuse of infrastructure and code patterns while supplying a small, aligned scenario dataset with reviewed expected outcomes, clear source ownership, and a fixed scenario date where purchase age matters. Keep any deliberate failure case separate from accidental source mismatch.

The exact retail-remedy scenario is not yet confirmed. A purpose-built fixture set is a proposal, not authorization to rewrite shared data used by other tracks.

## Alternative existing scenarios: research comparison

User question:

> I wonder if we should consider one of the other agents instead of the ACL - which is Australia centric?

Repository observations:

- `labs\agent-framework-dotnet\README.md` describes the Trip Disruption Concierge. It combines flight operations, passenger-rights knowledge, and specialist agents. Its example uses an AKL-to-SYD cancellation. It is not automatically jurisdiction-neutral.
- `shared\mcp-servers\flight-ops\src\server.py` exposes `get_flight_status`, `get_rebooking_options`, and `file_compensation_claim`. The first two provide candidate read-only tasks; the claim-submission tool falls outside the agreed read-only scope even though the fixture is mocked.
- `labs\introduction-foundry-agent-service\03-foundry-toolkit-vscode\README.md` contains a Contoso Outdoors retail assistant prompt for products, orders, and returns. This example does not by itself establish a complete, aligned knowledge/tool dataset.

Researcher recommendation, not a confirmed choice:

- Investigate the travel scenario next, focusing on operational facts and explicitly supplied fictional airline policy rather than legal entitlement advice.
- Compare travel with general retail for audience familiarity before choosing. Travel provides existing operational tool fixtures; general retail provides a simpler prompt but needs aligned supporting data and tools.
- Reusing a scenario does not require adopting the .NET track, its multi-agent design, or previous lab completion. A supplied single Python hosted agent remains a proposal.
- Neither alternative resolves the outstanding hosted custom MCP red-team compatibility question.

Confidence: high for repository observations; learner familiarity and comparative learning value remain unvalidated.

## Flight versus non-ACL retail: evaluation teaching comparison

User direction:

> Yes, let's explore the flight-disruption assistant agent as an option. But still consider the general retail agent (without the ACL components). Contrast which would provide the better scenarios for demonstraton of evaluations and rubrics

### Further repository observations

- Flight MCP has three status fixtures and three rebooking options. Option fields include seat availability, cabin, and departure/arrival timestamps. These support factual and constraint-based checks without legal entitlement judgments.
- `get_rebooking_options` filters on route and echoes the supplied booking reference. It does not validate booking ownership or passenger eligibility. A successful tool call must not be presented as evidence that these were checked.
- Flight fixture dates are fixed in June 2025. A proposed reproducible exercise needs an explicit scenario clock and reviewed time-zone data, rather than comparisons against the learner's current date.
- The passenger knowledge corpus has 12 documents, including compensation, delays, denied boarding, and re-routing. Removing ACL from the comparison does not make the existing travel knowledge jurisdiction-neutral; reviewed fictional airline policy would be a separate proposed fixture.
- Retail MCP has purchase, product-profile, policy-search, and replacement-option lookups. Its product notes, policy excerpts, and some replacement notes carry ACL assumptions. Removing an ACL sentence from the system prompt would not remove that content.
- General retail product matching, order status, or returns-policy advice would need an explicitly chosen task boundary and aligned data. The existing Contoso Outdoors prompt is not a ready implementation of these tasks.

### Researcher comparison, not validated learner findings

| Teaching need | Flight disruption | Non-ACL retail |
|---|---|---|
| Simple factual checks | Flight status and available seats | Product facts, stock, price, or purchase details |
| Tool-use checks | Correct flight/route, status plus options when needed | Correct receipt/product, product plus stock/policy when needed |
| Domain rubric | Feasible plan, respect stated priorities, explain compromises, distinguish recommendation from booking | Suitable recommendation, respect budget/preferences, explain compromises, distinguish advice from purchase/refund |
| Multiple acceptable answers | Naturally visible when departure, cabin, and group seating compete | Strong when product requirements compete; weaker if limited to FAQ answers |
| Abstention | No suitable flight or unverified booking eligibility | Missing product facts, unavailable stock, or unknown policy |
| Cost-quality comparison | Check that shorter/cheaper candidates retain constraints and useful alternatives | Check that shorter/cheaper candidates retain product suitability and policy evidence |
| Preparation | Small operations fixture exists; policy, date/time, and scope review needed | Existing read-only patterns exist; aligned neutral catalog/policy/tool data needed |

Provisional recommendation: investigate flight as the lead candidate for the full rubric-to-optimization journey, with retail retained as the simpler alternative. This is a pedagogical judgment, not evidence that flight yields better measured learning outcomes or guaranteed model savings.

Comparison examples remain illustrative task concepts, not generated evaluation rows or approved ground truth. Factual constraint checks should remain distinct from rubric judgment of explanation quality. A pleasant answer must not compensate for an infeasible recommendation. Custom MCP cloud red-team compatibility remains unresolved for both.

## Working scenario decision

User decision:

> Yes, let's use the flight disruption scenario for now.

Flight disruption is now the selected working scenario. Retain general retail as a parked alternative; do not build both. This decision does not establish better learner outcomes, approve cloud execution, or complete Method 2.

The existing read-only constraint remains. Passenger-facing advice versus staff assistance is the next scope question. Reviewed fictional airline policy, a supplied single Python hosted agent, and exclusion of booking/claim actions remain proposed details rather than separately confirmed requirements.

Subsequent user clarification:

> I think it should advise passengers

The agent's intended user is now confirmed as the passenger. The earlier passenger-versus-staff question is resolved. Policy-grounding scope remains open; fictional airline policy is recommended to keep expected outcomes controlled and avoid moving the regional legal-content problem from retail into aviation.

Subsequent policy-boundary decision:

> Yes. Let's avoid real-world legal-entitlement advice.

Clearly labelled fictional airline policy is now confirmed for the working scenario. Real-world legal-entitlement advice is excluded. The earlier open policy question is resolved.

Research implications: do not reuse the existing rights-focused corpus unchanged or treat model knowledge of passenger law as expected truth. Future evaluation design should distinguish adherence to the fictional policy from claims about real-world rights. The exact policy text, handling of out-of-scope legal questions, and expected evaluation outcomes still need review; no dataset is generated by this decision.

## Establishing red-team support: evidence plan

Rechecked official documentation on 2026-11-03:

- [Concept and support matrix](https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent): Foundry hosted container agents and Azure tool calls are supported; non-Azure tools and function tool calls are not. Custom remote MCP classification is not explicit. The page links to toolboxes but that does not establish support for every toolbox source.
- [Cloud SDK procedure](https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-ai-red-teaming-cloud): documents agent targets by name/version, taxonomy review, run status, and output-item retrieval.
- Agentic tests use synthetic data and mocked tool outputs. Distinguish testing agent behavior under these inputs from testing the real flight MCP service, access controls, or production data handling.

Recommended evidence sequence, not authorization to execute:

1. Ask the Foundry red-teaming product team, or Azure support, about the exact configuration: a Python Responses hosted agent using FoundryToolbox, a custom remote flight MCP deployed on Azure Container Apps, and policy knowledge retrieval. Ask which agentic risk categories and indirect-injection paths cover it, whether outputs are mocked or real tools invoked, and how reports identify unsupported or skipped tools.
1. Record the service/API and SDK versions, region, supported topology, and stated restrictions. Azure hosting alone does not classify the custom tool as a supported Azure tool.
1. After separate environment and cost approval, run a small non-production feasibility test in stages: hosted baseline without external tools; then read-only flight MCP; then the intended policy retrieval/toolbox configuration.
1. Require the exact intended tool configuration to be accepted and relevant output items to be scored without unexplained exclusions. Inspect available tool coverage and evidence of the documented simulation path. If reports do not expose enough evidence, retain a coverage gap and ask the product team.
1. Separate authorization/network/quota failures from unsupported configuration. A successful job demonstrates observed operation, not a general support commitment or proof of all real-tool protections.

No live feasibility test has run. The user asked for the discovery method, not permission to deploy or submit a paid scan.

## Clarification: agent scans versus tool-mediated coverage

User challenge:

> When it says "Not Azure tools" - if we're red-teaming the agent, and an agent is calling our remote MCP tools, does this actually prevent it working or is it specifically talking about red-teaming the tool itself, not the Agent calling the tools? This might be conflating 2 things.

Correction to earlier broad blocker framing:

- The official matrix is introduced as support for red teaming Foundry agents with Azure tool calls. It is not a matrix for penetration testing MCP servers independently.
- Distinguish response-level agent testing from tool-mediated agentic tests that require supported tool context or synthetic tool-output injection, and from security testing of the backend MCP service itself.
- Hosted container agents are documented targets. The matrix does not explicitly say whether a custom remote MCP dependency causes whole-run rejection, is left running normally, is excluded, or limits particular risk categories. Do not select any of these interpretations without evidence.
- Tool simulation and indirect prompt injection restrictions may be narrower than basic agent invocation support. That is a hypothesis, not a confirmed interpretation of the service.
- The outstanding question is exact execution and coverage, not an established inability to red team an agent that has remote tools.
- Ask separately whether ordinary content-risk scans accept the unchanged hosted agent, and which agentic tests can observe, mock, or inject into custom remote MCP tool results. No backend-security claim follows from either answer.

Evidence: re-read the official concept page's agentic risks, supported agents/tools, and known limitations sections on 2026-11-03. A targeted public-source search found no explicit custom-MCP clarification. No live scan was run.
