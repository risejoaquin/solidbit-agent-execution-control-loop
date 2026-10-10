# scripts\sacl-launch.ps1
# SACL V1 Wave Package Launch Wrapper
# Preserves the operator experience from RUN-WAVE.ps1 while executing via the SACL V1 engine.

[CmdletBinding()]
param(
    [Parameter(Position=0, Mandatory=$false)]
    [Alias("WaveDir", "PackageZip")]
    [string]$Package,

    [int]$MaxParallel = 4,

    [Alias("TargetRepo")]
    [string]$Repo = "",

    [string]$SourceOrchestrator = "C:\Users\Lucilfer\Documents\Stable-Ecommerce-Orchestrator",

    [switch]$BypassAcknowledged,

    [switch]$TestMode,

    [string]$RunDir = "",

    [string]$DbPath = "",

    [int]$TimeoutMinutes = 30
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# 1. Resolve Script & Repository Roots
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$SrcDir = Join-Path $RepoRoot "src"

# 2. Safety Gate: Bypass Acknowledged Check (matches RUN-WAVE.ps1#L7)
if (-not $BypassAcknowledged -and -not $TestMode) {
    Write-Host "[SECURITY REFUSAL] ACK_REQUIRED: --dangerously-skip-permissions grants broad host access." -ForegroundColor Red
    Write-Host "Pass -BypassAcknowledged to confirm authorized execution." -ForegroundColor Yellow
    exit 2
}

# 3. Locate Target Package
$TargetPackage = $Package
if ([string]::IsNullOrWhiteSpace($TargetPackage)) {
    # Check if current directory has a manifest.json or runs/
    if (Test-Path "manifest.json") {
        $TargetPackage = (Get-Location).Path
    } else {
        Write-Host "[ERROR] Missing wave package path. Specify -Package <path_to_wave_or_zip>" -ForegroundColor Red
        exit 1
    }
}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "               SACL V1 WAVE EXECUTION LAUNCHER                        " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Package:     $TargetPackage"
Write-Host "MaxParallel: $MaxParallel"
Write-Host "TestMode:    $TestMode"
if ($Repo) { Write-Host "Target Repo: $Repo" }
if ($DbPath) { Write-Host "Database:    $DbPath" }
Write-Host "----------------------------------------------------------------------"

# 4. Invoke SACL Python CLI Engine
$env:PYTHONPATH = "$SrcDir;$env:PYTHONPATH"

$cliArgs = @("-m", "sacl.cli", "launch", $TargetPackage, "--max-parallel", $MaxParallel, "--timeout-minutes", $TimeoutMinutes)

if ($BypassAcknowledged) {
    $cliArgs += "--bypass-acknowledged"
}
if ($TestMode) {
    $cliArgs += "--test-mode"
}
if ($Repo) {
    $cliArgs += @("--repo", $Repo)
}
if ($SourceOrchestrator) {
    $cliArgs += @("--source-orchestrator", $SourceOrchestrator)
}
if ($RunDir) {
    $cliArgs += @("--run-dir", $RunDir)
}
if ($DbPath) {
    $cliArgs += @("--db", $DbPath)
}

& python $cliArgs
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host "[SUCCESS] Wave execution completed successfully." -ForegroundColor Green
} else {
    Write-Host "[FAILURE] Wave execution exited with code $exitCode." -ForegroundColor Red
}

exit $exitCode
