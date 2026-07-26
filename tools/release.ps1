<#
.SYNOPSIS
    Package Byrd Health for release distribution.
.DESCRIPTION
    Creates a release archive containing the add-on configuration files
    and build instructions. For a full Docker image release, use build-ha.ps1
    and push to a container registry.
.PARAMETER Version
    Version tag for the release (default: reads from CHANGELOG.md)
.EXAMPLE
    .\tools\release.ps1 -Version "2.0.0"
.NOTES
    This produces a distributable archive. Docker images must be
    built and pushed separately.
#>

param(
    [string]$Version = "2.0.0"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$ReleaseDir = Join-Path $RepoRoot "dist\release-$Version"
$ArchiveName = "byrd-health-$Version.tar.gz"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Byrd Health — Release Packaging" -ForegroundColor Cyan
Write-Host " Version: $Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Clean and create release directory
if (Test-Path $ReleaseDir) { Remove-Item -Recurse -Force $ReleaseDir }
New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null

Write-Host "[1/6] Running tests..." -ForegroundColor Yellow

# Python tests
Push-Location $RepoRoot
try {
    python -m pytest packages/ -x -q 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Python tests failed. Fix before releasing." -ForegroundColor Red
        exit 1
    }
    Write-Host "  Python: PASS" -ForegroundColor Green
} finally {
    Pop-Location
}

# Frontend tests
Push-Location (Join-Path $RepoRoot "frontend")
try {
    npm test -- --run 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Frontend tests failed. Fix before releasing." -ForegroundColor Red
        exit 1
    }
    Write-Host "  Frontend: PASS" -ForegroundColor Green
} finally {
    Pop-Location
}

# Copy add-on files
Write-Host "[2/6] Copying add-on configuration..." -ForegroundColor Yellow
Copy-Item -Path (Join-Path $RepoRoot "config.yaml") -Destination $ReleaseDir -Force
Copy-Item -Path (Join-Path $RepoRoot "Dockerfile") -Destination $ReleaseDir -Force
Copy-Item -Path (Join-Path $RepoRoot "run.sh") -Destination $ReleaseDir -Force

# Copy repository metadata
Copy-Item -Path (Join-Path $RepoRoot "repository\repository.yaml") -Destination $ReleaseDir -Force

# Copy documentation
Write-Host "[3/6] Copying documentation..." -ForegroundColor Yellow
$docsDir = Join-Path $ReleaseDir "docs"
New-Item -ItemType Directory -Path $docsDir -Force | Out-Null
Copy-Item -Path (Join-Path $RepoRoot "README.md") -Destination $ReleaseDir -Force
Copy-Item -Path (Join-Path $RepoRoot "CHANGELOG.md") -Destination $ReleaseDir -Force
Copy-Item -Path (Join-Path $RepoRoot "LICENSE") -Destination $ReleaseDir -Force -ErrorAction SilentlyContinue

# Copy release validation docs
$releaseDocs = Join-Path $RepoRoot "docs\releases"
if (Test-Path $releaseDocs) {
    $targetDocs = Join-Path $docsDir "releases"
    New-Item -ItemType Directory -Path $targetDocs -Force | Out-Null
    Copy-Item -Path "$releaseDocs\*" -Destination $targetDocs -Force
}

# Create install guide
Write-Host "[4/6] Generating install guide..." -ForegroundColor Yellow
$installGuide = @"
# Byrd Health — Fertility Tracker v$Version
## Installation Guide

### Option 1: Home Assistant Add-on (Recommended)

1. Add this repository to Home Assistant Supervisor:
   - Settings → Add-ons → Add-on Store → ⋮ → Repositories
   - Add the repository URL

2. Find "Byrd Health — Fertility Tracker" in the add-on store
3. Click Install
4. Configure options (temperature unit, notifications, etc.)
5. Start the add-on
6. Click "Open Web UI" or find "Fertility Tracker" in the sidebar

### Option 2: Docker (Standalone)

```bash
docker build -t byrd-health:latest .
docker run -d \
  --name byrd-health \
  -p 8000:8000 \
  -v byrd-data:/data \
  -e BYRD_SECRET_KEY="$(openssl rand -hex 32)" \
  byrd-health:latest
```

Then visit http://localhost:8000

### Default Configuration

| Option | Default | Description |
|--------|---------|-------------|
| temp_unit | F | Temperature unit (F or C) |
| ha_sensor_entity | "" | Optional HA entity for automated temp reading |
| poll_interval_minutes | 15 | Poll interval for sensor |
| notify_temp_reminder | true | Daily temperature reminder |
| notify_temp_reminder_time | "07:00" | Reminder time (HH:MM) |
| notify_fertile_window | true | Fertile window notification |
| notify_period_prediction | true | Period prediction notification |
| notify_ovulation_detected | true | Ovulation detection notification |

### Data Privacy

All health data is stored locally. No data leaves your device.
The database is encrypted at rest with AES-256-GCM.
Your data belongs to you.

### Support

- GitHub: https://github.com/kylerpbyrd/byrd-health
- Documentation: https://github.com/kylerpbyrd/byrd-health/tree/main/docs

---

*Byrd Health — Privacy-first health intelligence*
"@

Set-Content -Path (Join-Path $ReleaseDir "INSTALL.md") -Value $installGuide
Write-Host "  -> INSTALL.md" -ForegroundColor Gray

# Verify required files
Write-Host "[5/6] Verifying release integrity..." -ForegroundColor Yellow
$requiredFiles = @(
    "config.yaml",
    "Dockerfile",
    "run.sh",
    "repository.yaml",
    "README.md",
    "CHANGELOG.md",
    "INSTALL.md"
)

$missing = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path (Join-Path $ReleaseDir $file))) {
        $missing += $file
    }
}

if ($missing.Count -gt 0) {
    Write-Host "WARNING: Missing files: $($missing -join ', ')" -ForegroundColor DarkYellow
} else {
    Write-Host "  All required files present" -ForegroundColor Green
}

# Create archive
Write-Host "[6/6] Creating release archive..." -ForegroundColor Yellow
$archivePath = Join-Path $RepoRoot "dist\$ArchiveName"

# Ensure dist directory exists
New-Item -ItemType Directory -Path (Join-Path $RepoRoot "dist") -Force | Out-Null

# Remove old archive if exists
if (Test-Path $archivePath) { Remove-Item $archivePath -Force }

Push-Location $ReleaseDir
try {
    # Use tar if available (Windows 10+), otherwise create zip
    if (Get-Command "tar" -ErrorAction SilentlyContinue) {
        tar -czf $archivePath *
    } else {
        Compress-Archive -Path "*" -DestinationPath (Join-Path $RepoRoot "dist\byrd-health-$Version.zip") -Force
        Write-Host "  Created ZIP archive (tar not available)" -ForegroundColor Gray
    }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Release packaging complete!" -ForegroundColor Green
Write-Host " Release dir: $ReleaseDir" -ForegroundColor White
if (Test-Path $archivePath) {
    Write-Host " Archive: $archivePath" -ForegroundColor White
}
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Review docs/releases/RC1_VALIDATION_CHECKLIST.md" -ForegroundColor Gray
Write-Host "  2. Complete runtime validation on HA instance" -ForegroundColor Gray
Write-Host "  3. Tag release: git tag v$Version" -ForegroundColor Gray
Write-Host "  4. Push to GitHub with release notes" -ForegroundColor Gray
