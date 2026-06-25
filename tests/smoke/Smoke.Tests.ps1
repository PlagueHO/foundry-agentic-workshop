[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string] $SubscriptionId,

    [Parameter(Mandatory)]
    [string] $EnvironmentName,

    [Parameter(Mandatory)]
    [string] $AttendeeProjectPrefix,

    [Parameter(Mandatory)]
    [int] $AttendeeCount,

    [Parameter()]
    [string] $AttendeeList = '',

    [Parameter(Mandatory)]
    [string] $AttendeeDefaultRole,

    [Parameter()]
    [switch] $AiSearchEnabled,

    [Parameter()]
    [switch] $CosmosDbEnabled,

    [Parameter()]
    [switch] $StorageAccountEnabled,

    [Parameter()]
    [string] $FacilitatorProjectPrefix = 'facilitator',

    [Parameter()]
    [string] $ProctorProjectPrefix = 'proctor',

    [Parameter()]
    [string] $OrganizerProjectPrefix = 'organizer',

    [Parameter()]
    [bool] $EnsureFacilitatorProject = $true,

    [Parameter()]
    [bool] $UseUpnProjectNames = $true
)

# Derives a Foundry project name from a UPN local part, mirroring Bicep's useUpnProjectNames logic.
# When UseUpn is $false, falls back to the padded-index format used by countProjectNames.
function Get-AttendeeProjectName {
    param(
        [string] $Upn,
        [string] $Prefix,
        [int]    $Index,
        [bool]   $UseUpn
    )
    if ($UseUpn) {
        $local   = ($Upn -split '@')[0]
        $derived = $local.ToLower() -replace '\.', '-' -replace '_', '-'
        return $derived.Substring(0, [Math]::Min($derived.Length, 32))
    }
    return '{0}-{1:D2}' -f $Prefix, ($Index + 1)
}

