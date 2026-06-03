param(
    [Parameter(Mandatory = $true)]
    [string]$OpenPiDir,

    [Parameter(Mandatory = $true)]
    [string]$RawHdf5,

    [Parameter(Mandatory = $true)]
    [string]$RepoId,

    [string]$ExperimentName = "xarm_pi05_lora",
    [int]$Fps = 10
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $OpenPiDir)) {
    throw "OpenPI directory not found: $OpenPiDir"
}

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Converter = Join-Path $ProjectRoot "scripts\prepare_openpi_lerobot.py"

Push-Location $OpenPiDir
try {
    Write-Host "Converting raw xArm HDF5 data to LeRobot..."
    uv run python $Converter --input $RawHdf5 --repo-id $RepoId --fps $Fps --overwrite

    Write-Host ""
    Write-Host "Next, add the pi05_xarm config snippet from:"
    Write-Host "  $ProjectRoot\fine_tune\openpi_xarm_config.py"
    Write-Host "to:"
    Write-Host "  $OpenPiDir\src\openpi\training\config.py"
    Write-Host "and set repo_id to: $RepoId"
    Write-Host ""

    Write-Host "Computing normalization stats..."
    uv run scripts/compute_norm_stats.py --config-name pi05_xarm

    Write-Host "Starting fine-tuning..."
    $env:XLA_PYTHON_CLIENT_MEM_FRACTION = "0.9"
    uv run scripts/train.py pi05_xarm --exp-name=$ExperimentName --overwrite
}
finally {
    Pop-Location
}
