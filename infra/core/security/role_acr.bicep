metadata name = 'Container Registry Role Assignments'
metadata description = 'Creates role assignments on an Azure Container Registry.'

// TODO: Once this proposal is implemented: https://github.com/azure/bicep/issues/2245
// We can create a generalized version of this resource that can be used any resource
// by passing in the resource as a parameter.

@description('Required. The name of the Azure Container Registry to assign roles to.')
param containerRegistryName string

@description('Optional. Array of role assignments to create.')
param roleAssignments roleAssignmentType[]?

var builtInRoleNames = {
  AcrPull: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  AcrPush: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8311e382-0749-4cb8-b61a-304f252e45ec')
  AcrDelete: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'c2f4ef07-c644-48eb-af81-4b1b4947fb11')
  'Container Registry Repository Reader': subscriptionResourceId(
    'Microsoft.Authorization/roleDefinitions',
    'b93aa761-3e63-49ed-ac28-beffa264f7ac'
  )
  'Container Registry Repository Writer': subscriptionResourceId(
    'Microsoft.Authorization/roleDefinitions',
    '2a1e307c-b015-4ebd-883e-5b7698a07328'
  )
  'Container Registry Repository Contributor': subscriptionResourceId(
    'Microsoft.Authorization/roleDefinitions',
    '2efddaa5-3f1f-4df3-97df-af3f13818f4c'
  )
  Contributor: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b24988ac-6180-42a0-ab88-20f7382dd24c')
  Owner: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8e3af657-a8ff-443c-a75c-2fe8c4bcb635')
  Reader: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'acdd72a7-3385-48ef-bd42-f606fba81ae7')
  'Role Based Access Control Administrator': subscriptionResourceId(
    'Microsoft.Authorization/roleDefinitions',
    'f58310d9-a9f6-439a-9e8d-f62e7b41a168'
  )
  'User Access Administrator': subscriptionResourceId(
    'Microsoft.Authorization/roleDefinitions',
    '18d7d88d-d35e-4fb5-a5c3-7773c20a72d9'
  )
}

var formattedRoleAssignments = [
  for (roleAssignment, index) in (roleAssignments ?? []): union(roleAssignment, {
    roleDefinitionId: builtInRoleNames[?roleAssignment.roleDefinitionIdOrName] ?? (contains(
        roleAssignment.roleDefinitionIdOrName,
        '/providers/Microsoft.Authorization/roleDefinitions/'
      )
      ? roleAssignment.roleDefinitionIdOrName
      : subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleAssignment.roleDefinitionIdOrName))
  })
]

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' existing = {
  name: containerRegistryName
}

resource containerRegistry_roleAssignments 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for (roleAssignment, index) in (formattedRoleAssignments ?? []): {
    name: roleAssignment.?name ?? guid(
      containerRegistry.id,
      roleAssignment.principalId,
      roleAssignment.roleDefinitionId
    )
    properties: {
      roleDefinitionId: roleAssignment.roleDefinitionId
      principalId: roleAssignment.principalId
      description: roleAssignment.?description
      principalType: roleAssignment.?principalType
      condition: roleAssignment.?condition
      conditionVersion: !empty(roleAssignment.?condition) ? (roleAssignment.?conditionVersion ?? '2.0') : null
      delegatedManagedIdentityResourceId: roleAssignment.?delegatedManagedIdentityResourceId
    }
    scope: containerRegistry
  }
]

@description('The resource IDs of the role assignments.')
output roleAssignmentResourceIds array = [
  for (roleAssignment, index) in (formattedRoleAssignments ?? []): containerRegistry_roleAssignments[index].id
]

@description('The names of the role assignments.')
output roleAssignmentNames array = [
  for (roleAssignment, index) in (formattedRoleAssignments ?? []): containerRegistry_roleAssignments[index].name
]

// =============== //
//   Definitions   //
// =============== //

@export()
type roleAssignmentType = {
  @description('Optional. The name (as GUID) of the role assignment. If not provided, a GUID will be generated.')
  name: string?

  @description('Required. The role to assign. You can provide either the display name of the role definition, the role definition GUID, or its fully qualified ID in the following format: \'/providers/Microsoft.Authorization/roleDefinitions/c2f4ef07-c644-48eb-af81-4b1b4947fb11\'.')
  roleDefinitionIdOrName: string

  @description('Required. The principal ID of the principal (user/group/identity) to assign the role to.')
  principalId: string

  @description('Optional. The principal type of the assigned principal ID.')
  principalType: ('ServicePrincipal' | 'Group' | 'User' | 'ForeignGroup' | 'Device')?

  @description('Optional. The description of the role assignment.')
  description: string?

  @description('Optional. The conditions on the role assignment. This limits the resources it can be assigned to. e.g.: @Resource[Microsoft.Storage/storageAccounts/blobServices/containers:ContainerName] StringEqualsIgnoreCase "foo_storage_container".')
  condition: string?

  @description('Optional. Version of the condition.')
  conditionVersion: '2.0'?

  @description('Optional. The Resource Id of the delegated managed identity resource.')
  delegatedManagedIdentityResourceId: string?
}
