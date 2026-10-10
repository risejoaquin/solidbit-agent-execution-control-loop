# scripts\sacl-monitor.ps1
# SACL V1 Live Terminal Console Dashboard Wrapper
# Preserves the operator experience from MONITOR.ps1 in read-only mode (zero lock contention).

[CmdletBinding()]
param(
    [string]$RunId = "",
    [ValidateRange(1, 120)]
    [int]$RefreshSeconds = 10,
    [string]$DbPath = "",
    [switch]$Once
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$SrcDir = Join-Path $RepoRoot "src"
$env:PYTHONPATH = "$SrcDir;$env:PYTHONPATH"

$cliArgs = @("-m", "sacl.cli", "monitor", "--refresh", $RefreshSeconds)

if ($RunId) {
    $cliArgs += @("--run-id", $RunId)
}
if ($DbPath) {
    $cliArgs += @("--db", $DbPath)
}
if ($Once) {
    $cliArgs += "--once"
}

& python $cliArgs
exit $LASTEXITCODE
