# Facilitator Quickstart

Use this quickstart to deliver the workshop. It is the high-level flow; see the
[Facilitator Guide](./guide-facilitator.md) for pacing, per-lab facilitation, and common
issues.

## Before you teach

1. Clone this repository to your machine.

   ```bash
   git clone https://github.com/PlagueHO/foundry-agentic-workshop.git
   cd foundry-agentic-workshop
   ```

1. Confirm the organizer has run `azd up`. Collect the per-attendee onboarding markdown files from `.azure/<env>/<upn_local>.md` and send each file to the corresponding attendee. See the [Facilitator Guide](./guide-facilitator.md#prepare) for details on what these files contain and how the provisioning hooks produce them.
1. Run the labs end to end once on a `foundry-user` test identity so you hit the same constraints attendees do.
1. Confirm proctors have the [Proctor Guide](./guide-proctor.md) and the attendee assignment list.

## During delivery

1. Open with the [workshop overview](./index.md) and the architecture context.
1. Have attendees complete the [Attendee Quickstart](./quickstart-attendee.md) setup and run `python scripts/health-check.py` before the first lab.
1. Work through lab modules in order, time-boxing each module. See the [Facilitator Guide](./guide-facilitator.md#suggested-pacing) for pacing guidance.
1. For each, module run the attendees through the key concepts and what they should see and tasks to perform. Indicate common issues to watch for and how to resolve them. See the [Facilitator Guide](./guide-facilitator.md) for details.

## If you run short on time

- Trim depth on the optional labs first; the core agent-building labs take priority.
- Use the `solution/` folder for live demonstrations when a lab cannot be completed independently.
- If attendees are on the default `foundry-user` role, some labs may not be completable independently; demonstrate those live.
