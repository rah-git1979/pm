$containerName = "pm-mvp-container"

docker build -t pm-mvp .

try {
    docker stop $containerName | Out-Null
} catch {}

try {
    docker rm $containerName | Out-Null
} catch {}

$envFile = "$PSScriptRoot\..\.env"
$envFlag = if (Test-Path $envFile) { "--env-file", $envFile } else { @() }
docker run -d --name $containerName -p 8000:8000 @envFlag pm-mvp
Write-Host "Started pm-mvp-container on http://localhost:8000"
