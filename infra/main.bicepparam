using './main.bicep'

// Environment Configuration
param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'azdtemp')
param location = readEnvironmentVariable('AZURE_LOCATION', 'EastUS2')

// Resource Group Configuration
param resourceGroupName = readEnvironmentVariable('AZURE_RESOURCE_GROUP', '')

// Per-attendee Foundry project configuration
param attendeeCount = int(readEnvironmentVariable('AZURE_ATTENDEE_COUNT', '1'))
param attendeeProjectPrefix = readEnvironmentVariable('AZURE_ATTENDEE_PROJECT_PREFIX', 'attendee')

// Structured attendee list (single source of truth for project creation and role assignment).
// When provided, it drives the set of per-attendee projects; otherwise attendeeCount is used.
param attendeeList = json(readEnvironmentVariable('AZURE_ATTENDEE_LIST', '[]'))

// Role-specific project prefix configuration
param facilitatorProjectPrefix = readEnvironmentVariable('AZURE_FACILITATOR_PROJECT_PREFIX', 'facilitator')
param proctorProjectPrefix = readEnvironmentVariable('AZURE_PROCTOR_PROJECT_PREFIX', 'proctor')
param organizerProjectPrefix = readEnvironmentVariable('AZURE_ORGANIZER_PROJECT_PREFIX', 'organizer')
param ensureFacilitatorProject = toLower(readEnvironmentVariable('AZURE_ENSURE_FACILITATOR_PROJECT', 'true')) != 'false'
param useUpnProjectNames = toLower(readEnvironmentVariable('AZURE_USE_UPN_PROJECT_NAMES', 'true')) != 'false'

// Capability host flags (off by default)
param azureAiSearchCapabilityHost = toLower(readEnvironmentVariable('AZURE_AI_SEARCH_CAPABILITY_HOST', 'false')) == 'true'
param cosmosDbCapabilityHost = toLower(readEnvironmentVariable('AZURE_COSMOS_DB_CAPABILITY_HOST', 'false')) == 'true'
param azureStorageAccountCapabilityHost = toLower(readEnvironmentVariable('AZURE_STORAGE_ACCOUNT_CAPABILITY_HOST', 'false')) == 'true'
