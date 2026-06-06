data "azurerm_client_config" "current" {}

data "azuread_user" "attendee_by_upn" {
  for_each = toset(var.attendee_user_principal_names)

  user_principal_name = each.value
}

locals {
  attendee_project_names = [for i in range(var.attendee_count) : format("%s-%02d", var.attendee_project_prefix, i + 1)]
  attendee_principal_ids = concat(
    var.attendee_object_ids,
    [for upn in var.attendee_user_principal_names : data.azuread_user.attendee_by_upn[upn].object_id]
  )

  foundry_user_role_definition_id            = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/53ca6127-db72-4b80-b1b0-d745d6d5456d"
  foundry_project_manager_role_definition_id = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/eadc314b-1a2d-4efa-be10-5d325db5065e"

  project_user_assignments = {
    for idx, principal_id in local.attendee_principal_ids :
    tostring(idx) => {
      principal_id  = principal_id
      project_name  = local.attendee_project_names[idx]
      project_scope = azapi_resource.attendee_projects[local.attendee_project_names[idx]].id
    }
    if idx < length(local.attendee_project_names)
  }

  resource_scope_assignments = {
    for idx, principal_id in local.attendee_principal_ids :
    tostring(idx) => {
      principal_id = principal_id
    }
  }

  foundry_resource_id = format(
    "/subscriptions/%s/resourceGroups/%s/providers/Microsoft.CognitiveServices/accounts/%s",
    data.azurerm_client_config.current.subscription_id,
    azurerm_resource_group.workshop.name,
    var.foundry_name
  )

  search_resource_id = format(
    "/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Search/searchServices/%s",
    data.azurerm_client_config.current.subscription_id,
    azurerm_resource_group.workshop.name,
    var.search_name
  )
}

resource "azurerm_resource_group" "workshop" {
  name     = var.resource_group_name
  location = var.location
  tags = {
    workshop    = "foundry-agentic"
    environment = var.env_name
  }
}

module "foundry_account" {
  source  = "Azure/avm-res-cognitiveservices-account/azurerm"
  version = "~> 0.11.0"

  name                     = var.foundry_name
  location                 = var.location
  parent_id                = azurerm_resource_group.workshop.id
  kind                     = "AIServices"
  sku_name                 = var.foundry_sku
  custom_subdomain_name    = var.foundry_name
  allow_project_management = true
}

module "search_service" {
  source  = "Azure/avm-res-search-searchservice/azurerm"
  version = "~> 0.2.0"

  name                = var.search_name
  location            = var.location
  resource_group_name = azurerm_resource_group.workshop.name
}

module "storage_account" {
  source  = "Azure/avm-res-storage-storageaccount/azurerm"
  version = "~> 0.7.2"

  name                      = var.storage_account_name
  location                  = var.location
  resource_group_name       = azurerm_resource_group.workshop.name
  shared_access_key_enabled = false
}

resource "azapi_resource" "attendee_projects" {
  for_each = toset(local.attendee_project_names)

  type      = "Microsoft.CognitiveServices/accounts/projects@2024-10-01-preview"
  name      = each.value
  parent_id = local.foundry_resource_id
  location  = var.location

  body = {
    properties = {
      displayName = each.value
      description = "Workshop attendee project ${each.value}"
    }
  }

  depends_on = [module.foundry_account]

  schema_validation_enabled = false
}

resource "azapi_resource" "foundry_search_connection" {
  type      = "Microsoft.CognitiveServices/accounts/connections@2024-10-01"
  name      = var.foundry_search_connection_name
  parent_id = local.foundry_resource_id

  body = {
    properties = {
      category                    = "CognitiveSearch"
      target                      = local.search_resource_id
      authType                    = "SystemAssignedManagedIdentity"
      isSharedToAll               = true
      useWorkspaceManagedIdentity = true
      metadata = {
        resourceType = "AISearch"
      }
    }
  }

  depends_on = [module.foundry_account, module.search_service]

  schema_validation_enabled = false
}

resource "azurerm_role_assignment" "attendee_foundry_user_project" {
  for_each = var.attendee_access_profile == "project-user" ? local.project_user_assignments : {}

  scope              = each.value.project_scope
  role_definition_id = local.foundry_user_role_definition_id
  principal_id       = each.value.principal_id
}

resource "azurerm_role_assignment" "attendee_reader_resource" {
  for_each = var.attendee_access_profile == "project-user" ? local.resource_scope_assignments : {}

  scope                = local.foundry_resource_id
  role_definition_name = "Reader"
  principal_id         = each.value.principal_id
}

resource "azurerm_role_assignment" "attendee_project_manager_resource" {
  for_each = var.attendee_access_profile == "project-publisher" ? local.resource_scope_assignments : {}

  scope              = local.foundry_resource_id
  role_definition_id = local.foundry_project_manager_role_definition_id
  principal_id       = each.value.principal_id
}
