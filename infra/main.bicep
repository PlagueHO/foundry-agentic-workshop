targetScope = 'subscription'

import { capabilityHostType } from './cognitive-services/accounts/capabilityHost/main.bicep'

@description('A single workshop attendee parsed from AZURE_ATTENDEE_LIST.')
type attendeeType = {
  @description('Attendee user principal name (UPN).')
  upn: string

  @description('Optional Foundry role key. Defaults to attendeeDefaultRole.')
  role: string?

  @description('Whether the attendee receives a dedicated project. Defaults to true.')
  individualProject: bool?

  @description('Optional explicit project name. Defaults to "<prefix>-NN" by list position.')
  projectName: string?
}

@description('A resolved attendee entry from the preprovision hook (scripts/prepare-attendee-roles.py).')
type resolvedAttendeeType = {
  @description('Attendee user principal name (UPN).')
  upn: string

  @description('Microsoft Entra object ID. Empty string when UPN resolution failed.')
  objectId: string

  @description('Precomputed Foundry project name, mirrors infra/main.bicep name derivation.')
  projectName: string

  @description('Effective role key (default applied by the preprovision hook).')
  role: string

  @description('Whether the attendee receives a dedicated project.')
  individualProject: bool?

  @description('True when the UPN was successfully resolved to an Entra object ID.')
  resolved: bool
}

// The main bicep module to provision Azure resources for the Microsoft Foundry workshop.
// For a more complete walkthrough to understand how this file works with azd,
// see https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/make-azd-compatible?pivots=azd-create

@minLength(1)
@maxLength(24)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

// Optional parameters to override the default azd resource naming conventions.
// Add the following to main.bicepparam to provide values:
// param resourceGroupName = readEnvironmentVariable('AZURE_RESOURCE_GROUP', 'myGroupName')
//
@description('Name of the resource group to create.')
param resourceGroupName string = ''

@description('Id of the user or app to assign application roles.')
param principalId string = ''

@description('Type of the principal referenced by principalId.')
@allowed([
  'User'
  'ServicePrincipal'
])
param principalIdType string = 'User'

@description('Number of per-attendee Foundry projects to create. Each attendee receives a dedicated project.')
@minValue(0)
@maxValue(50)
param attendeeCount int = 1

@description('Name prefix for per-attendee Foundry projects. Projects are named "<prefix>-NN" (for example, attendee-01).')
@minLength(1)
@maxLength(16)
param attendeeProjectPrefix string = 'attendee'

@description('Structured attendee list parsed from AZURE_ATTENDEE_LIST. When provided, it is the single source of truth for per-attendee project creation; otherwise attendeeCount sequential projects are created.')
param attendeeList attendeeType[] = []

@description('Name prefix for facilitator Foundry projects. Facilitators receive a dedicated project named "<prefix>-NN".')
@minLength(1)
@maxLength(16)
param facilitatorProjectPrefix string = 'facilitator'

@description('Name prefix for proctor Foundry projects. Proctors receive a dedicated project named "<prefix>-NN".')
@minLength(1)
@maxLength(16)
param proctorProjectPrefix string = 'proctor'

@description('Name prefix for organizer Foundry projects. Organizers receive a dedicated project named "<prefix>-NN".')
@minLength(1)
@maxLength(16)
param organizerProjectPrefix string = 'organizer'

@description('Always provision at least one facilitator project, even when no facilitator entry appears in attendeeList.')
param ensureFacilitatorProject bool = true

@description('When true (the default) and attendeeList is provided, project names are derived from the attendee UPN local part (before @, with . and _ replaced by -) instead of sequential prefix-NN names. Has no effect when attendeeList is empty.')
param useUpnProjectNames bool = true

@description('Default Foundry role key applied to attendees without an explicit role. Mirrors AZURE_ATTENDEE_DEFAULT_ROLE.')
@allowed([
  'foundry-user'
  'foundry-project-manager'
  'foundry-account-owner'
  'foundry-owner'
  'facilitator'
  'proctor'
  'organizer'
])
#disable-next-line no-unused-params
param attendeeDefaultRole string = 'foundry-user'

@description('Resolved attendee list from the preprovision hook (scripts/prepare-attendee-roles.py). Each entry carries the Entra object ID and precomputed project name. When empty, no per-attendee role assignments are created.')
param resolvedAttendeeList resolvedAttendeeType[] = []

@description('Enable Azure AI Search as a vector store capability host connection for Foundry agents.')
param azureAiSearchCapabilityHost bool = false

@description('Enable Cosmos DB as a thread storage capability host connection for Foundry agents.')
param cosmosDbCapabilityHost bool = false

@description('Enable Storage Account as a file storage capability host connection for Foundry agents.')
param azureStorageAccountCapabilityHost bool = false

@description('Optional explicit capability hosts to create in the Foundry account.')
param foundryCapabilityHosts capabilityHostType[] = []

@description('SKU for the shared Azure Container Registry used by hosted agents (Module 09). Basic is sufficient for the workshop.')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param containerRegistrySku string = 'Basic'

@description('Deploy the shared Azure Container Apps environment and the services that run in it (such as the Module 06 MCP server). Enabled by default; set to false to skip all Container Apps resources.')
param azureContainerAppsDeploy bool = true

var abbrs = loadJsonContent('./abbreviations.json')
var modelDeployments = loadJsonContent('./model-deployments.json')

// Role definition GUIDs for per-attendee Foundry RBAC assignments. Mirrors ROLE_DEFINITION_IDS
// in scripts/generate-attendee-onboarding.py. Bicep owns this catalog as the authoritative
// source — Python scripts derive their catalogs from this same set of values.
var foundryRoleCatalog = {
  'foundry-user':            '53ca6127-db72-4b80-b1b0-d745d6d5456d'
  'foundry-project-manager': 'eadc314b-1a2d-4efa-be10-5d325db5065e'
  'foundry-account-owner':   'e47c6f54-e4a2-4754-9501-8e0985b135e1'
  'foundry-owner':           'c883944f-8b7b-4483-af10-35834be79c4a'
  facilitator:               'c883944f-8b7b-4483-af10-35834be79c4a'
  proctor:                   'c883944f-8b7b-4483-af10-35834be79c4a'
  organizer:                 'c883944f-8b7b-4483-af10-35834be79c4a'
}