BeforeDiscovery {
    # Build project names and attendee test cases, mirroring the variable derivation in
    # infra/main.bicep. This block runs during Pester discovery and makes data available
    # to -ForEach on Describe blocks.
    #
    # Attendees are split into four role groups (standard, facilitator, proctor, organizer).
    # Each group is indexed independently, matching Bicep's per-group loop index (i + 1).
    if ($AttendeeList -ne '') {
        $parsedAttendees = $AttendeeList | ConvertFrom-Json

        if ($parsedAttendees.Count -gt 0) {
            # Per-role-group index counters. These advance only when an entry belongs to
            # that group, exactly replicating Bicep's "for (attendee, i) in <group>" index.
            $stdGrpIdx = 0
            $facGrpIdx = 0
            $prcGrpIdx = 0
            $orgGrpIdx = 0

            $standardNames    = [System.Collections.Generic.List[string]]::new()
            $facilitatorNames = [System.Collections.Generic.List[string]]::new()
            $proctorNames     = [System.Collections.Generic.List[string]]::new()
            $organizerNames   = [System.Collections.Generic.List[string]]::new()

            foreach ($attendee in $parsedAttendees) {
                $roleKey = if ($attendee.PSObject.Properties.Name.Contains('role') -and $attendee.role) {
                    $attendee.role
                } else {
                    $AttendeeDefaultRole
                }

                switch ($roleKey) {
                    'facilitator' {
                        $name = if ($attendee.PSObject.Properties.Name.Contains('projectName') -and $attendee.projectName) {
                            $attendee.projectName
                        } else {
                            Get-AttendeeProjectName -Upn $attendee.upn -Prefix $FacilitatorProjectPrefix -Index $facGrpIdx -UseUpn $UseUpnProjectNames
                        }
                        $facilitatorNames.Add($name)
                        $facGrpIdx++
                    }
                    'proctor' {
                        $name = if ($attendee.PSObject.Properties.Name.Contains('projectName') -and $attendee.projectName) {
                            $attendee.projectName
                        } else {
                            Get-AttendeeProjectName -Upn $attendee.upn -Prefix $ProctorProjectPrefix -Index $prcGrpIdx -UseUpn $UseUpnProjectNames
                        }
                        $proctorNames.Add($name)
                        $prcGrpIdx++
                    }
                    'organizer' {
                        $name = if ($attendee.PSObject.Properties.Name.Contains('projectName') -and $attendee.projectName) {
                            $attendee.projectName
                        } else {
                            Get-AttendeeProjectName -Upn $attendee.upn -Prefix $OrganizerProjectPrefix -Index $orgGrpIdx -UseUpn $UseUpnProjectNames
                        }
                        $organizerNames.Add($name)
                        $orgGrpIdx++
                    }
                    default {
                        # Standard group - covers foundry-user, foundry-project-manager,
                        # foundry-account-owner, foundry-owner, and any attendee with no role.
                        $includesProject = -not $attendee.PSObject.Properties.Name.Contains('individualProject') -or
                            $attendee.individualProject -ne $false
                        if ($includesProject) {
                            $name = if ($attendee.PSObject.Properties.Name.Contains('projectName') -and $attendee.projectName) {
                                $attendee.projectName
                            } else {
                                Get-AttendeeProjectName -Upn $attendee.upn -Prefix $AttendeeProjectPrefix -Index $stdGrpIdx -UseUpn $UseUpnProjectNames
                            }
                            if (-not $standardNames.Contains($name)) {
                                $standardNames.Add($name)
                            }
                        }
                        # The standard group counter advances for every standard entry,
                        # including individualProject:false, mirroring Bicep's loop index i.
                        $stdGrpIdx++
                    }
                }
            }

            # Apply EnsureFacilitatorProject: guarantee at least one facilitator project when no
            # facilitator entries appear in the list (mirrors infra/main.bicep ensureFacilitatorProject).
            $effectiveFacilitatorNames = if ($facilitatorNames.Count -gt 0) {
                $facilitatorNames.ToArray()
            } elseif ($EnsureFacilitatorProject) {
                @('{0}-01' -f $FacilitatorProjectPrefix)
            } else {
                @()
            }

            # Fall back to <prefix>-01 when the standard group produced no projects.
            $effectiveStandardNames = if ($standardNames.Count -gt 0) {
                $standardNames.ToArray()
            } else {
                @('{0}-01' -f $AttendeeProjectPrefix)
            }

            # Concatenate in the same order as Bicep: standard, facilitator, proctor, organizer.
            $script:ProjectNames = @(
                $effectiveStandardNames
                $effectiveFacilitatorNames
                $proctorNames.ToArray()
                $organizerNames.ToArray()
            )
        } else {
            $script:ProjectNames = 1..$AttendeeCount | ForEach-Object { '{0}-{1:D2}' -f $AttendeeProjectPrefix, $_ }
        }
    } else {
        $script:ProjectNames = 1..$AttendeeCount | ForEach-Object { '{0}-{1:D2}' -f $AttendeeProjectPrefix, $_ }
    }

    # Build attendee test cases for role assignment validation.
    # Project name derivation uses per-role-group counters so each attendee maps to the
    # exact project that Bicep and the postprovision hook created for them.
    $script:AttendeeTestCases = if ($AttendeeList -ne '') {
        $parsedAttendees = $AttendeeList | ConvertFrom-Json

        $stdIdx = 0
        $facIdx = 0
        $prcIdx = 0
        $orgIdx = 0

        $testCases = [System.Collections.Generic.List[hashtable]]::new()

        foreach ($attendee in $parsedAttendees) {
            $roleKey = if ($attendee.PSObject.Properties.Name.Contains('role') -and $attendee.role) {
                $attendee.role
            } else {
                $AttendeeDefaultRole
            }

            $projectName = if ($attendee.PSObject.Properties.Name.Contains('projectName') -and $attendee.projectName) {
                $attendee.projectName
            } elseif ($roleKey -eq 'facilitator') {
                $name = Get-AttendeeProjectName -Upn $attendee.upn -Prefix $FacilitatorProjectPrefix -Index $facIdx -UseUpn $UseUpnProjectNames
                $facIdx++
                $name
            } elseif ($roleKey -eq 'proctor') {
                $name = Get-AttendeeProjectName -Upn $attendee.upn -Prefix $ProctorProjectPrefix -Index $prcIdx -UseUpn $UseUpnProjectNames
                $prcIdx++
                $name
            } elseif ($roleKey -eq 'organizer') {
                $name = Get-AttendeeProjectName -Upn $attendee.upn -Prefix $OrganizerProjectPrefix -Index $orgIdx -UseUpn $UseUpnProjectNames
                $orgIdx++
                $name
            } else {
                $includesProject = -not $attendee.PSObject.Properties.Name.Contains('individualProject') -or
                    $attendee.individualProject -ne $false
                $name = if ($includesProject) {
                    Get-AttendeeProjectName -Upn $attendee.upn -Prefix $AttendeeProjectPrefix -Index $stdIdx -UseUpn $UseUpnProjectNames
                } else {
                    '{0}-01' -f $AttendeeProjectPrefix
                }
                $stdIdx++
                $name
            }

            $testCases.Add(@{
                Upn         = $attendee.upn
                RoleKey     = $roleKey
                ProjectName = $projectName
            })
        }

        $testCases.ToArray()
    } else {
        @()
    }
}

