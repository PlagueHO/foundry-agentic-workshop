---
description: "Test the organizer guide end-to-end: provision, RBAC, AI Search, and output validation"
argument-hint: "azureLocation=... resourceGroup=... environmentName=..."
---

## Inputs

* ${input:azureLocation}: (Required) Azure region to deploy to (e.g., `AustraliaEast`).
* ${input:resourceGroup}: (Required) Azure resource group name (e.g., `rg-foundry-hol`).
* ${input:environmentName}: (Required) azd environment name (e.g., `foundry-hol`).

You must test the steps in the #file:docs/guide-organizer.md.

The list of UPNs to use are:

```json
[{"upn":"lab.attendee.1@MngEnvMCAP199525.onmicrosoft.com"},{"upn":"lab.attendee.2@MngEnvMCAP199525.onmicrosoft.com"},{"upn":"lab.attendee.3@MngEnvMCAP199525.onmicrosoft.com"},{"upn":"lab.facilitator.1@MngEnvMCAP199525.onmicrosoft.com","role":"facilitator"},{"upn":"lab.organizer.1@MngEnvMCAP199525.onmicrosoft.com","role":"organizer"},{"upn":"lab.proctor.1@MngEnvMCAP199525.onmicrosoft.com","role":"proctor"}]
```

The Azure Location should be `${input:azureLocation}`. The default role should be `foundry-project-manager`. The resource group should be `${input:resourceGroup}`. The environment name should be `${input:environmentName}`. I have already authenticated to az and azd. The provisioning will take some time.

You must validate that:

1. The AI Search has been populated.
1. The RBAC roles are assigned correctly.
1. The CSV and MD outputs produced by the pre-provision #file:scripts/prepare-attendee-roles.py and post-provision #file:scripts/generate-attendee-onboarding.py are complete and show the correct output and are in the right place (`.azure/<envname>`).
1. The onboarding index (`index.json`) and per-attendee markdown files were uploaded to Azure Blob Storage by #file:scripts/generate-attendee-onboarding.py (confirm from hook output that upload log lines appear for both the index and the markdown backups).
1. The Attendee Onboarding Portal was deployed by #file:scripts/deploy-attendee-portal.py - confirm the portal image was built and pushed to the container registry, the Container App was updated, and EasyAuth was configured.
