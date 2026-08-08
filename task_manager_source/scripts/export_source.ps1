$Source = Get-Location
$Target = Join-Path $Source "task_manager_source"

if (Test-Path $Target) {
    Remove-Item $Target -Recurse -Force
}

New-Item -ItemType Directory -Path $Target | Out-Null

$IncludeExtensions = @(
    "*.py",
    "*.html",
    "*.css",
    "*.js",
    "*.json",
    "*.toml",
    "*.lock",
    "*.md",
    "*.txt",
    "*.yaml",
    "*.yml",
    "*.ps1"
)

$ExcludeFolders = @(
    ".venv",
    "__pycache__",
    ".git",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    "task_manager_source",
    "htmlcov"
)

Get-ChildItem -Path $Source -Recurse -File |
Where-Object {

    $file = $_

    $extensionMatch = $false

    foreach ($pattern in $IncludeExtensions) {
        if ($file.Name -like $pattern) {
            $extensionMatch = $true
            break
        }
    }

    if (-not $extensionMatch) {
        return $false
    }

    foreach ($folder in $ExcludeFolders) {
        if ($file.FullName -match "\\$folder\\") {
            return $false
        }
    }

    if ($file.Name -match "^task\.db") {
        return $false
    }

    return $true

} | ForEach-Object {

    $relative = $_.FullName.Substring($Source.Path.Length + 1)

    $destination = Join-Path $Target $relative

    $parent = Split-Path $destination

    if (!(Test-Path $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }

    Copy-Item $_.FullName $destination
}

Write-Host ""
Write-Host "Export completed."
Write-Host "Folder:"
Write-Host $Target

$ZipFile = Join-Path $Source "task_manager_source.zip"

# Remove previous ZIP if it exists
if (Test-Path $ZipFile) {
    Remove-Item $ZipFile -Force
}

# Create ZIP - no password
Compress-Archive `
    -Path "$Target\*" `
    -DestinationPath $ZipFile `
    -CompressionLevel Optimal

Write-Host ""
Write-Host "ZIP created successfully."
Write-Host "ZIP file:"
Write-Host $ZipFile