// Azure AI Search role definition GUIDs paired with each Foundry role. Mirrors
// SEARCH_ROLES in scripts/generate-attendee-onboarding.py. Bicep owns this catalog as the
// authoritative source.
//
// Foundry IQ knowledge base and knowledge source creation (Module 07) is authorized through
// the Azure AI Search data plane, not ARM. Creating those objects requires Search Service
// Contributor, and Search Index Data Contributor is additionally needed when a knowledge
// source generates an indexing pipeline or when reading/writing index content. Every lab
// attendee role therefore receives both roles so attendees can create and test their own
// knowledge base against the shared search service. Higher roles keep the broad Contributor
// role for service management and add Search Index Data Contributor for data-plane access.
// See: https://learn.microsoft.com/azure/search/agentic-knowledge-source-overview#creating-knowledge-sources
var searchServiceContributorRoleId = '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
var searchIndexDataContributorRoleId = '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
var searchContributorRoleId = 'b24988ac-6180-42a0-ab88-20f7382dd24c'
var searchRoleCatalog = {
  'foundry-user':            [searchServiceContributorRoleId, searchIndexDataContributorRoleId]
  'foundry-project-manager': [searchServiceContributorRoleId, searchIndexDataContributorRoleId]
  'foundry-account-owner':   [searchServiceContributorRoleId, searchIndexDataContributorRoleId]
  'foundry-owner':           [searchContributorRoleId, searchIndexDataContributorRoleId]
  facilitator:               [searchContributorRoleId, searchIndexDataContributorRoleId]
  proctor:                   [searchContributorRoleId, searchIndexDataContributorRoleId]
  organizer:                 [searchContributorRoleId, searchIndexDataContributorRoleId]
}

// tags that should be applied to all resources.
var tags = {
  // Tag all resources with the environment name.
  'azd-env-name': environmentName
}

var effectiveResourceGroupName = !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
var deploymentId = uniqueString(subscription().id, environmentName, location)
var logAnalyticsName = '${abbrs.operationalInsightsWorkspaces}${environmentName}'
var sendTologAnalyticsCustomSettingName = 'send-to-${logAnalyticsName}'
var applicationInsightsName = '${abbrs.insightsComponents}${environmentName}'
var storageAccounName = take(toLower(replace('${abbrs.storageStorageAccounts}${environmentName}', '-', '')), 24)
var keyVaultName = take(toLower(replace('${abbrs.keyVaultVaults}${environmentName}', '-', '')), 24)
var cosmosDbAccountName = toLower(replace('${abbrs.cosmosDBAccounts}${environmentName}', '-', ''))
var aiSearchName = '${abbrs.aiSearchSearchServices}${environmentName}'
var containerRegistryName = take(toLower(replace('${abbrs.containerRegistryRegistries}${environmentName}', '-', '')), 50)
var containerAppsEnvironmentName = '${abbrs.appManagedEnvironments}${environmentName}'
var mcpServerContainerAppName = take(toLower('${abbrs.appContainerApps}mcp-${environmentName}'), 32)
var mcpServerIdentityName = '${abbrs.managedIdentityUserAssignedIdentities}mcp-${environmentName}'

// Principal that runs scripts/deploy-mcp-server.py and therefore needs push access to the shared
// registry. Prefer an explicit AZURE_PRINCIPAL_ID; otherwise fall back to the principal running
// the deployment (the signed-in user for an interactive `azd provision`).
var containerAppsDeployerPrincipalId = !empty(principalId) ? principalId : deployer().objectId
var containerAppsDeployerPrincipalType = !empty(principalId) ? principalIdType : 'User'
var aiFoundryName = '${abbrs.aiFoundryAccounts}${environmentName}'
var aiFoundryCustomSubDomainName = aiFoundryName // toLower(replace(aiFoundryName, '-', ''))

// Build per-attendee and per-role Foundry projects. Role assignments are created here
// in Bicep using the Entra object IDs resolved by the preprovision hook
// (scripts/prepare-attendee-roles.py), which emits AZURE_ATTENDEE_LIST_RESOLVED with
// objectId and precomputed projectName for each attendee.
//
// Attendees with role 'facilitator', 'proctor', or 'organizer' receive projects under
// their role-specific prefix (e.g. facilitator-01). All other attendees use the standard
// attendeeProjectPrefix. When attendeeList is empty the fallback is attendeeCount sequential
// projects. The preprovision hook computes the same names so role scopes line up exactly.
// The ensureFacilitatorProject flag (default true) guarantees at least one facilitator
// project even when attendeeList contains no facilitator entries.

// Separate attendees by role group for per-role project prefix derivation.
var standardAttendeeEntries = filter(attendeeList, a =>
  a.?role != 'facilitator' && a.?role != 'proctor' && a.?role != 'organizer')
var facilitatorEntries = filter(attendeeList, a => a.?role == 'facilitator')
var proctorEntries = filter(attendeeList, a => a.?role == 'proctor')
var organizerEntries = filter(attendeeList, a => a.?role == 'organizer')

// Standard attendee project names (indexed sequentially within the standard-attendee group only).
var standardAttendeeProjectNames = [
  for (attendee, i) in standardAttendeeEntries: (attendee.?individualProject ?? true)
    ? (attendee.?projectName ?? (useUpnProjectNames
        ? take(toLower(replace(replace(split(attendee.upn, '@')[0], '.', '-'), '_', '-')), 32)
        : '${attendeeProjectPrefix}-${padLeft(string(i + 1), 2, '0')}'))
    : ''
]
var standardAttendeeProjectNamesFiltered = filter(standardAttendeeProjectNames, name => !empty(name))
var standardAttendeeDistinctProjectNames = union(standardAttendeeProjectNamesFiltered, standardAttendeeProjectNamesFiltered)
var countProjectNames = [for i in range(1, attendeeCount): '${attendeeProjectPrefix}-${padLeft(string(i), 2, '0')}']
var effectiveStandardProjectNames = empty(attendeeList)
  ? countProjectNames
  : (!empty(standardAttendeeDistinctProjectNames)
      ? standardAttendeeDistinctProjectNames
      : ['${attendeeProjectPrefix}-01'])

