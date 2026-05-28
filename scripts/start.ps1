$containerName = "pm-mvp-container"

docker build -t pm-mvp .

try {
    docker stop $containerName | Out-Null
} catch {}

try {
    docker rm $containerName | Out-Null
} catch {}

docker run -d --name $containerName -p 8000:8000 pm-mvp
Write-Host "Started pm-mvp-container on http://localhost:8000"
