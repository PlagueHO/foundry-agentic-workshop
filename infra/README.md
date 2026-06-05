# Infrastructure (Terraform + azd)

This workshop uses Terraform with Azure Verified Modules (AVM) and AzAPI.

## What gets deployed

- 1 shared Azure AI Foundry account
- N attendee projects under the shared Foundry account (`attendee_count`)
- 1 shared Azure AI Search service
- 1 shared Azure Storage account
- 1 Foundry connection resource targeting the shared Search service

## Technology choices

- **AVM modules**
  - `Azure/avm-res-cognitiveservices-account/azurerm`
  - `Azure/avm-res-search-searchservice/azurerm`
  - `Azure/avm-res-storage-storageaccount/azurerm`
- **AzAPI resources**
  - `Microsoft.CognitiveServices/accounts/projects@2024-10-01-preview`
  - `Microsoft.CognitiveServices/accounts/connections@2024-10-01`

## Parameters

Copy `terraform.tfvars.example` if you want local tfvars workflows, or set equivalent values with `azd env set TF_VAR_*`.

Primary workshop variables:

- `location`
- `resource_group_name`
- `attendee_count`
- `attendee_project_prefix`
- `foundry_name`
- `search_name`
- `storage_account_name`

## Deploy with azd

```bash
az login
azd auth login
./deploy.sh hol australiaeast rg-foundry-hol 20
```

## Teardown with azd

```bash
./teardown.sh hol
```
