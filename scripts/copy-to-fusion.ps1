param(
    [string]$FusionAddInRoot = "$env:APPDATA\Autodesk\Autodesk Fusion\API\AddIns"
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$source = $projectRoot
$target = Join-Path $FusionAddInRoot (Split-Path $projectRoot -Leaf)

if (-not (Test-Path $source)) {
    throw "Source add-in folder not found: $source"
}

if (-not (Test-Path $FusionAddInRoot)) {
    New-Item -ItemType Directory -Path $FusionAddInRoot | Out-Null
}

if (Test-Path $target) {
    Remove-Item -LiteralPath $target -Recurse -Force
}

Copy-Item -LiteralPath $source -Destination $target -Recurse
Write-Host "Copied FusionBambuBridge to $target"