BeforeAll {
    # Foundry RBAC role definition IDs and their assignment scope type.
    # Staff roles (facilitator, proctor, organizer) all resolve to Foundry Owner at account scope.
    $script:RoleDefinitions = @{
        'foundry-user'            = @{ Id = '53ca6127-db72-4b80-b1b0-d745d6d5456d'; Scope = 'project' }
        'foundry-project-manager' = @{ Id = 'eadc314b-1a2d-4efa-be10-5d325db5065e'; Scope = 'account' }
        'foundry-account-owner'   = @{ Id = 'e47c6f54-e4a2-4754-9501-8e0985b135e1'; Scope = 'account' }
        'foundry-owner'           = @{ Id = 'c883944f-8b7b-4483-af10-35834be79c4a'; Scope = 'account' }
        'facilitator'             = @{ Id = 'c883944f-8b7b-4483-af10-35834be79c4a'; Scope = 'account' }
        'proctor'                 = @{ Id = 'c883944f-8b7b-4483-af10-35834be79c4a'; Scope = 'account' }
        'organizer'               = @{ Id = 'c883944f-8b7b-4483-af10-35834be79c4a'; Scope = 'account' }
    }

    # Derive resource names using the same logic as infra/main.bicep.
    $script:ResourceGroup      = "rg-$EnvironmentName"
    $script:FoundryAccountName = "aif-$EnvironmentName"

    $kvRaw = ('kv-' + $EnvironmentName) -replace '-', ''
    $script:KeyVaultName = if ($kvRaw.Length -gt 24) { $kvRaw.Substring(0, 24) } else { $kvRaw }

    $script:CosmosDbAccountName = ('cdb' + $EnvironmentName) -replace '-', ''
    $script:AiSearchName        = "aisrch-$EnvironmentName"

    $storageRaw = ('st' + $EnvironmentName) -replace '-', ''
    $script:StorageAccountName  = if ($storageRaw.Length -gt 24) { $storageRaw.Substring(0, 24) } else { $storageRaw }

    $crRaw = (('cr' + $EnvironmentName) -replace '-', '').ToLower()
    $script:ContainerRegistryName = if ($crRaw.Length -gt 50) { $crRaw.Substring(0, 50) } else { $crRaw }

    $script:AccountResourceId = "/subscriptions/$SubscriptionId/resourceGroups/$script:ResourceGroup" +
        "/providers/Microsoft.CognitiveServices/accounts/$script:FoundryAccountName"

    $script:ResourceGroupScope = "/subscriptions/$SubscriptionId/resourceGroups/$script:ResourceGroup"
    $script:SearchResourceId   = "/subscriptions/$SubscriptionId/resourceGroups/$script:ResourceGroup" +
        "/providers/Microsoft.Search/searchServices/$script:AiSearchName"
    $script:SearchBaseUrl      = "https://$($script:AiSearchName).search.windows.net"
    $script:RgReaderRoleId     = 'acdd72a7-3385-48ef-bd42-f606fba81ae7'

    # Search role IDs assigned to each attendee by the postprovision hook.
    $script:SearchRoleDefinitions = @{
        'foundry-user'            = @{ Id = '8ebe5a00-799e-43f5-93ac-243d3dce84a7'; Name = 'Search Index Data Contributor' }
        'foundry-project-manager' = @{ Id = '8ebe5a00-799e-43f5-93ac-243d3dce84a7'; Name = 'Search Index Data Contributor' }
        'foundry-account-owner'   = @{ Id = '8ebe5a00-799e-43f5-93ac-243d3dce84a7'; Name = 'Search Index Data Contributor' }
        'foundry-owner'           = @{ Id = '8ebe5a00-799e-43f5-93ac-243d3dce84a7'; Name = 'Search Index Data Contributor' }
        'facilitator'             = @{ Id = 'b24988ac-6180-42a0-ab88-20f7382dd24c'; Name = 'Contributor' }
        'proctor'                 = @{ Id = 'b24988ac-6180-42a0-ab88-20f7382dd24c'; Name = 'Contributor' }
        'organizer'               = @{ Id = 'b24988ac-6180-42a0-ab88-20f7382dd24c'; Name = 'Contributor' }
    }
}

Describe 'Resource Group' {
    It 'Exists and is in Succeeded provisioning state' {
        $rawOutput = az group show --name $script:ResourceGroup --output json 2>&1
        $LASTEXITCODE | Should -Be 0 -Because "Resource group '$script:ResourceGroup' must exist"
        ($rawOutput | ConvertFrom-Json).properties.provisioningState | Should -Be 'Succeeded'
    }
}

