using './main.bicep'

// Environment Configuration
param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'azdtemp')
param location = readEnvironmentVariable('AZURE_LOCATION', 'EastUS2')

// Resource Group Configuration
param resourceGroupName = readEnvironmentVariable('AZURE_RESOURCE_GROUP', '')

// Principal running the deployment - populated automatically by azd from the signed-in identity.
// Used to assign Search Index Data Contributor and Search Service Contributor to the organizer
// so the postprovision seeding scripts can write to AI Search without a manual role grant.
param principalId = readEnvironmentVariable('AZURE_PRINCIPAL_ID', '')
param principalIdType = readEnvironmentVariable('AZURE_PRINCIPAL_TYPE', 'User')

// Per-attendee Foundry project configuration
param attendeeCount = int(readEnvironmentVariable('AZURE_ATTENDEE_COUNT', '1'))
param attendeeProjectPrefix = readEnvironmentVariable('AZURE_ATTENDEE_PROJECT_PREFIX', 'attendee')

// Structured attendee list (single source of truth for project creation).
// When provided, it drives the set of per-attendee projects; otherwise attendeeCount is used.
param attendeeList = json(readEnvironmentVariable('AZURE_ATTENDEE_LIST', '[]'))

// Resolved attendee list written by the preprovision hook (scripts/prepare-attendee-roles.py).
// Contains Entra object IDs and precomputed project names. When not set (e.g. azd provision
// called without hooks), this is empty and Bicep creates no per-attendee role assignments.
param resolvedAttendeeList = json(readEnvironmentVariable('AZURE_ATTENDEE_LIST_RESOLVED', '[]'))

// Role-specific project prefix configuration
param facilitatorProjectPrefix = readEnvironmentVariable('AZURE_FACILITATOR_PROJECT_PREFIX', 'facilitator')
param proctorProjectPrefix = readEnvironmentVariable('AZURE_PROCTOR_PROJECT_PREFIX', 'proctor')
param organizerProjectPrefix = readEnvironmentVariable('AZURE_ORGANIZER_PROJECT_PREFIX', 'organizer')
param ensureFacilitatorProject = toLower(readEnvironmentVariable('AZURE_ENSURE_FACILITATOR_PROJECT', 'true')) != 'false'
param useUpnProjectNames = toLower(readEnvironmentVariable('AZURE_USE_UPN_PROJECT_NAMES', 'true')) != 'false'
param attendeeDefaultRole = readEnvironmentVariable('AZURE_ATTENDEE_DEFAULT_ROLE', 'foundry-user')

// Shared Container Registry SKU for hosted agents (Module 09). Basic is sufficient for the workshop.
param containerRegistrySku = readEnvironmentVariable('AZURE_CONTAINER_REGISTRY_SKU', 'Basic')

// Capability host flags (off by default)
param azureAiSearchCapabilityHost = toLower(readEnvironmentVariable('AZURE_AI_SEARCH_CAPABILITY_HOST', 'false')) == 'true'
param cosmosDbCapabilityHost = toLower(readEnvironmentVariable('AZURE_COSMOS_DB_CAPABILITY_HOST', 'false')) == 'true'
param azureStorageAccountCapabilityHost = toLower(readEnvironmentVariable('AZURE_STORAGE_ACCOUNT_CAPABILITY_HOST', 'false')) == 'true'

// Azure Container Apps deployment. When true (the default), deploys the shared Container Apps
// environment and the services that run in it, such as the Module 06 MCP server.
param azureContainerAppsDeploy = toLower(readEnvironmentVariable('AZURE_CONTAINER_APPS_DEPLOY', 'true')) == 'true'
