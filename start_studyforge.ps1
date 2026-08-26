$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"

if (-not (Test-Path (Join-Path $backend "app\main.py"))) {
    throw "Backend not found at $backend"
}
if (-not (Test-Path (Join-Path $frontend "package.json"))) {
    throw "Frontend not found at $frontend"
}

$backendCommand = "Set-Location -LiteralPath '$backend'; py -3.10 -m uvicorn app.main:app --host 127.0.0.1 --port 8001"
$frontendCommand = "Set-Location -LiteralPath '$frontend'; npm.cmd run dev"

Start-Process powershell.exe -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $backendCommand)
Start-Sleep -Seconds 2
Start-Process powershell.exe -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $frontendCommand)

Start-Sleep -Seconds 6

try {
    $health = Invoke-RestMethod "http://127.0.0.1:8001/health" -TimeoutSec 5
    if ($health.status -ne "ok") {
        throw "The wrong service is running on port 8001."
    }
    Write-Host "Backend:  http://127.0.0.1:8001/health" -ForegroundColor Green
    Write-Host "Frontend: http://localhost:3002" -ForegroundColor Green
    Write-Host "Signup:   http://localhost:3002/signup" -ForegroundColor Green
} catch {
    Write-Host "Backend did not become healthy. Check the backend terminal for the exact error." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
