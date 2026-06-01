data "azurerm_client_config" "current" {}

locals {
  attendee_project_names = [for i in range(var.attendee_count) : format("%s-%02d", var.attendee_project_prefix, i + 1)]

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
  version = "~> 0.1.0"

  name                = var.search_name
  location            = var.location
  resource_group_name = azurerm_resource_group.workshop.name
}

module "storage_account" {
  source  = "Azure/avm-res-storage-storageaccount/azurerm"
  version = "~> 0.6.0"

  name      = var.storage_account_name
  location  = var.location
  parent_id = azurerm_resource_group.workshop.id
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
      category                     = "CognitiveSearch"
      target                       = local.search_resource_id
      authType                     = "SystemAssignedManagedIdentity"
      isSharedToAll                = true
      useWorkspaceManagedIdentity = true
      metadata = {
        resourceType = "AISearch"
      }
    }
  }

  depends_on = [module.foundry_account, module.search_service]

  schema_validation_enabled = false
}
