<#
.SYNOPSIS
    Deploys the Entra Private Access — Quick Access proof-of-concept.

.DESCRIPTION
    This script automates the following POC steps:
      1. Verify Global Secure Access activation
      2. Enable the Private Access traffic forwarding profile
      3. Check connector health
      4. Create a dedicated connector group (POC-ConnectorGroup)
      5. Assign the first active connector to the new group
      6. Create the pilot security group (POC-PrivateAccess-Pilot)
      7. Create the break-glass exclusion group (CA-Exclusion-BreakGlass)
      8. Assign the pilot group to the Quick Access enterprise app
      9. Create a Conditional Access policy in report-only mode

    All operations are idempotent — running the script multiple times does not produce duplicates.
    No resources are deleted (no Remove-* / DELETE calls).

.PARAMETER TenantId
    The directory (tenant) ID. Defaults to the current Graph context tenant.

.PARAMETER PilotGroupName
    Name of the pilot security group. Default: POC-PrivateAccess-Pilot

.PARAMETER ConnectorGroupName
    Name of the connector group. Default: POC-ConnectorGroup

.PARAMETER ConnectorGroupRegion
    Azure region for the connector group. Valid: nam, eur, aus, asi, ind. Default: nam

.PARAMETER BreakGlassGroupName
    Name of the break-glass exclusion group. Default: CA-Exclusion-BreakGlass

.PARAMETER TestUserObjectIds
    Array of user object IDs to add to the pilot group.

.NOTES
    Requires Microsoft.Graph.Authentication module.
    Uses Invoke-MgGraphRequest for all Graph calls.

    Required Graph scopes:
      NetworkAccess.ReadWrite.All, Application.ReadWrite.All,
      Group.ReadWrite.All, Policy.ReadWrite.ConditionalAccess,
      Policy.Read.All, Directory.ReadWrite.All
#>

[CmdletBinding(SupportsShouldProcess)]
param (
    [Parameter()]
    [string]$TenantId,

    [Parameter()]
    [string]$PilotGroupName = "POC-PrivateAccess-Pilot",

    [Parameter()]
    [string]$ConnectorGroupName = "POC-ConnectorGroup",

    [Parameter()]
    [ValidateSet("nam", "eur", "aus", "asi", "ind")]
    [string]$ConnectorGroupRegion = "nam",

    [Parameter()]
    [string]$BreakGlassGroupName = "CA-Exclusion-BreakGlass",

    [Parameter()]
    [string[]]$TestUserObjectIds = @()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ─────────────────────────────────────────────
# Helper: Connect to Microsoft Graph
# ─────────────────────────────────────────────
function Connect-IfNeeded {
    $ctx = Get-MgContext -ErrorAction SilentlyContinue
    if (-not $ctx) {
        $scopes = @(
            "NetworkAccess.ReadWrite.All",
            "Application.ReadWrite.All",
            "Group.ReadWrite.All",
            "Policy.ReadWrite.ConditionalAccess",
            "Policy.Read.All",
            "Directory.ReadWrite.All"
        )
        $connectParams = @{ Scopes = $scopes }
        if ($TenantId) { $connectParams["TenantId"] = $TenantId }
        Connect-MgGraph @connectParams
    } else {
        Write-Host "[Auth] Already connected as $($ctx.Account) to tenant $($ctx.TenantId)" -ForegroundColor Cyan
    }
}

# ─────────────────────────────────────────────
# Helper: Find or create a security group
# ─────────────────────────────────────────────
function Get-OrCreateSecurityGroup {
    [CmdletBinding(SupportsShouldProcess)]
    param (
        [string]$DisplayName,
        [string]$Description,
        [string]$MailNickname
    )

    $filter = "displayName eq '$DisplayName'"
    $existing = (Invoke-MgGraphRequest -Method GET `
        -Uri "https://graph.microsoft.com/v1.0/groups?`$filter=$filter&`$select=id,displayName").value

    if ($existing.Count -gt 0) {
        Write-Host "  [Skip] Group '$DisplayName' already exists (id: $($existing[0].id))." -ForegroundColor Yellow
        return $existing[0]
    }

    if ($PSCmdlet.ShouldProcess($DisplayName, "Create security group")) {
        $body = @{
            displayName     = $DisplayName
            description     = $Description
            securityEnabled = $true
            mailEnabled     = $false
            mailNickname    = $MailNickname
            groupTypes      = @()
        } | ConvertTo-Json -Depth 5

        $newGroup = Invoke-MgGraphRequest -Method POST `
            -Uri "https://graph.microsoft.com/v1.0/groups" `
            -Body $body -ContentType "application/json"
        Write-Host "  [Created] Group '$DisplayName' (id: $($newGroup.id))." -ForegroundColor Green
        return $newGroup
    }
}

# ─────────────────────────────────────────────
# Helper: Add members to a group (idempotent)
# ─────────────────────────────────────────────
function Add-GroupMembers {
    [CmdletBinding(SupportsShouldProcess)]
    param (
        [string]$GroupId,
        [string]$GroupName,
        [string[]]$MemberIds
    )

    foreach ($memberId in $MemberIds) {
        # Check existing membership
        $members = (Invoke-MgGraphRequest -Method GET `
            -Uri "https://graph.microsoft.com/v1.0/groups/$GroupId/members?`$select=id").value
        $alreadyMember = $members | Where-Object { $_.id -eq $memberId }

        if ($alreadyMember) {
            Write-Host "  [Skip] User $memberId is already a member of '$GroupName'." -ForegroundColor Yellow
            continue
        }

        if ($PSCmdlet.ShouldProcess("User $memberId", "Add to group '$GroupName'")) {
            $body = @{
                "@odata.id" = "https://graph.microsoft.com/v1.0/directoryObjects/$memberId"
            } | ConvertTo-Json

            Invoke-MgGraphRequest -Method POST `
                -Uri "https://graph.microsoft.com/v1.0/groups/$GroupId/members/`$ref" `
                -Body $body -ContentType "application/json"
            Write-Host "  [Added] User $memberId to group '$GroupName'." -ForegroundColor Green
        }
    }
}

