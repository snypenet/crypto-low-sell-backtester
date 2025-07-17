# Init-Environment.ps1
# PowerShell script to set up Python virtual environment and install dependencies

param(
    [switch]$Recreate
)

$venvPath = "./.venv"
$requirements = "./requirements.txt"

Write-Host "Setting up Python virtual environment..."

# Remove existing virtual environment if -Recreate is specified
if ($Recreate -and (Test-Path $venvPath)) {
    Write-Host "Removing existing virtual environment..."
    Remove-Item -Recurse -Force $venvPath
}

# Create new virtual environment if it doesn't exist
if (!(Test-Path $venvPath)) {
    Write-Host "Creating new virtual environment..."
    python -m venv $venvPath
} else {
    Write-Host "Virtual environment already exists. Use -Recreate to force recreation."
}

# Activate the virtual environment
$activateScript = Join-Path $venvPath "Scripts/Activate.ps1"
Write-Host "Activating virtual environment..."
. $activateScript

# Use the venv's python executable
$venvPython = Join-Path $venvPath "Scripts/python.exe"

# Upgrade pip using the venv's python
Write-Host "Upgrading pip..."
& $venvPython -m pip install --upgrade pip

# Install requirements using the venv's python
if (Test-Path $requirements) {
    Write-Host "Installing packages from requirements.txt..."
    & $venvPython -m pip install -r $requirements
} else {
    Write-Host "requirements.txt not found. Skipping package installation."
}

Write-Host "Environment setup complete." 