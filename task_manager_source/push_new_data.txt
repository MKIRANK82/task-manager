$ProjectRoot = Get-Location
$Source = Join-Path $ProjectRoot "task_manager_source"

if (!(Test-Path $Source)) {
    Write-Host "ERROR: Source folder not found:"
    Write-Host $Source
    exit 1
}

Write-Host ""
Write-Host "Source:"
Write-Host $Source

Write-Host ""
Write-Host "Target:"
Write-Host $ProjectRoot

Write-Host ""
Write-Host "Starting deployment..."
Write-Host ""

$CopiedCount = 0
$CreatedCount = 0

Get-ChildItem -Path $Source -Recurse -File |
ForEach-Object {

    # Get path relative to task_manager_source
    $relativePath = $_.FullName.Substring(
        $Source.Length + 1
    )

    # Build destination path
    $destination = Join-Path `
        $ProjectRoot `
        $relativePath

    # Get destination directory
    $destinationFolder = Split-Path `
        $destination `
        -Parent

    # Create directory only if it does not exist
    if (!(Test-Path $destinationFolder)) {

        New-Item `
            -ItemType Directory `
            -Path $destinationFolder `
            -Force |
        Out-Null

        Write-Host "[NEW FOLDER] $destinationFolder"
    }

    # Check whether file already exists
    if (Test-Path $destination) {

        Copy-Item `
            -Path $_.FullName `
            -Destination $destination `
            -Force

        Write-Host "[UPDATED] $relativePath"

        $CopiedCount++
    }
    else {

        Copy-Item `
            -Path $_.FullName `
            -Destination $destination

        Write-Host "[NEW FILE] $relativePath"

        $CreatedCount++
    }
}

Write-Host ""
Write-Host "================================="
Write-Host "Deployment completed."
Write-Host "================================="
Write-Host ""
Write-Host "Updated files : $CopiedCount"
Write-Host "New files     : $CreatedCount"
Write-Host ""
Write-Host "Existing files not in the source were NOT deleted."
Write-Host "Existing folders were NOT deleted."
Write-Host ""