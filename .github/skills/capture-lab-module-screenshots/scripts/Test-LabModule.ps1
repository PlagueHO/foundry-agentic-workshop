<#
.SYNOPSIS
    Validate a workshop lab module README: confirm every referenced screenshot
    exists on disk and run markdownlint over the README.

.DESCRIPTION
    Parses the given lab README for Markdown image references, resolves each path
    relative to the README's directory, and reports any that are missing. Then
    runs markdownlint-cli2 (via pnpm) on the README. Exits non-zero if any
    screenshot is missing or markdownlint reports errors, so it can gate a lab
    update.

.PARAMETER ReadmePath
    Path to the lab module README.md (absolute, or relative to the current
    working directory).

.PARAMETER SkipLint
    Skip the markdownlint step (only check screenshot existence).

.EXAMPLE
    ./Test-LabModule.ps1 -ReadmePath "labs/introduction-foundry-agent-service/06-mcp-tools/README.md"

.NOTES
    Requires PowerShell 7+. markdownlint step requires pnpm + markdownlint-cli2
    available in the repository (skipped automatically if pnpm is not found).
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string] $ReadmePath,

    [Parameter()]
    [switch] $SkipLint
)

$ErrorActionPreference = 'Stop'

$readmeItem = Get-Item -LiteralPath $ReadmePath -ErrorAction SilentlyContinue
if ($null -eq $readmeItem) {
    Write-Error "README not found: $ReadmePath"
    exit 2
}

$readmeDirectory = Split-Path -Path $readmeItem.FullName -Parent
$content = Get-Content -LiteralPath $readmeItem.FullName -Raw

# Match Markdown image references: ![alt](path)
$imageMatches = [regex]::Matches($content, '!\[[^\]]*\]\(([^)]+)\)')
$missing = [System.Collections.Generic.List[string]]::new()
$checked = 0

foreach ($match in $imageMatches) {
    $reference = $match.Groups[1].Value.Trim()

    # Ignore remote images and in-page anchors
    if ($reference -match '^(https?:)?//' -or $reference.StartsWith('#')) {
        continue
    }

    # Strip any title or fragment after the path
    $pathPart = ($reference -split '\s+')[0]
    $pathPart = ($pathPart -split '#')[0]

    $resolved = Join-Path -Path $readmeDirectory -ChildPath $pathPart
    $checked++

    if (-not (Test-Path -LiteralPath $resolved)) {
        $missing.Add($pathPart)
    }
}

Write-Output "Checked $checked local image reference(s) in $($readmeItem.Name)."

if ($missing.Count -gt 0) {
    Write-Output ''
    Write-Output "MISSING screenshot file(s):"
    foreach ($entry in $missing) {
        Write-Output "  - $entry"
    }
}
else {
    Write-Output 'All referenced screenshots exist on disk.'
}

$lintFailed = $false
if (-not $SkipLint) {
    $pnpm = Get-Command -Name 'pnpm' -ErrorAction SilentlyContinue
    if ($null -eq $pnpm) {
        Write-Warning 'pnpm not found; skipping markdownlint. Re-run with the lint toolchain installed.'
    }
    else {
        Write-Output ''
        Write-Output 'Running markdownlint-cli2...'
        & pnpm exec markdownlint-cli2 $readmeItem.FullName
        if ($LASTEXITCODE -ne 0) {
            $lintFailed = $true
        }
    }
}

if ($missing.Count -gt 0 -or $lintFailed) {
    exit 1
}

Write-Output ''
Write-Output 'Lab module validation passed.'
exit 0
