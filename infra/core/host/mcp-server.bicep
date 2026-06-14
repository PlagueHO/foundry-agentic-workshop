metadata name = 'MCP Server (Azure Container Apps)'
metadata description = 'Deploys the Module 06 Retail Remedy Operations MCP server as a publicly reachable HTTPS Container App into the shared Azure Container Apps environment. The cloud-hosted Foundry agent connects to this endpoint when a local dev tunnel is unreachable.'

@description('Required. Name of the Container App that hosts the MCP server.')
@maxLength(32)
param containerAppName string

@description('Required. Resource ID of the shared Container Apps managed environment that hosts the MCP server.')
param containerAppsEnvironmentResourceId string

@description('Required. Name of the user-assigned managed identity used to pull the image from the shared Container Registry.')
param userAssignedIdentityName string

@description('Required. Login server of the shared Azure Container Registry that hosts the MCP server image.')
param containerRegistryLoginServer string

@description('Optional. Location for all resources.')
param location string = resourceGroup().location

@description('Optional. Tags to apply to all resources.')
param tags object = {}

@description('Optional. Container image reference for the MCP server. Defaults to a public placeholder image that scripts/deploy-mcp-server.py replaces with the built image.')
param containerImage string = 'mcr.microsoft.com/k8se/quickstart:latest'

@description('Optional. Port the MCP server listens on inside the container.')
param targetPort int = 8080

// User-assigned managed identity used by the Container App to pull the image from the shared
// Container Registry. The matching 'Container Registry Repository Reader' role assignment is
// created by the caller (main.bicep) against the shared registry.
module userAssignedIdentity 'br/public:avm/res/managed-identity/user-assigned-identity:0.5.1' = {
  name: 'mcp-server-identity'
  params: {
    name: userAssignedIdentityName
    location: location
    tags: tags
  }
}

// Container App that hosts the MCP server, deployed into the shared Container Apps environment.
// External ingress exposes the public HTTPS endpoint the agent connects to. A single always-on
// replica keeps the in-memory mock data reachable without a cold start. The placeholder image is
// replaced by scripts/deploy-mcp-server.py, which builds and pushes the real image and rolls the
// Container App to a new revision.
module containerApp 'br/public:avm/res/app/container-app:0.22.1' = {
  name: 'mcp-server-app'
  params: {
    name: containerAppName
    environmentResourceId: containerAppsEnvironmentResourceId
    location: location
    tags: tags
    ingressExternal: true
    ingressTargetPort: targetPort
    ingressAllowInsecure: false
    scaleSettings: {
      minReplicas: 1
      maxReplicas: 1
    }
    managedIdentities: {
      userAssignedResourceIds: [
        userAssignedIdentity.outputs.resourceId
      ]
    }
    registries: [
      {
        server: containerRegistryLoginServer
        identity: userAssignedIdentity.outputs.resourceId
      }
    ]
    containers: [
      {
        name: 'mcp-server'
        image: containerImage
        resources: {
          cpu: json('0.5')
          memory: '1.0Gi'
        }
        env: [
          {
            name: 'MCP_SERVER_PORT'
            value: string(targetPort)
          }
        ]
      }
    ]
  }
}

@description('The name of the MCP server Container App.')
output containerAppName string = containerApp.outputs.name

@description('The public HTTPS MCP endpoint (including the /mcp path) for the deployed server.')
output mcpEndpoint string = 'https://${containerApp.outputs.fqdn}/mcp'

@description('The principal ID of the user-assigned managed identity that pulls the image.')
output userAssignedIdentityPrincipalId string = userAssignedIdentity.outputs.principalId
