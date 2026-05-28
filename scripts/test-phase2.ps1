# Phase 2 validation script for the backend scaffold
# Run from the repository root using PowerShell.

$containerName = "pm-mvp-test"
$imageName = "pm-mvp"
$port = 8000

Write-Host "Building Docker image $imageName..."
docker build -t $imageName .

Write-Host "Cleaning up any existing container named $containerName..."
if (docker ps -a --format "{{.Names}}" | Select-String -Pattern "^$containerName$") {
    docker rm -f $containerName | Out-Null
}

Write-Host "Starting container $containerName..."
docker run -d --name $containerName -p $port:8000 $imageName | Out-Null

# wait for service
$maxAttempts = 20
$attempt = 0
$ok = $false
while (-not $ok -and $attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 1
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$port/api/hello" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            $ok = $true
            break
        }
    } catch {
        $attempt++
    }
}

if (-not $ok) {
    Write-Error "The backend did not respond on http://localhost:$port/api/hello after $maxAttempts seconds."
    docker logs $containerName
    docker rm -f $containerName | Out-Null
    exit 1
}

Write-Host "Backend is responding. Checking routes..."
$routes = @("/", "/api/hello", "/api/health")
foreach ($route in $routes) {
    $url = "http://localhost:$port$route"
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
        Write-Host "[$route] Status: $($response.StatusCode)"
        $bodyPreview = $response.Content.Trim()
        if ($bodyPreview.Length -gt 200) {
            $bodyPreview = $bodyPreview.Substring(0, 200) + "..."
        }
        Write-Host $bodyPreview
    } catch {
        Write-Error "Route $route failed: $_"
        docker logs $containerName
        docker rm -f $containerName | Out-Null
        exit 1
    }
}

Write-Host "Running backend tests inside the container..."
docker run --rm -e PYTHONPATH=/app $imageName sh -c "pip install pytest httpx >/dev/null 2>&1 && python -m pytest /app/backend/tests/test_api.py"
$exitCode = $LASTEXITCODE

Write-Host "Stopping and removing container $containerName..."
docker stop $containerName | Out-Null
docker rm $containerName | Out-Null

if ($exitCode -ne 0) {
    Write-Error "Backend tests failed with exit code $exitCode."
    exit $exitCode
}

Write-Host "Phase 2 validation succeeded."
