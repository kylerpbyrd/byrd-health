<#
.SYNOPSIS
    Build Byrd Health Docker image for Home Assistant runtime validation.
.DESCRIPTION
    Builds the Docker image from the repository root and tags it as
    byrd-health:rc1. This image can be used for local HA testing.
.PARAMETER Tag
    Docker image tag (default: rc1)
.PARAMETER NoCache
    Force a full rebuild without cache
.EXAMPLE
    .\tools\build-ha.ps1
    .\tools\build-ha.ps1 -Tag "beta" -NoCache
#>

param(
    [string]$Tag = "rc1",
    [switch]$NoCache
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$ImageName = "byrd-health:$Tag"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Byrd Health — Docker Build" -ForegroundColor Cyan
Write-Host " Image: $ImageName" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Push-Location $RepoRoot
try {
    $args = @("build", "-t", $ImageName)
    if ($NoCache) { $args += "--no-cache" }
    $args += "."

    Write-Host "[1/1] Building Docker image..." -ForegroundColor Yellow
    docker @args

    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Docker build failed with exit code $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }

    Write-Host ""
    Write-Host "Build complete: $ImageName" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps for HA runtime validation:" -ForegroundColor White
    Write-Host "  1. Load this image on your HA host" -ForegroundColor Gray
    Write-Host "  2. Install the add-on via HA Supervisor" -ForegroundColor Gray
    Write-Host "  3. Follow docs/releases/RC1_VALIDATION_CHECKLIST.md" -ForegroundColor Gray
} finally {
    Pop-Location
}