// Role-specific project names (indexed sequentially within each role group).
var facilitatorProjectNamesFromList = [
  for (attendee, i) in facilitatorEntries: (attendee.?projectName ?? (useUpnProjectNames
    ? take(toLower(replace(replace(split(attendee.upn, '@')[0], '.', '-'), '_', '-')), 32)
    : '${facilitatorProjectPrefix}-${padLeft(string(i + 1), 2, '0')}'))
]
var proctorProjectNamesFromList = [
  for (attendee, i) in proctorEntries: (attendee.?projectName ?? (useUpnProjectNames
    ? take(toLower(replace(replace(split(attendee.upn, '@')[0], '.', '-'), '_', '-')), 32)
    : '${proctorProjectPrefix}-${padLeft(string(i + 1), 2, '0')}'))
]
var organizerProjectNamesFromList = [
  for (attendee, i) in organizerEntries: (attendee.?projectName ?? (useUpnProjectNames
    ? take(toLower(replace(replace(split(attendee.upn, '@')[0], '.', '-'), '_', '-')), 32)
    : '${organizerProjectPrefix}-${padLeft(string(i + 1), 2, '0')}'))
]

// Apply ensureFacilitatorProject: always provision at least one facilitator project.
var effectiveFacilitatorProjectNames = !empty(facilitatorProjectNamesFromList)
  ? facilitatorProjectNamesFromList
  : (ensureFacilitatorProject ? ['${facilitatorProjectPrefix}-01'] : [])
var effectiveProctorProjectNames = proctorProjectNamesFromList
var effectiveOrganizerProjectNames = organizerProjectNamesFromList

// Combine all role groups into a single ordered project list.
var allProjectNames = concat(
  effectiveStandardProjectNames,
  effectiveFacilitatorProjectNames,
  effectiveProctorProjectNames,
  effectiveOrganizerProjectNames
)

var attendeeProjects = [
  for name in allProjectNames: {
    name: name
    location: location
    properties: {
      displayName: name
      description: 'Foundry workshop project for ${name}.'
    }
    tags: tags
    roleAssignments: map(
      filter(attendeeProjectRoleEntries, pr => pr.projectName == name),
      pr => pr.roleAssignment
    )
  }
]

var defaultAttendeeProjectName = !empty(effectiveStandardProjectNames) ? effectiveStandardProjectNames[0] : ''

// ---------- ATTENDEE ROLE ASSIGNMENT DATA ----------
// Uses resolvedAttendeeList from AZURE_ATTENDEE_LIST_RESOLVED (set by the preprovision hook).
// Entries with an empty objectId (unresolved UPNs) are excluded from all role assignments.

// Attendees whose UPNs were successfully resolved to Entra object IDs.
var resolvedAttendeesWithIds = filter(resolvedAttendeeList, a => !empty(a.objectId))

// Project-scoped entries (foundry-user → role is assigned on the individual Foundry project).
// Flattened to {projectName, roleAssignment} pairs so attendeeProjects can group by name.
var attendeeProjectRoleEntries = flatten(map(
  filter(resolvedAttendeesWithIds, a =>
    a.role == 'foundry-user' && (a.?individualProject ?? true) && !empty(a.projectName)
  ),
  a => [{
    projectName: a.projectName
    roleAssignment: {
      roleDefinitionIdOrName: foundryRoleCatalog['foundry-user']
      principalId: a.objectId
      principalType: 'User'
    }
  }]
))

// Account-scoped Foundry role assignments (all roles except foundry-user).
var attendeeFoundryAccountRoleAssignments = map(
  filter(resolvedAttendeesWithIds, a => a.role != 'foundry-user'),
  a => {
    roleDefinitionIdOrName: foundryRoleCatalog[a.role]
    principalId: a.objectId
    principalType: 'User'
  }
)

// Azure AI Search role assignments. Each resolved attendee receives every search role paired
// with their Foundry role, flattened into one assignment per role.
var attendeeSearchRoleAssignments = flatten(map(resolvedAttendeesWithIds, a =>
  map(searchRoleCatalog[a.role], roleId => {
    roleDefinitionIdOrName: roleId
    principalId: a.objectId
    principalType: 'User'
  })
))

// Azure Container Registry repository role assignments (all resolved attendees). Required so each
// attendee can build and push their hosted agent image to the shared registry in Module 09, and
// browse the registry catalog/repositories in the portal and CLI. The registry uses ABAC repository
// permissions mode, so the ABAC-enabled 'Container Registry Repository Contributor' role (not legacy
// AcrPush) grants full repository access: catalog read, pull, push, and delete. Per-attendee image
// tags keep pushes logically isolated; the role grants registry-wide access, acceptable for a shared lab.
var attendeeAcrPushRoleAssignments = map(resolvedAttendeesWithIds, a => {
  roleDefinitionIdOrName: 'Container Registry Repository Contributor'
  principalId: a.objectId
  principalType: 'User'
})

// Resource group Reader role assignments (all resolved attendees).
var attendeeResourceGroupReaderRoleAssignments = map(resolvedAttendeesWithIds, a => {
  roleDefinitionIdOrName: 'acdd72a7-3385-48ef-bd42-f606fba81ae7'
  principalId: a.objectId
  principalType: 'User'
})

// Application Insights Log Analytics Reader role assignments (all resolved attendees).
// Required so each attendee can query agent telemetry on the connected Application Insights
// resource and view traces in the Foundry portal Traces view. The Log Analytics Reader role
// GUID is 73c42c96-874c-492b-b04d-ab87d138a893.
// See: https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-setup#prerequisites
var attendeeAppInsightsLogAnalyticsReaderRoleAssignments = map(resolvedAttendeesWithIds, a => {
  roleDefinitionIdOrName: '73c42c96-874c-492b-b04d-ab87d138a893'
  principalId: a.objectId
  principalType: 'User'
})

