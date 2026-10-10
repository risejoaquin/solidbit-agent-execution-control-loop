# scripts\sacl-package.ps1
# SACL V1 Canonical Wave ZIP Packaging & Integrity Verification Wrapper
# Preserves the package bundling and verification experience per ADR-004.

[CmdletBinding()]
param(
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet("Create", "Verify", "Extract")]
    [string]$Action,

    [Parameter(Position=1, Mandatory=$true)]
    [Alias("InputDir", "PackageFile")]
    [string]$Path,

    [Alias("OutputFile")]
    [string]$Output = "",

    [Alias("OutputDir")]
    [string]$Destination = "",

    [switch]$PrefixRoot
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$SrcDir = Join-Path $RepoRoot "src"
$env:PYTHONPATH = "$SrcDir;$env:PYTHONPATH"

$lowerAction = $Action.ToLower()

if ($lowerAction -eq "create") {
    $cliArgs = @("-m", "sacl.cli", "package", "create", $Path)
    if ($Output) { $cliArgs += @("--output", $Output) }
    if ($PrefixRoot) { $cliArgs += "--prefix-root" }
    & python $cliArgs
} elseif ($lowerAction -eq "verify") {
    $cliArgs = @("-m", "sacl.cli", "package", "verify", $Path)
    & python $cliArgs
} elseif ($lowerAction -eq "extract") {
    $targetDest = if ($Destination) { $Destination } else { $Output }
    if (-not $targetDest) {
        Write-Host "[ERROR] Extraction requires destination directory (-Destination <path>)" -ForegroundColor Red
        exit 1
    }
    $cliArgs = @("-m", "sacl.cli", "package", "extract", $Path, $targetDest)
    & python $cliArgs
}

exit $LASTEXITCODE