Describe 'Foundry Account' {
    BeforeAll {
        $rawOutput = az cognitiveservices account show `
            --name $script:FoundryAccountName `
            --resource-group $script:ResourceGroup `
            --output json 2>&1
        $script:FoundryAccount = if ($LASTEXITCODE -eq 0) { $rawOutput | ConvertFrom-Json } else { $null }
    }

    It 'Exists' {
        $script:FoundryAccount | Should -Not -BeNullOrEmpty -Because "Foundry account '$script:FoundryAccountName' must exist"
    }

    It 'Is in Succeeded provisioning state' {
        $script:FoundryAccount | Should -Not -BeNullOrEmpty
        $script:FoundryAccount.properties.provisioningState | Should -Be 'Succeeded'
    }
}

Describe 'Foundry Projects' {
    It 'Project <_> exists and is in Succeeded state' -ForEach $script:ProjectNames {
        $resourceId = "$script:AccountResourceId/projects/$_"
        $rawOutput = az resource show --ids $resourceId --output json 2>&1
        $LASTEXITCODE | Should -Be 0 `
            -Because "Foundry project '$_' must exist under account '$script:FoundryAccountName'"
        ($rawOutput | ConvertFrom-Json).properties.provisioningState | Should -Be 'Succeeded'
    }
}

Describe 'Model Deployments' {
    It 'Chat model deployment exists and is in Succeeded state' {
        $resourceId = "$script:AccountResourceId/deployments/chat"
        $rawOutput = az resource show --ids $resourceId --output json 2>&1
        $LASTEXITCODE | Should -Be 0 `
            -Because "Model deployment 'chat' must exist on account '$script:FoundryAccountName'"
        ($rawOutput | ConvertFrom-Json).properties.provisioningState | Should -Be 'Succeeded'
    }

    It 'Embedding model deployment exists and is in Succeeded state' {
        $resourceId = "$script:AccountResourceId/deployments/embedding"
        $rawOutput = az resource show --ids $resourceId --output json 2>&1
        $LASTEXITCODE | Should -Be 0 `
            -Because "Model deployment 'embedding' must exist on account '$script:FoundryAccountName'"
        ($rawOutput | ConvertFrom-Json).properties.provisioningState | Should -Be 'Succeeded'
    }
}

Describe 'Attendee Role Assignments' -Skip:($script:AttendeeTestCases.Count -eq 0) {
    It 'Attendee <Upn> has role <RoleKey> assigned at correct scope' -ForEach $script:AttendeeTestCases {
        $roleDef = $script:RoleDefinitions[$RoleKey]
        $roleDef | Should -Not -BeNullOrEmpty -Because "Role key '$RoleKey' must be a known Foundry role"

        $objectId = (az ad user show --id $Upn --query id --output tsv 2>&1).Trim()
        $LASTEXITCODE | Should -Be 0 -Because "UPN '$Upn' must be resolvable in the tenant"
        $objectId | Should -Not -BeNullOrEmpty -Because "Resolved object ID for '$Upn' must not be empty"

        $scope = if ($roleDef.Scope -eq 'project') {
            "$script:AccountResourceId/projects/$ProjectName"
        } else {
            $script:AccountResourceId
        }

        $rawOutput = az role assignment list `
            --scope $scope `
            --assignee $objectId `
            --role $roleDef.Id `
            --output json 2>&1
        $LASTEXITCODE | Should -Be 0
        ($rawOutput | ConvertFrom-Json).Count | Should -BeGreaterThan 0 `
            -Because "Attendee '$Upn' must have role '$RoleKey' assigned at scope '$scope'"
    }

    It 'Attendee <Upn> has Reader role on resource group' -ForEach $script:AttendeeTestCases {
        $objectId = (az ad user show --id $Upn --query id --output tsv 2>&1).Trim()
        $LASTEXITCODE | Should -Be 0 -Because "UPN '$Upn' must be resolvable in the tenant"
        $objectId | Should -Not -BeNullOrEmpty -Because "Resolved object ID for '$Upn' must not be empty"

        $rawOutput = az role assignment list `
            --scope $script:ResourceGroupScope `
            --assignee $objectId `
            --role $script:RgReaderRoleId `
            --output json 2>&1
        $LASTEXITCODE | Should -Be 0
        ($rawOutput | ConvertFrom-Json).Count | Should -BeGreaterThan 0 `
            -Because "Attendee '$Upn' must have Reader role on resource group '$script:ResourceGroup'"
    }

    It 'Attendee <Upn> has correct Search role assigned' -Skip:(-not $AiSearchEnabled) -ForEach $script:AttendeeTestCases {
        $searchRoleDef = $script:SearchRoleDefinitions[$RoleKey]
        $searchRoleDef | Should -Not -BeNullOrEmpty -Because "Role key '$RoleKey' must have a Search role mapping"

        $objectId = (az ad user show --id $Upn --query id --output tsv 2>&1).Trim()
        $LASTEXITCODE | Should -Be 0 -Because "UPN '$Upn' must be resolvable in the tenant"
        $objectId | Should -Not -BeNullOrEmpty -Because "Resolved object ID for '$Upn' must not be empty"

        $rawOutput = az role assignment list `
            --scope $script:SearchResourceId `
            --assignee $objectId `
            --role $searchRoleDef.Id `
            --output json 2>&1
        $LASTEXITCODE | Should -Be 0
        ($rawOutput | ConvertFrom-Json).Count | Should -BeGreaterThan 0 `
            -Because "Attendee '$Upn' must have '$($searchRoleDef.Name)' on Search service '$script:AiSearchName'"
    }
}

Describe 'Key Vault' {
    It 'Exists and is in Succeeded provisioning state' {
        $rawOutput = az keyvault show `
            --name $script:KeyVaultName `
            --resource-group $script:ResourceGroup `
            --output json 2>&1
        $LASTEXITCODE | Should -Be 0 -Because "Key Vault '$script:KeyVaultName' must exist"
        ($rawOutput | ConvertFrom-Json).properties.provisioningState | Should -Be 'Succeeded'
    }
}

