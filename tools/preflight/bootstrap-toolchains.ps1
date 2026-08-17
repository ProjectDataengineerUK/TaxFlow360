[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidateSet('java','node','terraform','databricks','gradle-wrapper')][string]$Tool,
    [string]$ManifestPath = (Join-Path $PSScriptRoot '..\..\config\local-toolchains.yaml'),
    [string]$CacheRoot = $(if ($env:TAXFLOW_TOOL_CACHE) { $env:TAXFLOW_TOOL_CACHE } else { Join-Path $env:LOCALAPPDATA 'TaxFlow360\tool-cache' }),
    [string]$ExistingArtifact
)
$ErrorActionPreference = 'Stop'
$repository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$pythonPath = Join-Path $PSScriptRoot 'src'
$env:PYTHONPATH = "$pythonPath$([IO.Path]::PathSeparator)$env:PYTHONPATH"
$json = python -m taxflow_preflight.cli manifest --manifest $ManifestPath --tool $Tool
if ($LASTEXITCODE -ne 0) { throw 'Manifest validation failed.' }
$spec = @($json | ConvertFrom-Json)[0]
$uri = [Uri]$spec.archive_url
if ($uri.Scheme -ne 'https' -or $spec.official_hosts -notcontains $uri.Host) { throw 'Unapproved download origin.' }

$cache = [IO.Path]::GetFullPath($CacheRoot)
$stagingRoot = Join-Path $cache '.staging'
$null = New-Item -ItemType Directory -Force -Path $stagingRoot
$archive = Join-Path $stagingRoot ("{0}-{1}.download" -f $spec.id, [Guid]::NewGuid())
try {
    if ($ExistingArtifact) {
        Copy-Item -LiteralPath ([IO.Path]::GetFullPath($ExistingArtifact)) -Destination $archive
    } else {
        $curl = Get-Command curl.exe -ErrorAction Stop
        & $curl.Source --fail --silent --show-error --location --max-redirs 5 --max-time 120 `
            --output $archive --url $spec.archive_url
        if ($LASTEXITCODE -ne 0) { throw "Download failed for $Tool." }
    }
    if ((Get-Item -LiteralPath $archive).Length -gt $spec.max_archive_bytes) { throw 'Artifact exceeds approved size.' }
    $actual = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $spec.sha256) { throw "Checksum mismatch for $Tool." }
    if ($spec.repository_target) {
        $target = [IO.Path]::GetFullPath((Join-Path $repository $spec.repository_target))
        if (-not $target.StartsWith($repository, [StringComparison]::OrdinalIgnoreCase)) { throw 'Invalid repository target.' }
        $null = New-Item -ItemType Directory -Force -Path (Split-Path $target)
        Copy-Item -LiteralPath $archive -Destination $target -Force
    } else {
        $target = Join-Path $cache (Join-Path $spec.id (Join-Path $spec.version $spec.sha256))
        $stage = "$target.staging"
        if (Test-Path -LiteralPath $stage) { throw "Staging path already exists: $stage" }
        $null = New-Item -ItemType Directory -Path $stage
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $zip = [IO.Compression.ZipFile]::OpenRead($archive)
        try {
            foreach ($entry in $zip.Entries) {
                $candidate = [IO.Path]::GetFullPath((Join-Path $stage $entry.FullName))
                if (-not $candidate.StartsWith(([IO.Path]::GetFullPath($stage) + [IO.Path]::DirectorySeparatorChar), [StringComparison]::OrdinalIgnoreCase)) {
                    throw 'Archive path traversal detected.'
                }
            }
        } finally { $zip.Dispose() }
        & tar.exe -xf $archive -C $stage
        if ($LASTEXITCODE -ne 0) { throw "Archive extraction failed for $Tool." }
        if (Test-Path -LiteralPath $target) { throw "Verified cache target already exists: $target" }
        Move-Item -LiteralPath $stage -Destination $target
    }
    Write-Output "Installed verified $Tool $($spec.version)."
} finally {
    if (Test-Path -LiteralPath $archive) { Remove-Item -LiteralPath $archive -Force }
}