// Constrained Role Based Access Control Administrator assignments (all resolved attendees) at the
// Foundry account scope. Required for Module 09: each hosted agent receives a per-deploy Microsoft
// Entra agent identity that needs the Foundry User role on the account to invoke models at runtime.
// That identity's principal ID only exists after deployment, so it cannot be pre-assigned in Bicep —
// the attendee's deploy script assigns it. The ABAC condition restricts each attendee to assigning
// ONLY the Foundry User role to ServicePrincipals, enforcing least privilege. The Role Based Access
// Control Administrator role GUID is f58310d9-a9f6-439a-9e8d-f62e7b41a168.
// See: https://learn.microsoft.com/azure/role-based-access-control/delegate-role-assignments-portal
var attendeeAgentIdentityRbacAdminRoleAssignments = map(resolvedAttendeesWithIds, a => {
  roleDefinitionIdOrName: 'f58310d9-a9f6-439a-9e8d-f62e7b41a168'
  principalId: a.objectId
  principalType: 'User'
  description: 'Constrained: assign Foundry User to hosted agent identities only (Module 09).'
  conditionVersion: '2.0'
  condition: '((!(ActionMatches{\'Microsoft.Authorization/roleAssignments/write\'})) OR (@Request[Microsoft.Authorization/roleAssignments:RoleDefinitionId] ForAnyOfAnyValues:GuidEquals {${foundryRoleCatalog['foundry-user']}} AND @Request[Microsoft.Authorization/roleAssignments:PrincipalType] StringEqualsIgnoreCase \'ServicePrincipal\')) AND ((!(ActionMatches{\'Microsoft.Authorization/roleAssignments/delete\'})) OR (@Resource[Microsoft.Authorization/roleAssignments:RoleDefinitionId] ForAnyOfAnyValues:GuidEquals {${foundryRoleCatalog['foundry-user']}}))'
})

// ---------- CAPABILITY HOSTS CONFIGURATION ----------
var aiSearchConnectionName = replace(aiSearchName, '-', '')
var appInsightsConnectionName = replace(applicationInsightsName, '-', '')
var storageConnectionName = replace(storageAccounName, '-', '')
var cosmosDbConnectionName = replace(cosmosDbAccountName, '-', '')
var containerRegistryConnectionName = replace(containerRegistryName, '-', '')

var foundryServiceConnections = concat(
  [
    {
      category: 'AppInsights'
      connectionProperties: {
        authType: 'ApiKey'
        credentials: {
          // Foundry's OpenTelemetry exporter requires the full Application Insights connection
          // string (which carries the regional ingestion endpoint), not the legacy
          // instrumentation key. An instrumentation-key-only connection falls back to the
          // deprecated global endpoint, causing telemetry to arrive unreliably or not at all.
          key: applicationInsights.outputs.connectionString
        }
      }
      name: appInsightsConnectionName
      target: applicationInsights.outputs.resourceId
      isSharedToAll: true
      metadata: {
        ApiType: 'Azure'
        ResourceId: applicationInsights.outputs.resourceId
      }
    }
  ],
  [
    {
      category: 'CognitiveSearch'
      connectionProperties: {
        authType: 'AAD'
      }
      name: aiSearchConnectionName
      target: 'https://${aiSearchName}.search.windows.net'
      isSharedToAll: true
      metadata: {
        displayName: aiSearchName
        type: 'azure_ai_search'
        ApiType: 'Azure'
        ResourceId: aiSearchService.outputs.resourceId
        ApiVersion: '2024-05-01-preview'
        DeploymentApiVersion: '2023-11-01'
      }
    }
  ],
  [
    {
      // Container Registry connection so Foundry hosted agents (Module 09) can pull images
      // from the shared registry using the project managed identity (Container Registry
      // Repository Reader, granted in projectAcrRoleAssignments).
      category: 'ContainerRegistry'
      connectionProperties: {
        authType: 'AAD'
      }
      name: containerRegistryConnectionName
      target: containerRegistry.outputs.loginServer
      isSharedToAll: true
      metadata: {
        ApiType: 'Azure'
        ResourceId: containerRegistry.outputs.resourceId
      }
    }
  ],
  cosmosDbCapabilityHost ? [
    {
      category: 'CosmosDb'
      connectionProperties: {
        authType: 'AAD'
      }
      name: cosmosDbConnectionName
      target: 'https://${cosmosDbAccountName}.documents.azure.com:443/'
      isSharedToAll: true
    }
  ] : [],
  azureStorageAccountCapabilityHost ? [
    {
      category: 'AzureBlob'
      connectionProperties: {
        authType: 'AAD'
      }
      name: storageConnectionName
      target: 'https://${storageAccounName}.blob.${environment().suffixes.storage}/'
      isSharedToAll: true
    }
  ] : []
)

var autoCapabilityHost capabilityHostType = {
  name: 'default'
  capabilityHostKind: 'Agents'
  threadStorageConnectionNames: cosmosDbCapabilityHost ? [cosmosDbConnectionName] : null
  vectorStoreConnectionNames: azureAiSearchCapabilityHost ? [aiSearchConnectionName] : null
  storageConnectionNames: azureStorageAccountCapabilityHost ? [storageConnectionName] : null
}

var hasAutoCapabilityHost = cosmosDbCapabilityHost || azureAiSearchCapabilityHost || azureStorageAccountCapabilityHost
var effectiveCapabilityHosts = concat(foundryCapabilityHosts, hasAutoCapabilityHost ? [autoCapabilityHost] : [])

// Organize resources in a resource group using Azure Verified Module (AVM)
module resourceGroup 'br/public:avm/res/resources/resource-group:0.4.3' = {
  name: 'resource-group-deployment-${deploymentId}'
  params: {
    name: effectiveResourceGroupName
    location: location
    tags: tags
  }
}

// Create the Log Analytics workspace using Azure Verified Module (AVM)
module logAnalyticsWorkspace 'br/public:avm/res/operational-insights/workspace:0.15.1' = {
  name: 'logAnalytics-workspace-deployment-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: logAnalyticsName
    location: location
    tags: tags
  }
}

// Create the Application Insights resource using Azure Verified Module (AVM)
module applicationInsights 'br/public:avm/res/insights/component:0.7.2' = {
  name: 'application-insights-deployment-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: applicationInsightsName
    location: location
    tags: tags
    workspaceResourceId: logAnalyticsWorkspace.outputs.resourceId
  }
}