# ═════════════════════════════════════════════
# MAIN EXECUTION
# ═════════════════════════════════════════════

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Entra Private Access — Quick Access POC" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Connect-IfNeeded

# ─────────────────────────────────────────────
# Step 1: Verify Global Secure Access activation
# ─────────────────────────────────────────────
Write-Host "[Step 1/9] Verifying Global Secure Access activation..." -ForegroundColor Cyan
try {
    $gsaSettings = Invoke-MgGraphRequest -Method GET `
        -Uri "https://graph.microsoft.com/beta/networkAccess/settings"
    if ($gsaSettings.isEnabled) {
        Write-Host "  [OK] Global Secure Access is activated." -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] Global Secure Access is NOT activated." -ForegroundColor Red
        Write-Host "  Action: Activate GSA in the Entra admin center > Global Secure Access > Get started." -ForegroundColor Red
        return
    }
} catch {
    Write-Host "  [ERROR] Unable to query GSA settings. Ensure the tenant has an Entra Private Access license." -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    return
}

# ─────────────────────────────────────────────
# Step 2: Enable Private Access traffic profile
# ─────────────────────────────────────────────
Write-Host "[Step 2/9] Enabling Private Access traffic forwarding profile..." -ForegroundColor Cyan
$profiles = (Invoke-MgGraphRequest -Method GET `
    -Uri "https://graph.microsoft.com/beta/networkAccess/forwardingProfiles").value
$privateProfile = $profiles | Where-Object { $_.trafficForwardingType -eq "private" }

if (-not $privateProfile) {
    Write-Host "  [ERROR] Private Access forwarding profile not found. GSA may not be fully provisioned." -ForegroundColor Red
    return
}