Describe 'Container Registry' {
    It 'Exists and is in Succeeded provisioning state' {
        $rawOutput = az acr show `
            --name $script:ContainerRegistryName `
            --resource-group $script:ResourceGroup `
            --output json 2>&1
        $LASTEXITCODE | Should -Be 0 -Because "Container Registry '$script:ContainerRegistryName' must exist"
        ($rawOutput | ConvertFrom-Json).provisioningState | Should -Be 'Succeeded'
    }
}

Describe 'AI Search' -Skip:(-not $AiSearchEnabled) {
    It 'Exists and is in Succeeded provisioning state' {
        $rawOutput = az search service show `
            --name $script:AiSearchName `
            --resource-group $script:ResourceGroup `
            --output json 2>&1
        $LASTEXITCODE | Should -Be 0 -Because "AI Search service '$script:AiSearchName' must exist"
        ($rawOutput | ConvertFrom-Json).provisioningState | Should -Be 'Succeeded'
    }

    It 'Index <_> exists' -ForEach @('retail-products', 'retail-policies') {
        $rawOutput = az rest --method get `
            --url "$($script:SearchBaseUrl)/indexes/${_}?api-version=2024-07-01" `
            --resource 'https://search.azure.com' `
            --output json 2>&1
        $LASTEXITCODE | Should -Be 0 -Because "AI Search index '$_' must exist in '$script:AiSearchName'"
    }

    It 'Index <_> contains seeded documents' -ForEach @('retail-products', 'retail-policies') {
        $rawOutput = az rest --method get `
            --url "$($script:SearchBaseUrl)/indexes/${_}/docs/`$count?api-version=2024-07-01" `
            --resource 'https://search.azure.com' 2>&1
        $LASTEXITCODE | Should -Be 0
        [int]$rawOutput | Should -BeGreaterThan 0 `
            -Because "AI Search index '$_' must contain seeded documents"
    }
}

Describe 'Cosmos DB' -Skip:(-not $CosmosDbEnabled) {
    It 'Exists and is in Succeeded provisioning state' {
        $rawOutput = az cosmosdb show `
            --name $script:CosmosDbAccountName `
            --resource-group $script:ResourceGroup `
            --output json 2>&1
        $LASTEXITCODE | Should -Be 0 -Because "Cosmos DB account '$script:CosmosDbAccountName' must exist"
        ($rawOutput | ConvertFrom-Json).provisioningState | Should -BeIn @('Succeeded', 'Online')
    }
}

Describe 'Storage Account' -Skip:(-not $StorageAccountEnabled) {
    It 'Exists and is in Succeeded provisioning state' {
        $rawOutput = az storage account show `
            --name $script:StorageAccountName `
            --resource-group $script:ResourceGroup `
            --output json 2>&1
        $LASTEXITCODE | Should -Be 0 -Because "Storage account '$script:StorageAccountName' must exist"
        ($rawOutput | ConvertFrom-Json).provisioningState | Should -Be 'Succeeded'
    }
}