// Create a Key Vault with public access and RBAC authorization using Azure Verified Module (AVM)
module keyVault 'br/public:avm/res/key-vault/vault:0.13.3' = {
  name: 'keyvault-deployment-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: keyVaultName
    location: location
    tags: tags
    diagnosticSettings: [
      {
        workspaceResourceId: logAnalyticsWorkspace.outputs.resourceId
      }
    ]
    enablePurgeProtection: false
    enableRbacAuthorization: true
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
  }
}

// Create a Storage Account with public access using Azure Verified Module (AVM)
module storageAccount 'br/public:avm/res/storage/storage-account:0.32.1' = {
  name: 'storage-account-deployment-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: storageAccounName
    allowBlobPublicAccess: false
    blobServices: {
      automaticSnapshotPolicyEnabled: false
      containerDeleteRetentionPolicyEnabled: false
      deleteRetentionPolicyEnabled: false
      lastAccessTimeTrackingPolicyEnabled: true
      containers: [
        // This container is used to store information about Lab setup
        {
            name: 'lab-info'
            publicAccess: 'None'
        }
        {
          name: 'retail-products'
          publicAccess: 'None'
        }
      ]
    }
    diagnosticSettings: [
      {
        metricCategories: [
          {
            category: 'AllMetrics'
          }
        ]
        name: sendTologAnalyticsCustomSettingName
        workspaceResourceId: logAnalyticsWorkspace.outputs.resourceId
      }
    ]
    enableHierarchicalNamespace: false
    enableNfsV3: false
    enableSftp: false
    largeFileSharesState: 'Enabled'
    location: location
    managedIdentities: {
      systemAssigned: true
    }
    sasExpirationPeriod: '180.00:00:00'
    skuName: 'Standard_LRS'
    tags: tags
  }
}

// Create a serverless Cosmos DB account with public access using Azure Verified Module (AVM)
module cosmosDbAccount 'br/public:avm/res/document-db/database-account:0.19.0' = {
  name: 'cosmos-db-account-deployment-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: cosmosDbAccountName
    location: location
    tags: tags
    failoverLocations: [
      {
        failoverPriority: 0
        isZoneRedundant: false
        locationName: location
      }
    ]
    enableAutomaticFailover: false
    capabilitiesToAdd: [
      'EnableServerless'
    ]
    databaseAccountOfferType: 'Standard'
    diagnosticSettings: [
      {
        workspaceResourceId: logAnalyticsWorkspace.outputs.resourceId
      }
    ]
    disableKeyBasedMetadataWriteAccess: true
    disableLocalAuthentication: true
    minimumTlsVersion: 'Tls12'
    networkRestrictions: {
      networkAclBypass: 'None'
      publicNetworkAccess: 'Enabled'
    }
    backupStorageRedundancy: 'Local'
    sqlDatabases: [
      {
        // EF Core creates application containers at runtime.
        // The 'leases' container (partition key: /id, 400 RU/s) is required by
        // the Cosmos DB Change Feed Processor for search index sync.
        // It is created automatically by the SearchIndexSyncService on first run.
        name: 'no-containers-specified'
      }
    ]
  }
}

// Create an Azure AI Search service with public access using Azure Verified Module (AVM)
module aiSearchService 'br/public:avm/res/search/search-service:0.12.2' = {
  name: 'ai-search-service-deployment-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: aiSearchName
    location: location
    sku: 'basic'
    semanticSearch: 'standard'
    disableLocalAuth: true
    managedIdentities: {
      systemAssigned: true
    }
    diagnosticSettings: [
      {
        metricCategories: [
          {
            category: 'AllMetrics'
          }
        ]
        name: sendTologAnalyticsCustomSettingName
        workspaceResourceId: logAnalyticsWorkspace.outputs.resourceId
      }
    ]
    publicNetworkAccess: 'Enabled'
    tags: tags
  }
}

// Create an Azure Container Registry with public access using Azure Verified Module (AVM).
// Hosted agents (Module 09) pull their container images from this registry, and attendees push
// their built images here. A single shared registry is used for the whole workshop; per-attendee
// image tags (<image>:<project-name>) keep each attendee's deployment isolated. Public network
// access is enabled so attendees can push from GitHub Codespaces without private networking.
// See: https://learn.microsoft.com/azure/ai-foundry/agents/how-to/deploy-hosted-agents
module containerRegistry 'br/public:avm/res/container-registry/registry:0.12.1' = {
  name: 'container-registry-deployment-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: containerRegistryName
    location: location
    acrSku: containerRegistrySku
    acrAdminUserEnabled: false
    // Hosted agent image pulls require the project managed identity to hold the ABAC-enabled
    // 'Container Registry Repository Reader' role, which is only honored when the registry uses
    // ABAC repository permissions mode. Legacy AcrPull/AcrPush roles are NOT honored in this mode,
    // so all ACR role assignments below use the ABAC-enabled equivalents.
    // See: https://learn.microsoft.com/azure/container-registry/container-registry-rbac-abac-repository-permissions
    roleAssignmentMode: 'AbacRepositoryPermissions'
    diagnosticSettings: [
      {
        metricCategories: [
          {
            category: 'AllMetrics'
          }
        ]
        name: sendTologAnalyticsCustomSettingName
        workspaceResourceId: logAnalyticsWorkspace.outputs.resourceId
      }
    ]
    tags: tags
  }
}

// ---------- AZURE CONTAINER APPS ----------
// Shared Azure Container Apps hosting for workshop services. Enabled by default and gated behind
// azureContainerAppsDeploy. The managed environment is created once and reused by every service
// Container App. The Module 06 Retail Remedy Operations MCP server is published here so the
// cloud-hosted Foundry agent can always reach it over HTTPS when a local dev tunnel is unreachable.
// Future labs can add more services (MCP or otherwise) into the same environment.
//
// Container images are built and pushed by scripts/deploy-mcp-server.py (the shared registry uses
// AbacRepositoryPermissions mode, which azd's image-push path cannot authenticate against). Bicep
// provisions each app with a public placeholder image first so provisioning succeeds before the
// real image exists.
module containerAppsEnvironment './core/host/container-apps-environment.bicep' = if (azureContainerAppsDeploy) {
  name: 'container-apps-environment-deployment-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [
    resourceGroup
  ]
  params: {
    containerAppsEnvironmentName: containerAppsEnvironmentName
    logAnalyticsWorkspaceResourceId: logAnalyticsWorkspace.outputs.resourceId
    location: location
    tags: tags
  }
}

