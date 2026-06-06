# Organizer Quickstart

Use this guide when an organizer deploys one shared Microsoft Foundry environment for multiple learners.

## Prerequisites

1. Azure subscription with sufficient quota.
1. Azure CLI and Azure Developer CLI installed.
1. Python 3.11 or later.

## Sign in

```bash
az login
azd auth login
```

## Create or select an environment

```bash
azd env new hol-shared
azd env select hol-shared
```

## Configure core variables

```bash
azd env set AZURE_LOCATION australiaeast
azd env set AZURE_RESOURCE_GROUP rg-foundry-hol-shared
azd env set AZURE_ATTENDEE_COUNT 20
azd env set AZURE_ATTENDEE_PROJECT_PREFIX attendee
```

## Optional RBAC configuration

If your subscription already grants broad access, skip this section.

```bash
azd env set AZURE_ATTENDEE_ACCESS_PROFILE project-user
azd env set AZURE_ATTENDEE_USER_PRINCIPAL_NAMES '["learner1@contoso.com","learner2@contoso.com"]'
```

Use `project-user` for least-privilege labs 00-07.
Use `project-publisher` when learners need publishing rights for lab 08.

## Provision

```bash
azd provision
```

## Share attendee assignments

```bash
azd env get-value AZURE_ATTENDEE_PROJECT_NAMES
```

Give each learner their assigned `FOUNDRY_PROJECT_NAME`.

## Teardown

```bash
azd down --force --purge
```
