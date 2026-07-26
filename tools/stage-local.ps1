<#
.SYNOPSIS
    Validate and optionally build the Byrd Health add-on for local HA Supervisor installation.
.DESCRIPTION
    Validates that the required add-on files exist in the repository/byrd_health_fertility/
    directory (which is now committed directly to the repo).  No longer generates files --
    the canonical copies live in the repository tree.
.PARAMETER Build
    Also build the Docker image after validation
.PARAMETER Tag
    Docker image tag when using -Build (default: rc1)
.EXAMPLE
    .\tools\stage-local.ps1
    .\tools\stage-local.ps1 -Build -Tag rc1
.NOTES
    After staging, add the repository directory to HA Supervisor:
      Settings -> Add-ons -> Add-on Store -> ... -> Repositories
      Add: /path/to/byrd-health/repository
#>

param(
    [switch]$Build,
    [string]$Tag = "rc1"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$StageDir = Join-Path $RepoRoot "repository\byrd_health_fertility"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Byrd Health -- Validate Add-on Files" -ForegroundColor Cyan
Write-Host " Target: $StageDir" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$errors = @()
$files = @("config.yaml", "Dockerfile", "run.sh")

foreach ($file in $files) {
    $path = Join-Path $StageDir $file
    if (Test-Path $path) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $file" -ForegroundColor Red
        $errors += $file
    }
}

if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "Validation FAILED: $($errors.Count) file(s) missing." -ForegroundColor Red
    Write-Host "The add-on files should be committed to $StageDir" -ForegroundColor Red
    Write-Host "Run 'git status repository/' to check." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "All add-on files present." -ForegroundColor Green
Write-Host ""

if (Test-Path (Join-Path $RepoRoot "icon.png")) {
    Write-Host "  [OK] icon.png" -ForegroundColor Green
} else {
    Write-Host "  [!] icon.png not found (optional)" -ForegroundColor DarkYellow
}
if (Test-Path (Join-Path $RepoRoot "logo.png")) {
    Write-Host "  [OK] logo.png" -ForegroundColor Green
} else {
    Write-Host "  [!] logo.png not found (optional)" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "To use this add-on in Home Assistant:" -ForegroundColor White
Write-Host "  1. Copy the 'repository/' directory to your HA host" -ForegroundColor Gray
Write-Host "  2. In HA: Settings -> Add-ons -> Add-on Store -> ... -> Repositories" -ForegroundColor Gray
Write-Host "  3. Add the full path to the 'repository/' directory" -ForegroundColor Gray
Write-Host "  4. The 'Byrd Health -- Fertility Tracker' add-on should appear" -ForegroundColor Gray
Write-Host ""

if ($Build) {
    Write-Host "Building Docker image..." -ForegroundColor Yellow
    Push-Location $RepoRoot
    try {
        docker build -t "byrd-health:$Tag" .
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Build successful: byrd-health:$Tag" -ForegroundColor Green
        }
    } finally {
        Pop-Location
    }
}