// Module 06 Retail Remedy Operations MCP server, published into the shared environment above.
module mcpServer './core/host/mcp-server.bicep' = if (azureContainerAppsDeploy) {
  name: 'mcp-server-deployment-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [
    resourceGroup
  ]
  params: {
    containerAppName: mcpServerContainerAppName
    #disable-next-line BCP318 // containerAppsEnvironment is gated by the same azureContainerAppsDeploy condition as this module
    containerAppsEnvironmentResourceId: containerAppsEnvironment.outputs.resourceId
    userAssignedIdentityName: mcpServerIdentityName
    containerRegistryLoginServer: containerRegistry.outputs.loginServer
    location: location
    tags: tags
  }
}

// ACR role assignments for the Container Apps services. Each service's managed identity needs the
// ABAC-enabled 'Container Registry Repository Reader' role to pull its image (the shared registry
// uses AbacRepositoryPermissions mode, so legacy AcrPull is not honored). The deploying principal
// needs 'Container Registry Repository Contributor' so scripts/deploy-mcp-server.py can push the
// built image to the shared registry.
module containerAppsAcrRoleAssignments './core/security/role_acr.bicep' = if (azureContainerAppsDeploy) {
  name: 'container-apps-acr-roles-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [
    resourceGroup
  ]
  params: {
    containerRegistryName: containerRegistryName
    roleAssignments: [
      {
        roleDefinitionIdOrName: 'Container Registry Repository Reader'
        principalType: 'ServicePrincipal'
        #disable-next-line BCP318 // mcpServer is gated by the same azureContainerAppsDeploy condition as this module
        principalId: mcpServer.outputs.userAssignedIdentityPrincipalId
      }
      {
        roleDefinitionIdOrName: 'Container Registry Repository Contributor'
        principalType: containerAppsDeployerPrincipalType
        principalId: containerAppsDeployerPrincipalId
      }
    ]
  }
}

// Create the Microsoft Foundry account with public access and per-attendee projects.
// Uses the local cognitive-services module to support Foundry features such as RAI policies.
module aiFoundryAccount './cognitive-services/accounts/main.bicep' = {
  name: 'ai-foundry-account-deployment-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    kind: 'AIServices'
    name: aiFoundryName
    location: location
    customSubDomainName: aiFoundryCustomSubDomainName
    disableLocalAuth: true
    managedIdentities: {
      systemAssigned: true
    }
    sku: 'S0'
    diagnosticSettings: [
      {
        workspaceResourceId: logAnalyticsWorkspace.outputs.resourceId
      }
    ]
    publicNetworkAccess: 'Enabled'
    allowProjectManagement: true
    connections: foundryServiceConnections
    capabilityHosts: effectiveCapabilityHosts
    projects: attendeeProjects
    raiPolicies: [
      {
        name: 'FoundryWorkshopContentPolicy'
        basePolicyName: 'Microsoft.Default'
        mode: 'Blocking'
        contentFilters: [
          {
            name: 'Hate'
            enabled: true
            blocking: true
            severityThreshold: 'Medium'
            source: 'Prompt'
          }
          {
            name: 'Sexual'
            enabled: true
            blocking: true
            severityThreshold: 'Medium'
            source: 'Prompt'
          }
          {
            name: 'Violence'
            enabled: true
            blocking: true
            severityThreshold: 'Medium'
            source: 'Prompt'
          }
          {
            name: 'SelfHarm'
            enabled: true
            blocking: true
            severityThreshold: 'Medium'
            source: 'Prompt'
          }
          {
            name: 'Hate'
            enabled: true
            blocking: true
            severityThreshold: 'Medium'
            source: 'Completion'
          }
          {
            name: 'Sexual'
            enabled: true
            blocking: true
            severityThreshold: 'Medium'
            source: 'Completion'
          }
          {
            name: 'Violence'
            enabled: true
            blocking: true
            severityThreshold: 'Medium'
            source: 'Completion'
          }
          {
            name: 'SelfHarm'
            enabled: true
            blocking: true
            severityThreshold: 'Medium'
            source: 'Completion'
          }
        ]
      }
    ]
    deployments: modelDeployments
  }
}

// ---------- AI SEARCH ROLE ASSIGNMENTS ----------
// Role assignments for the AI Search service to allow Foundry and developer access
var aiSearchRoleAssignmentsArray = [
  // Foundry service managed identity needs access to AI Search
  ...(!empty(aiFoundryAccount.outputs.?systemAssignedMIPrincipalId) ? [
    {
      roleDefinitionIdOrName: 'Search Index Data Contributor'
      principalType: 'ServicePrincipal'
      principalId: aiFoundryAccount.outputs.?systemAssignedMIPrincipalId ?? ''
    }
    {
      roleDefinitionIdOrName: 'Search Index Data Reader'
      principalType: 'ServicePrincipal'
      principalId: aiFoundryAccount.outputs.?systemAssignedMIPrincipalId ?? ''
    }
    {
      roleDefinitionIdOrName: 'Search Service Contributor'
      principalType: 'ServicePrincipal'
      principalId: aiFoundryAccount.outputs.?systemAssignedMIPrincipalId ?? ''
    }
  ] : [])
  // Developer role assignments
  ...(!empty(principalId) ? [
    {
      roleDefinitionIdOrName: 'Search Service Contributor'
      principalType: principalIdType
      principalId: principalId
    }
    {
      roleDefinitionIdOrName: 'Search Index Data Contributor'
      principalType: principalIdType
      principalId: principalId
    }
  ] : [])
  // Per-attendee search role assignments (paired role for each Foundry role).
  ...attendeeSearchRoleAssignments
]

module aiSearchRoleAssignments './core/security/role_aisearch.bicep' = {
  name: 'ai-search-role-assignments-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [
    resourceGroup
    aiSearchService
  ]
  params: {
    azureAiSearchName: aiSearchName
    roleAssignments: aiSearchRoleAssignmentsArray
  }
}

