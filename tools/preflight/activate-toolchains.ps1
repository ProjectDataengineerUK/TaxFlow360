[CmdletBinding()]
param([string]$CacheRoot = $(if ($env:TAXFLOW_TOOL_CACHE) { $env:TAXFLOW_TOOL_CACHE } else { Join-Path $env:LOCALAPPDATA 'TaxFlow360\tool-cache' }))
$ErrorActionPreference = 'Stop'
$manifest = Join-Path $PSScriptRoot '..\..\config\local-toolchains.yaml'
$env:PYTHONPATH = "$(Join-Path $PSScriptRoot 'src')$([IO.Path]::PathSeparator)$env:PYTHONPATH"
$specs = python -m taxflow_preflight.cli manifest --manifest $manifest | ConvertFrom-Json
foreach ($spec in $specs) {
    if ($spec.repository_target) { continue }
    $base = Join-Path $CacheRoot (Join-Path $spec.id (Join-Path $spec.version $spec.sha256))
    $executable = Join-Path (Join-Path $base $spec.archive_root) $spec.executable
    if (-not (Test-Path -LiteralPath $executable)) { Write-Warning "$($spec.id) is not installed in the verified cache."; continue }
    $bin = Split-Path -Parent $executable
    $env:PATH = "$bin$([IO.Path]::PathSeparator)$env:PATH"
    if ($spec.id -eq 'java') { $env:JAVA_HOME = Join-Path $base $spec.archive_root }
}
$env:TAXFLOW_TOOL_CACHE = [IO.Path]::GetFullPath($CacheRoot)
$repository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
if (-not $env:GRADLE_USER_HOME) {
    $env:GRADLE_USER_HOME = Join-Path $repository '.local-evidence\gradle-home'
}
Write-Output 'TaxFlow360 toolchains activated for this PowerShell process only.'
