using './bot-service.bicep'

param botServiceName = readEnvironmentVariable('BOT_SERVICE_NAME', 'acl-remedy-advisor-cea')
param displayName = 'ACL Remedy Advisor'
param appClientId = readEnvironmentVariable('BOT_APP_CLIENT_ID', '')
param tenantId = readEnvironmentVariable('BOT_TENANT_ID', '')
param messagingEndpoint = readEnvironmentVariable('BOT_MESSAGING_ENDPOINT', '')
param location = readEnvironmentVariable('BOT_LOCATION', 'australiaeast')
param skuName = 'F0'
param tags = {
  workshop: 'foundry-agentic-workshop'
  module: '13-custom-engine-agent'
}
