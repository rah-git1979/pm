$containerName = "pm-mvp-container"

try {
    docker stop $containerName | Out-Null
} catch {}

try {
    docker rm $containerName | Out-Null
} catch {}

Write-Host "Stopped pm-mvp-container"
