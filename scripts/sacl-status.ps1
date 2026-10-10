# scripts\sacl-status.ps1
# SACL V1 Agent & Run Execution Status Wrapper
# Preserves the operator experience from status.ps1 while querying SACL V1 state.

[CmdletBinding()]
param(
    [string]$RunId = "",
    [string]$Agent = "all",
    [string]$DbPath = "",
    [Alias("WaveDir")]
    [string]$RunDir = "",
    [switch]$Json,
    [switch]$Watch,
    [Alias("Interval")]
    [int]$RefreshSeconds = 5
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$SrcDir = Join-Path $RepoRoot "src"
$env:PYTHONPATH = "$SrcDir;$env:PYTHONPATH"

$baseArgs = @("-m", "sacl.cli", "status", "--agent", $Agent)

if ($RunId) {
    $baseArgs += @("--run-id", $RunId)
}
if ($DbPath) {
    $baseArgs += @("--db", $DbPath)
}
if ($RunDir) {
    $baseArgs += @("--run-dir", $RunDir)
}
if ($Json) {
    $baseArgs += "--json"
}

if ($Watch) {
    Write-Host "[INFO] Watching status every $RefreshSeconds seconds. Press Ctrl+C to stop." -ForegroundColor Cyan
    try {
        while ($true) {
            Clear-Host
            & python $baseArgs
            Start-Sleep -Seconds $RefreshSeconds
        }
    } catch {
        Write-Host "`n[INFO] Stopped watching."
    }
} else {
    & python $baseArgs
}

exit $LASTEXITCODE
