metadata name = 'Attendee Onboarding Portal (Azure Container Apps)'
metadata description = 'Deploys the Attendee Onboarding Portal as an authenticated Container App into the shared Azure Container Apps environment. Attendees visit the published URL, sign in with their lab Entra ID account, and see their personal onboarding configuration. Authentication is handled by Container Apps built-in EasyAuth — no custom auth code is required in the application.'

@description('Required. Name of the Container App that hosts the attendee portal.')
@maxLength(32)
param containerAppName string

@description('Required. Resource ID of the shared Container Apps managed environment that hosts the portal.')
param containerAppsEnvironmentResourceId string

@description('Required. Name of the user-assigned managed identity used to pull the image from the shared Container Registry and read onboarding data from blob storage.')
param userAssignedIdentityName string

@description('Required. Login server of the shared Azure Container Registry that hosts the portal image.')
param containerRegistryLoginServer string

@description('Required. Name of the Azure Storage Account that holds the attendee onboarding index blob.')
param storageAccountName string

@description('Optional. Name of the blob container that holds the attendee onboarding index.')
param onboardingContainerName string = 'attendee-onboarding'

@description('Optional. Location for all resources.')
param location string = resourceGroup().location

@description('Optional. Tags to apply to all resources.')
param tags object = {}

@description('Optional. Container image reference for the portal. Defaults to a public placeholder image that scripts/deploy-attendee-portal.py replaces with the built image.')
param containerImage string = 'mcr.microsoft.com/k8se/quickstart:latest'

@description('Optional. Port the portal listens on inside the container.')
param targetPort int = 8000

@description('Required. Resource ID of the Log Analytics workspace to send diagnostic logs and metrics to.')
param logAnalyticsWorkspaceResourceId string

// User-assigned managed identity used by the Container App to pull the image from the shared
// Container Registry and to authenticate against blob storage with DefaultAzureCredential.
// The caller (main.bicep) assigns the matching ACR Reader and Storage Blob Data Reader roles.
module userAssignedIdentity 'br/public:avm/res/managed-identity/user-assigned-identity:0.5.1' = {
  name: 'attendee-portal-identity'
  params: {
    name: userAssignedIdentityName
    location: location
    tags: tags
  }
}

// Container App that hosts the attendee portal, deployed into the shared Container Apps
// environment. External ingress exposes the public HTTPS endpoint. A single always-on replica
// keeps the portal responsive without cold-start delay. The placeholder image is replaced by
// scripts/deploy-attendee-portal.py, which builds and pushes the real image, rolls the Container
// App to a new revision, and wires Container Apps EasyAuth.
module containerApp 'br/public:avm/res/app/container-app:0.22.1' = {
  name: 'attendee-portal-app'
  params: {
    name: containerAppName
    environmentResourceId: containerAppsEnvironmentResourceId
    location: location
    tags: tags
    ingressExternal: true
    ingressTargetPort: targetPort
    ingressAllowInsecure: false
    diagnosticSettings: [
      {
        workspaceResourceId: logAnalyticsWorkspaceResourceId
      }
    ]
    scaleSettings: {
      // Zero minimum allows provisioning to succeed with the placeholder image (which
      // listens on port 80, not 8000). The Container App scales up from zero on the first
      // HTTP request after scripts/deploy-attendee-portal.py replaces the image.
      minReplicas: 0
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
        name: 'attendee-portal'
        image: containerImage
        resources: {
          cpu: json('0.25')
          memory: '0.5Gi'
        }
        env: [
          {
            name: 'AZURE_STORAGE_ACCOUNT_NAME'
            value: storageAccountName
          }
          {
            name: 'ATTENDEE_ONBOARDING_CONTAINER'
            value: onboardingContainerName
          }
          {
            name: 'PORT'
            value: string(targetPort)
          }
          {
            name: 'AZURE_CLIENT_ID'
            value: userAssignedIdentity.outputs.clientId
          }
        ]
      }
    ]
  }
}

@description('The name of the attendee portal Container App.')
output containerAppName string = containerApp.outputs.name

@description('The public HTTPS URL of the attendee portal.')
output portalUrl string = 'https://${containerApp.outputs.fqdn}'

@description('The principal ID of the user-assigned managed identity that pulls images and reads blobs.')
output userAssignedIdentityPrincipalId string = userAssignedIdentity.outputs.principalId
