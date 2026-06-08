# Facilitator Guide

This guide covers how to deliver the workshop: pacing, per-lab facilitation, and the issues
attendees hit most often. For the condensed flow, see the
[Facilitator Quickstart](./quickstart-facilitator.md).

## Delivery goals

- Keep modules interactive and time-boxed.
- Encourage pair troubleshooting before the solution reveal.
- Keep every attendee productive — pull in a [proctor](./guide-proctor.md) early when
  someone is blocked.

## Prepare

1. Clone this repository to your machine.

   ```bash
   git clone https://github.com/PlagueHO/foundry-agentic-workshop.git
   cd foundry-agentic-workshop
   ```

1. Confirm the organizer has provisioned the environment and run `azd up` (or `azd provision`).
   The preprovision hook (`scripts/prepare-attendee-roles.py`) resolves UPNs to Entra object IDs
   and writes a resolution audit CSV to `.azure/<env>/attendee-resolution-<env>-<ts>.csv`.
   The postprovision hook (`scripts/generate-attendee-onboarding.py`) writes:
   - A per-attendee onboarding markdown file to `.azure/<env>/<upn_local>.md` for every resolved attendee.
   - A provisioning summary CSV to `.azure/<env>/attendee-provisioning-<env>-<ts>.csv`.
1. **Distribute per-attendee onboarding files.** Locate each `.azure/<env>/<upn_local>.md` file and
   send it to the corresponding attendee before the session. Each file contains the attendee's
   pre-populated `.env` values, sign-in commands, and setup instructions. Attendees whose UPNs
   could not be resolved will not have a file; follow up with the organizer for those cases.
1. Run all labs once on a `foundry-user` test identity. This surfaces the same
   least-privilege constraints attendees experience (for example, no model deployment).
1. Confirm proctors have the attendee assignment list and the [Proctor Guide](./guide-proctor.md).

## Configuring models

The workshop deploys a fixed set of models defined in [`infra/model-deployments.json`](../infra/model-deployments.json). To add or change deployed models, edit that file before running `azd provision`.

Each entry in the file follows this structure:

```json
{
  "name": "chat",
  "model": {
    "format": "OpenAI",
    "name": "gpt-4o",
    "version": "2024-11-20"
  },
  "sku": {
    "name": "GlobalStandard",
    "capacity": 120
  },
  "raiPolicyName": "FoundryWorkshopContentPolicy"
}
```

Two deployments are required for all lab sample code to work without modification:

* A deployment named `chat` pointing to a ChatCompletions-compatible model (for example, `gpt-4o`).
* A deployment named `embedding` pointing to an Embeddings-compatible model (for example, `text-embedding-3-small`).

Additional models can be added alongside these two as long as they are available in your target region.

To discover which models are available in your target region, run:

```bash
az cognitiveservices model list -l australiaeast --query '[?model.deprecation.deprecationStatus == `null`].{Name:model.name, Publisher:model.publisher, Kind:kind, SkuName:model.skus[0].name, MaxCapacity:model.skus[0].capacity.maximum}' --output table
```

Replace `australiaeast` with the region matching `AZURE_LOCATION` in your environment.
The filter excludes models with no deprecation status set, which typically indicates
preview or unlisted entries.

## Suggested pacing

The full workshop runs 3–4 hours. Work through labs in sequence, time-boxing each module. Block on setup until every attendee passes `python scripts/health-check.py` before moving on; unresolved setup issues compound throughout the session.

Protect time for the core agent-building labs. Treat later optional labs as depth-adds and trim their scope when the session is running behind. If attendees are on the default `foundry-user` role, some labs may not be completable independently; treat those as live demonstrations.

## Lab facilitation

- Frame each lab with the problem it solves before attendees open the starter.
- Let attendees attempt the starter; reveal the `solution/` only after a genuine attempt.
- Remind attendees that each lab is independently runnable, so a blocked attendee can move on and return later.

## Common issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Health check fails at setup | Sign-in or `.env` value missing. | Re-run `az login`; confirm assignment values. |
| Attendee cannot deploy a model | Expected on the `foundry-user` role. | Point them to the pre-deployed models. |
| Attendee cannot perform an action in a lab | The lab may require an elevated Foundry role. | Have the organizer raise the role, or demonstrate it live. |
| Attendee fell behind | Long-running step or distraction. | Each lab is self-contained; resume at the current module. |

## Fallback

Keep one demo project as a fallback for an attendee whose assignment is blocked, and let a
proctor pair them on it while you continue delivery.
