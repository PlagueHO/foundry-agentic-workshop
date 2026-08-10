metadata name = 'Cosmos DB Management Role Assignments'
metadata description = 'Creates management-plane role assignments on an Azure Cosmos DB account.'

@description('Required. The name of the existing Cosmos DB account.')
param cosmosDbAccountName string

@description('Required. Array of role assignments to create.')
param roleAssignments roleAssignmentType[]

resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2024-11-15' existing = {
  name: cosmosDbAccountName
}

resource cosmosDbAccountRoleAssignments 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for roleAssignment in roleAssignments: {
    name: guid(cosmosDbAccount.id, roleAssignment.principalId, roleAssignment.roleDefinitionId)
    properties: {
      roleDefinitionId: roleAssignment.roleDefinitionId
      principalId: roleAssignment.principalId
      principalType: roleAssignment.principalType
    }
    scope: cosmosDbAccount
  }
]

@export()
type roleAssignmentType = {
  @description('Required. The role definition ID to assign.')
  roleDefinitionId: string

  @description('Required. The principal ID to assign the role to.')
  principalId: string

  @description('Required. The principal type.')
  principalType: 'ServicePrincipal'
}