// Per-project managed identity search role assignments for Foundry IQ knowledge base retrieval.
// Each Foundry project's system-assigned managed identity authenticates to the Azure AI Search
// knowledge base MCP endpoint (https://<search>.search.windows.net/knowledgebases/<kb>/mcp) when an
// agent performs Foundry IQ retrieval (Module 07). Without the Search Index Data Reader role, those
// knowledge base tool calls fail with HTTP 403 Forbidden. A module loop is used (rather than a
// variable loop) so the per-project principal IDs — only known after the Foundry account deploys —
// can be referenced in the loop body. The loop count comes from allProjectNames (compile-time), and
// the project array order matches aiFoundryAccount's projects input so IDs are indexed by position.
// See: https://learn.microsoft.com/azure/foundry/agents/how-to/foundry-iq-connect#authentication-and-permissions
module projectSearchRoleAssignments './core/security/role_aisearch.bicep' = [
  for (name, i) in allProjectNames: {
    name: 'project-search-role-${i}-${deploymentId}'
    scope: az.resourceGroup(effectiveResourceGroupName)
    dependsOn: [
      resourceGroup
      aiSearchService
    ]
    params: {
      azureAiSearchName: aiSearchName
      roleAssignments: [
        {
          roleDefinitionIdOrName: 'Search Index Data Reader'
          principalType: 'ServicePrincipal'
          principalId: aiFoundryAccount.outputs.projectSystemAssignedMIPrincipalIds[i]
        }
      ]
    }
  }
]

// Per-project managed identity Container Registry Repository Reader role assignments for hosted
// agent image pulls (Module 09). Each Foundry project's system-assigned managed identity
// authenticates to the shared Container Registry to pull the hosted agent image when the agent
// version is created. The hosted agent deployment path requires the ABAC-enabled 'Container
// Registry Repository Reader' role (not legacy AcrPull); without it, deployment fails with
// image_pull_failed (HTTP 400). This role is only honored because the registry is configured with
// ABAC repository permissions mode (see containerRegistry above). A module loop is used (rather
// than a variable loop) so the per-project principal IDs — only known after the Foundry account
// deploys — can be referenced in the loop body. The loop count comes from allProjectNames
// (compile-time), and the project array order matches aiFoundryAccount's projects input so IDs are
// indexed by position.
// See: https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent#required-permissions
module projectAcrRoleAssignments './core/security/role_acr.bicep' = [
  for (name, i) in allProjectNames: {
    name: 'project-acr-role-${i}-${deploymentId}'
    scope: az.resourceGroup(effectiveResourceGroupName)
    dependsOn: [
      resourceGroup
      containerRegistry
    ]
    params: {
      containerRegistryName: containerRegistryName
      roleAssignments: [
        {
          roleDefinitionIdOrName: 'Container Registry Repository Reader'
          principalType: 'ServicePrincipal'
          principalId: aiFoundryAccount.outputs.projectSystemAssignedMIPrincipalIds[i]
        }
      ]
    }
  }
]

// Per-project managed identity Application Insights Reader role assignments for trace access.
// Each Foundry project's system-assigned managed identity needs the Reader role on the shared
// Application Insights component to read traces in the Foundry portal. Without it, the portal
// reports "Setup incomplete: Assign the Foundry project's managed identity the Reader role on
// Application Insights to access traces." A module loop is used (rather than a variable loop) so
// the per-project principal IDs — only known after the Foundry account deploys — can be referenced
// in the loop body. The loop count comes from allProjectNames (compile-time), and the project array
// order matches aiFoundryAccount's projects input so IDs are indexed by position.
module projectAppInsightsRoleAssignments './core/security/role_appinsights.bicep' = [
  for (name, i) in allProjectNames: {
    name: 'project-appinsights-role-${i}-${deploymentId}'
    scope: az.resourceGroup(effectiveResourceGroupName)
    dependsOn: [
      resourceGroup
      applicationInsights
    ]
    params: {
      applicationInsightsName: applicationInsightsName
      roleAssignments: [
        {
          roleDefinitionIdOrName: 'Reader'
          principalType: 'ServicePrincipal'
          principalId: aiFoundryAccount.outputs.projectSystemAssignedMIPrincipalIds[i]
        }
      ]
    }
  }
]

// Per-attendee Application Insights Log Analytics Reader role assignments for trace querying.
// Each resolved attendee needs the Log Analytics Reader role on the shared Application Insights
// component to query agent telemetry and view traces in the Foundry portal Traces view. Without
// it, attendees see authorization errors when opening traces. Separate from the per-project
// managed identity Reader assignments above (which authorize trace ingestion, not human querying).
// See: https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-setup#prerequisites
module attendeeAppInsightsRoleAssignments './core/security/role_appinsights.bicep' = if (!empty(resolvedAttendeesWithIds)) {
  name: 'attendee-appinsights-roles-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [
    resourceGroup
    applicationInsights
  ]
  params: {
    applicationInsightsName: applicationInsightsName
    roleAssignments: attendeeAppInsightsLogAnalyticsReaderRoleAssignments
  }
}

// Per-attendee Azure Container Registry repository role assignments for hosted agent image pushes.
// Each resolved attendee needs the ABAC-enabled 'Container Registry Repository Contributor' role on
// the shared Container Registry so they can browse the registry catalog and build, push, and manage
// their hosted agent image in Module 09. Without it, the docker push (or az acr login) step fails
// with an authorization error and the registry catalog appears empty in the portal.
// See: https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent#required-permissions
module attendeeAcrRoleAssignments './core/security/role_acr.bicep' = if (!empty(resolvedAttendeesWithIds)) {
  name: 'attendee-acr-roles-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [
    resourceGroup
    containerRegistry
  ]
  params: {
    containerRegistryName: containerRegistryName
    roleAssignments: attendeeAcrPushRoleAssignments
  }
}

