# scripts\sacl-stop.ps1
# SACL V1 Safe Stop & Kill Switch Wrapper
# Preserves the operator experience from stop-agents.ps1 while enforcing the
# 3-Way PID Recycling Defense to ensure unrelated system processes are never harmed.

[CmdletBinding()]
param(
    [string]$Agent = "all",
    [string]$RunId = "",
    [string]$DbPath = "",
    [Alias("WaveDir")]
    [string]$RunDir = "",
    [switch]$All,
    [Alias("Pid", "TargetPid")]
    [int]$ProcessId = 0,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$SrcDir = Join-Path $RepoRoot "src"
$env:PYTHONPATH = "$SrcDir;$env:PYTHONPATH"

$cliArgs = @("-m", "sacl.cli", "stop")

if ($All) {
    $cliArgs += "--all"
} elseif ($Agent) {
    $cliArgs += @("--agent", $Agent)
}

if ($ProcessId -gt 0) {
    $cliArgs += @("--pid", $ProcessId)
}
if ($RunId) {
    $cliArgs += @("--run-id", $RunId)
}
if ($DbPath) {
    $cliArgs += @("--db", $DbPath)
}
if ($RunDir) {
    $cliArgs += @("--run-dir", $RunDir)
}
if ($Force) {
    $cliArgs += "--force"
}

& python $cliArgs
exit $LASTEXITCODE
