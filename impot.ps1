$sqliteBrowserExe = "C:\Program Files\DB Browser for SQLite\DB Browser for SQLite.exe"
$csvFolder = "C:\Users\steve\source\repos\ParadeRoute\LA-2024"
$dbFile = "C:\Users\steve\source\repos\ParadeRoute\db.db"

if (-not (Test-Path $sqliteBrowserExe))
{
    Write-Error "sqlitebrowser.exe not found: $sqliteBrowserExe"
    exit 1
}

if (-not (Test-Path $csvFolder))
{
    Write-Error "CSV folder not found: $csvFolder"
    exit 1
}

$csvFiles = Get-ChildItem -Path $csvFolder -Filter *.csv -File

foreach ($csvFile in $csvFiles)
{
    $tableName = [System.IO.Path]::GetFileNameWithoutExtension($csvFile.Name)
    $tableName = $tableName.ToLower()
    $tableName = $tableName -replace '[^a-z0-9_]', '_'

    Write-Host "Importing $($csvFile.Name) into table [$tableName]"

    & $sqliteBrowserExe --import-csv $csvFile.FullName --table $tableName $dbFile

    if ($LASTEXITCODE -ne 0)
    {
        Write-Warning "Import failed for $($csvFile.Name)"
    }
}