// ---------- FOUNDRY ROLE ASSIGNMENTS ----------
// Role assignments for Foundry to allow AI Search and developer access
var foundryRoleAssignmentsArray = [
  // AI Search managed identity needs access to Foundry for vectorization
  ...(!empty(aiSearchService.outputs.?systemAssignedMIPrincipalId) ? [
    {
      roleDefinitionIdOrName: 'Cognitive Services Contributor'
      principalType: 'ServicePrincipal'
      principalId: aiSearchService.outputs.?systemAssignedMIPrincipalId ?? ''
    }
    {
      roleDefinitionIdOrName: 'Cognitive Services OpenAI Contributor'
      principalType: 'ServicePrincipal'
      principalId: aiSearchService.outputs.?systemAssignedMIPrincipalId ?? ''
    }
  ] : [])
  // Developer role assignments
  ...(!empty(principalId) ? [
    {
      roleDefinitionIdOrName: 'Contributor'
      principalType: principalIdType
      principalId: principalId
    }
    {
      roleDefinitionIdOrName: 'Cognitive Services OpenAI Contributor'
      principalType: principalIdType
      principalId: principalId
    }
  ] : [])
  // Per-attendee account-scoped Foundry role assignments (all roles except foundry-user).
  ...attendeeFoundryAccountRoleAssignments
  // Per-attendee constrained RBAC Administrator (Module 09 hosted agent identity grants).
  ...attendeeAgentIdentityRbacAdminRoleAssignments
]

module foundryRoleAssignments './core/security/role_foundry.bicep' = {
  name: 'foundry-role-assignments-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [
    resourceGroup
    aiFoundryAccount
  ]
  params: {
    foundryName: aiFoundryName
    roleAssignments: foundryRoleAssignmentsArray
  }
}

// ---------- COSMOS DB ROLE ASSIGNMENTS ----------
// Assigns Cosmos DB Built-in Data Contributor (data-plane RBAC) to the deploying principal
// for local development access. Uses a separate module to avoid redeploying the Cosmos DB account.
// The built-in Data Contributor role GUID is 00000000-0000-0000-0000-000000000002.
// ---------- ATTENDEE RESOURCE GROUP ROLE ASSIGNMENTS ----------
// Grants the resource group Reader role to every resolved attendee so they can browse
// the workshop resource group in the Azure portal and run health checks.
module attendeeResourceGroupRoles './core/security/role_resourcegroup.bicep' = if (!empty(resolvedAttendeesWithIds)) {
  name: 'attendee-resource-group-roles-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [
    resourceGroup
  ]
  params: {
    roleAssignments: attendeeResourceGroupReaderRoleAssignments
  }
}

module principalCosmosDbRoles './core/security/role_cosmosdb.bicep' = if (!empty(principalId)) {
  name: 'principal-cosmos-db-roles-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [
    resourceGroup
    cosmosDbAccount
  ]
  params: {
    cosmosDbAccountName: cosmosDbAccountName
    sqlRoleAssignments: [
      {
        principalId: principalId
        roleDefinitionId: '00000000-0000-0000-0000-000000000002'
      }
    ]
  }
}

// Alert rule for dead-letter indexing failures.
// Fires when the indexing failure count exceeds 5 in a 5-minute window.
module indexingFailureAlert 'br/public:avm/res/insights/metric-alert:0.4.1' = {
  name: 'indexing-failure-alert-deployment-${deploymentId}'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: 'search-indexing-failure-alert-${environmentName}'
    location: 'global'
    tags: tags
    severity: 2
    evaluationFrequency: 'PT5M'
    windowSize: 'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allof: [
        {
          name: 'IndexingFailureCount'
          metricName: 'DocumentsProcessedCount'
          metricNamespace: 'microsoft.search/searchservices'
          operator: 'GreaterThan'
          threshold: 5
          timeAggregation: 'Total'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    scopes: [
      aiSearchService.outputs.resourceId
    ]
  }
}

@description('The Azure region where resources are deployed.')
output AZURE_LOCATION string = location

@description('The name of the resource group.')
output AZURE_RESOURCE_GROUP string = resourceGroup.outputs.name

@description('The Microsoft Entra tenant ID.')
output AZURE_TENANT_ID string = tenant().tenantId

@description('The name of the Microsoft Foundry account.')
output FOUNDRY_RESOURCE_NAME string = aiFoundryAccount.outputs.name

@description('The custom subdomain name of the Microsoft Foundry account.')
output FOUNDRY_CUSTOM_DOMAIN_NAME string = aiFoundryAccount.outputs.customSubDomainName

@description('The endpoint of the Microsoft Foundry account.')
output FOUNDRY_ENDPOINT string = aiFoundryAccount.outputs.endpoint

@description('The default Foundry project name targeted in single-attendee mode.')
output FOUNDRY_PROJECT_NAME string = defaultAttendeeProjectName

@description('The name of the first facilitator Foundry project. Use this endpoint and project name for data generation.')
output FOUNDRY_FACILITATOR_PROJECT_NAME string = !empty(effectiveFacilitatorProjectNames) ? effectiveFacilitatorProjectNames[0] : ''

@description('The names of all provisioned Foundry projects (standard attendees, facilitators, proctors, and organizers).')
output AZURE_ATTENDEE_PROJECT_NAMES array = [for project in attendeeProjects: project.name]

@description('The name of the Azure AI Search service.')
output AZURE_SEARCH_SERVICE_NAME string = aiSearchService.outputs.name

@description('The name of the storage account.')
output AZURE_STORAGE_ACCOUNT_NAME string = storageAccount.outputs.name

@description('The name of the Azure Container Registry used by hosted agents (Module 09).')
output AZURE_CONTAINER_REGISTRY_NAME string = containerRegistry.outputs.name

@description('The login server endpoint of the Azure Container Registry used by hosted agents (Module 09).')
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer

@description('Whether the shared Azure Container Apps environment and its services were deployed.')
output AZURE_CONTAINER_APPS_DEPLOY_ENABLED bool = azureContainerAppsDeploy

@description('The name of the Module 06 MCP server Container App. Empty when Container Apps deployment is disabled. Consumed by scripts/deploy-mcp-server.py.')
#disable-next-line BCP318 // mcpServer output is only dereferenced when azureContainerAppsDeploy is true
output AZURE_MCP_SERVER_CONTAINER_APP_NAME string = azureContainerAppsDeploy ? mcpServer.outputs.containerAppName : ''

@description('The public HTTPS MCP endpoint (including the /mcp path) for the deployed MCP server. Empty when Container Apps deployment is disabled.')
#disable-next-line BCP318 // mcpServer output is only dereferenced when azureContainerAppsDeploy is true
output MCP_SERVER_URL string = azureContainerAppsDeploy ? mcpServer.outputs.mcpEndpoint : ''
