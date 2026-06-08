# Proctor Guide

Proctors give floor support during delivery so the facilitator can keep teaching. Keep this
guide and the attendee assignment list handy throughout the session.

## Before the session

1. Clone this repository to your machine.

   ```bash
   git clone https://github.com/PlagueHO/foundry-agentic-workshop.git
   cd foundry-agentic-workshop
   ```

1. Get the attendee assignment list from the organizer (UPN to `FOUNDRY_PROJECT_NAME`).
1. Confirm the environment is provisioned: run `python scripts/list-attendee-projects.py` to see the expected project names.
1. Keep one demo project as a fallback for an attendee whose assignment is blocked.

## During the session

- Watch for blocked attendees during setup and the first lab — most issues surface there.
- Triage with the [Attendee Guide troubleshooting table](./guide-attendee.md#troubleshooting) before escalating.
- Each lab is independently runnable, so help a blocked attendee move on and return later.
- Escalate to the facilitator only when an issue affects multiple attendees.
- Watch for model 503 issues and increase quotas as needed.

## Common requests

| Request | Action |
|---------|--------|
| Attendee cannot sign in | Re-run `az login` and `az account set --subscription <id>`. |
| Attendee cannot find their project | Confirm their `FOUNDRY_PROJECT_NAME` against the assignment list. |
| Attendee cannot deploy a model | Expected on `foundry-user`; point to the pre-deployed models. |
| Attendee cannot perform an action in a lab | The lab may require an elevated Foundry role; note it for the organizer to review. |
