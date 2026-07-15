@description('The globally unique name of the Azure Bot Service resource.')
@minLength(2)
@maxLength(64)
param botServiceName string

@description('The display name shown for the bot.')
param displayName string = 'ACL Remedy Advisor'

@description('The Microsoft Entra application (Microsoft App) client ID.')
param appClientId string

@description('The Microsoft Entra tenant ID for the single-tenant bot.')
param tenantId string

@description('The public HTTPS endpoint for the proxy, including /api/messages.')
param messagingEndpoint string

@description('The Azure region for the Bot Service resource.')
param location string = resourceGroup().location

@description('The Bot Service SKU. F0 is sufficient for workshop testing.')
@allowed([
  'F0'
  'S1'
])
param skuName string = 'F0'

@description('Resource tags applied to the Bot Service.')
param tags object = {}

resource botService 'Microsoft.BotService/botServices@2022-09-15' = {
  name: botServiceName
  location: location
  tags: tags
  sku: {
    name: skuName
  }
  kind: 'azurebot'
  properties: {
    displayName: displayName
    endpoint: messagingEndpoint
    msaAppId: appClientId
    msaAppType: 'SingleTenant'
    msaAppTenantId: tenantId
  }
}

resource teamsChannel 'Microsoft.BotService/botServices/channels@2022-09-15' = {
  parent: botService
  name: 'MsTeamsChannel'
  location: location
  properties: {
    channelName: 'MsTeamsChannel'
  }
}

output botServiceId string = botService.id
output appClientId string = appClientId