if ($privateProfile.state -eq "enabled") {
    Write-Host "  [Skip] Private Access profile is already enabled." -ForegroundColor Yellow
} else {
    if ($PSCmdlet.ShouldProcess("Private Access traffic profile", "Enable")) {
        $patchBody = @{ state = "enabled" } | ConvertTo-Json
        Invoke-MgGraphRequest -Method PATCH `
            -Uri "https://graph.microsoft.com/beta/networkAccess/forwardingProfiles/$($privateProfile.id)" `
            -Body $patchBody -ContentType "application/json"
        Write-Host "  [Enabled] Private Access traffic forwarding profile." -ForegroundColor Green
    }
}

# ─────────────────────────────────────────────
# Step 3: Check connector health
# ─────────────────────────────────────────────
Write-Host "[Step 3/9] Checking connector health..." -ForegroundColor Cyan
$connectors = (Invoke-MgGraphRequest -Method GET `
    -Uri "https://graph.microsoft.com/beta/onPremisesPublishingProfiles/applicationProxy/connectors").value

if ($connectors.Count -eq 0) {
    Write-Host "  [WARNING] No connectors found. Install a connector on a Windows Server with network access to your private resources." -ForegroundColor Red
    Write-Host "  The script will continue but Quick Access will not function without a connector." -ForegroundColor Red
} else {
    $activeConnectors = $connectors | Where-Object { $_.status -eq "active" }
    Write-Host "  Total connectors: $($connectors.Count) | Active: $($activeConnectors.Count)" -ForegroundColor Cyan
    foreach ($c in $connectors) {
        $color = if ($c.status -eq "active") { "Green" } else { "Red" }
        Write-Host "    $($c.machineName) | Status: $($c.status) | IP: $($c.externalIp)" -ForegroundColor $color
    }
}

# ─────────────────────────────────────────────
# Step 4: Create connector group
# ─────────────────────────────────────────────
Write-Host "[Step 4/9] Creating connector group '$ConnectorGroupName'..." -ForegroundColor Cyan

$cgFilter = "name eq '$ConnectorGroupName'"
$existingCG = (Invoke-MgGraphRequest -Method GET `
    -Uri "https://graph.microsoft.com/beta/onPremisesPublishingProfiles/applicationProxy/connectorGroups?`$filter=$cgFilter").value

if ($existingCG.Count -gt 0) {
    $connectorGroup = $existingCG[0]
    Write-Host "  [Skip] Connector group '$ConnectorGroupName' already exists (id: $($connectorGroup.id))." -ForegroundColor Yellow
} else {
    if ($PSCmdlet.ShouldProcess($ConnectorGroupName, "Create connector group")) {
        $cgBody = @{
            name   = $ConnectorGroupName
            region = $ConnectorGroupRegion
        } | ConvertTo-Json

        $connectorGroup = Invoke-MgGraphRequest -Method POST `
            -Uri "https://graph.microsoft.com/beta/onPremisesPublishingProfiles/applicationProxy/connectorGroups" `
            -Body $cgBody -ContentType "application/json"
        Write-Host "  [Created] Connector group '$ConnectorGroupName' (id: $($connectorGroup.id))." -ForegroundColor Green
    }
}

# ─────────────────────────────────────────────
# Step 5: Assign first active connector to group
# ─────────────────────────────────────────────
Write-Host "[Step 5/9] Assigning connector to group '$ConnectorGroupName'..." -ForegroundColor Cyan

