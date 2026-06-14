metadata name = 'Azure Container Apps Environment'
metadata description = 'Deploys the shared Azure Container Apps managed environment that hosts workshop services such as MCP servers. The environment is created once and reused by every service Container App.'

@description('Required. Name of the Container Apps managed environment.')
param containerAppsEnvironmentName string

@description('Required. Resource ID of the Log Analytics workspace used for Container Apps logs.')
param logAnalyticsWorkspaceResourceId string

@description('Optional. Location for all resources.')
param location string = resourceGroup().location

@description('Optional. Tags to apply to all resources.')
param tags object = {}

// Container Apps managed environment shared by every workshop service Container App. Public network
// access is enabled so the cloud-hosted Foundry agent can reach published services over HTTPS. Zone
// redundancy is disabled because the environment is consumption-only and is not deployed into a
// virtual network.
module containerAppsEnvironment 'br/public:avm/res/app/managed-environment:0.13.3' = {
  name: 'container-apps-environment'
  params: {
    name: containerAppsEnvironmentName
    location: location
    tags: tags
    zoneRedundant: false
    publicNetworkAccess: 'Enabled'
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsWorkspaceResourceId: logAnalyticsWorkspaceResourceId
    }
  }
}

@description('The resource ID of the Container Apps managed environment.')
output resourceId string = containerAppsEnvironment.outputs.resourceId

@description('The name of the Container Apps managed environment.')
output name string = containerAppsEnvironment.outputs.name
