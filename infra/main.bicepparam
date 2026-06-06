using './main.bicep'

// Environment Configuration
param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'azdtemp')
param location = readEnvironmentVariable('AZURE_LOCATION', 'EastUS2')

// Resource Group Configuration
param resourceGroupName = readEnvironmentVariable('AZURE_RESOURCE_GROUP', '')

// Per-attendee Foundry project configuration
param attendeeCount = int(readEnvironmentVariable('AZURE_ATTENDEE_COUNT', '1'))
param attendeeProjectPrefix = readEnvironmentVariable('AZURE_ATTENDEE_PROJECT_PREFIX', 'attendee')

// Capability host flags (off by default)
param azureAiSearchCapabilityHost = toLower(readEnvironmentVariable('AZURE_AI_SEARCH_CAPABILITY_HOST', 'false')) == 'true'
param cosmosDbCapabilityHost = toLower(readEnvironmentVariable('AZURE_COSMOS_DB_CAPABILITY_HOST', 'false')) == 'true'
param azureStorageAccountCapabilityHost = toLower(readEnvironmentVariable('AZURE_STORAGE_ACCOUNT_CAPABILITY_HOST', 'false')) == 'true'