if ($connectors.Count -gt 0 -and $connectorGroup) {
    $firstActive = $connectors | Where-Object { $_.status -eq "active" } | Select-Object -First 1
    if ($firstActive) {
        # Check if already in the group
        $groupMembers = (Invoke-MgGraphRequest -Method GET `
            -Uri "https://graph.microsoft.com/beta/onPremisesPublishingProfiles/applicationProxy/connectorGroups/$($connectorGroup.id)/members").value
        $alreadyAssigned = $groupMembers | Where-Object { $_.id -eq $firstActive.id }

        if ($alreadyAssigned) {
            Write-Host "  [Skip] Connector '$($firstActive.machineName)' is already in '$ConnectorGroupName'." -ForegroundColor Yellow
        } else {
            if ($PSCmdlet.ShouldProcess("Connector '$($firstActive.machineName)'", "Assign to '$ConnectorGroupName'")) {
                $assignBody = @{
                    "@odata.id" = "https://graph.microsoft.com/beta/onPremisesPublishingProfiles/applicationProxy/connectors/$($firstActive.id)"
                } | ConvertTo-Json

                Invoke-MgGraphRequest -Method POST `
                    -Uri "https://graph.microsoft.com/beta/onPremisesPublishingProfiles/applicationProxy/connectorGroups/$($connectorGroup.id)/members/`$ref" `
                    -Body $assignBody -ContentType "application/json"
                Write-Host "  [Assigned] Connector '$($firstActive.machineName)' to '$ConnectorGroupName'." -ForegroundColor Green
            }
        }
    } else {
        Write-Host "  [WARNING] No active connectors available to assign." -ForegroundColor Red
    }
} else {
    Write-Host "  [Skip] No connectors or connector group to work with." -ForegroundColor Yellow
}

# ─────────────────────────────────────────────
# Step 6: Create pilot security group
# ─────────────────────────────────────────────
Write-Host "[Step 6/9] Creating pilot group '$PilotGroupName'..." -ForegroundColor Cyan
$pilotGroup = Get-OrCreateSecurityGroup `
    -DisplayName $PilotGroupName `
    -Description "Pilot group for Entra Private Access Quick Access POC" `
    -MailNickname ($PilotGroupName -replace '[^a-zA-Z0-9]', '')

if ($TestUserObjectIds.Count -gt 0 -and $pilotGroup) {
    Write-Host "  Adding $($TestUserObjectIds.Count) test user(s) to '$PilotGroupName'..." -ForegroundColor Cyan
    Add-GroupMembers -GroupId $pilotGroup.id -GroupName $PilotGroupName -MemberIds $TestUserObjectIds
}

# ─────────────────────────────────────────────
# Step 7: Create break-glass exclusion group
# ─────────────────────────────────────────────
Write-Host "[Step 7/9] Creating break-glass group '$BreakGlassGroupName'..." -ForegroundColor Cyan
$bgGroup = Get-OrCreateSecurityGroup `
    -DisplayName $BreakGlassGroupName `
    -Description "Emergency access accounts excluded from all CA policies" `
    -MailNickname ($BreakGlassGroupName -replace '[^a-zA-Z0-9]', '')

# ─────────────────────────────────────────────
# Step 8: Assign pilot group to Quick Access app
# ─────────────────────────────────────────────
Write-Host "[Step 8/9] Assigning pilot group to Quick Access enterprise app..." -ForegroundColor Cyan

# Find the Quick Access service principal
$spResult = (Invoke-MgGraphRequest -Method GET `
    -Uri "https://graph.microsoft.com/v1.0/servicePrincipals?`$filter=displayName eq 'Quick Access'&`$select=id,displayName,appRoles").value

if ($spResult.Count -eq 0) {
    Write-Host "  [WARNING] Quick Access enterprise app not found. It is created when you configure Quick Access in the portal." -ForegroundColor Red
    Write-Host "  Complete Step 6 in the POC guide (configure application segments) before running this step." -ForegroundColor Red
} else {
    $qaSP = $spResult[0]
    Write-Host "  Found Quick Access app: $($qaSP.displayName) (id: $($qaSP.id))" -ForegroundColor Cyan

    if ($pilotGroup) {
        # Check existing assignments
        $assignments = (Invoke-MgGraphRequest -Method GET `
            -Uri "https://graph.microsoft.com/v1.0/servicePrincipals/$($qaSP.id)/appRoleAssignments?`$select=id,principalId,principalDisplayName").value
        $alreadyAssigned = $assignments | Where-Object { $_.principalId -eq $pilotGroup.id }

        if ($alreadyAssigned) {
            Write-Host "  [Skip] '$PilotGroupName' is already assigned to Quick Access." -ForegroundColor Yellow
        } else {
            if ($PSCmdlet.ShouldProcess("Quick Access app", "Assign group '$PilotGroupName'")) {
                $roleBody = @{
                    principalId   = $pilotGroup.id
                    principalType = "Group"
                    appRoleId     = "00000000-0000-0000-0000-000000000000"
                    resourceId    = $qaSP.id
                } | ConvertTo-Json

                Invoke-MgGraphRequest -Method POST `
                    -Uri "https://graph.microsoft.com/v1.0/servicePrincipals/$($qaSP.id)/appRoleAssignments" `
                    -Body $roleBody -ContentType "application/json"
                Write-Host "  [Assigned] '$PilotGroupName' to Quick Access enterprise app." -ForegroundColor Green
            }
        }
    }
}

# ─────────────────────────────────────────────
# Step 9: Create Conditional Access policy
# ─────────────────────────────────────────────
Write-Host "[Step 9/9] Creating Conditional Access policy..." -ForegroundColor Cyan

$caPolicyName = "POC-PrivateAccess-RequireMFA"
$existingCA = (Invoke-MgGraphRequest -Method GET `
    -Uri "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies?`$filter=displayName eq '$caPolicyName'").value

if ($existingCA.Count -gt 0) {
    Write-Host "  [Skip] CA policy '$caPolicyName' already exists (id: $($existingCA[0].id))." -ForegroundColor Yellow
} else {
    if (-not $pilotGroup -or -not $bgGroup) {
        Write-Host "  [ERROR] Pilot or break-glass group not available. Cannot create CA policy." -ForegroundColor Red
    } else {
        # Determine target app ID
        $targetAppId = if ($spResult.Count -gt 0) { $qaSP.id } else { "All" }

        if ($PSCmdlet.ShouldProcess($caPolicyName, "Create CA policy (report-only)")) {
            $caBody = @{
                displayName = $caPolicyName
                state       = "enabledForReportingButNotEnforced"
                conditions  = @{
                    users = @{
                        includeGroups = @($pilotGroup.id)
                        excludeGroups = @($bgGroup.id)
                    }
                    applications = @{
                        includeApplications = @($targetAppId)
                    }
                }
                grantControls = @{
                    operator        = "OR"
                    builtInControls = @("mfa")
                }
            } | ConvertTo-Json -Depth 10

            $newCA = Invoke-MgGraphRequest -Method POST `
                -Uri "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies" `
                -Body $caBody -ContentType "application/json"
            Write-Host "  [Created] CA policy '$caPolicyName' (id: $($newCA.id))." -ForegroundColor Green
            Write-Host "  State: REPORT-ONLY — validate in Conditional Access Insights before enabling." -ForegroundColor Yellow
        }
    }
}

# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Deployment Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GSA Activation:       Verified" -ForegroundColor Green
Write-Host "  Private Access:       Enabled" -ForegroundColor Green
Write-Host "  Connector Group:      $ConnectorGroupName" -ForegroundColor Green
Write-Host "  Pilot Group:          $PilotGroupName" -ForegroundColor Green
Write-Host "  Break-Glass Group:    $BreakGlassGroupName" -ForegroundColor Green
Write-Host "  CA Policy:            POC-PrivateAccess-RequireMFA (report-only)" -ForegroundColor Green
Write-Host ""
Write-Host "  MANUAL STEPS REMAINING:" -ForegroundColor Yellow
Write-Host "    1. Install a connector on a Windows Server (if not done)" -ForegroundColor Yellow
Write-Host "    2. Configure Quick Access application segments in the portal" -ForegroundColor Yellow
Write-Host "    3. Assign Quick Access to connector group '$ConnectorGroupName'" -ForegroundColor Yellow
Write-Host "    4. Install GSA Client on test devices" -ForegroundColor Yellow
Write-Host "    5. Test connectivity to private resources" -ForegroundColor Yellow
Write-Host "    6. Review CA policy in Insights, then switch to enforced" -ForegroundColor Yellow
Write-Host "`nDone." -ForegroundColor Green
