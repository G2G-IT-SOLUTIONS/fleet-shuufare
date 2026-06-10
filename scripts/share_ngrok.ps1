# <#
# PowerShell helper to start the FastAPI app and open an ngrok tunnel.

# Usage (PowerShell, from repo root):
#   .\scripts\share_ngrok.ps1

# Prereqs:
#   - Activate your venv or ensure Python from `.venv` is available.
#   - Install dependencies: `pip install -r requirements.txt`
#   - Install ngrok and authenticate (optional for stable subdomain).

# This script will:
#   1. Start `uvicorn app.main:app` bound to 0.0.0.0:8000.
#   2. Launch `ngrok http 8000` (if `ngrok` is on PATH).

# #>

# Push-Location $PSScriptRoot
# try {
#     # Ensure running from repo root
#     $repoRoot = Resolve-Path "$(Join-Path $PSScriptRoot '..')"
#     Set-Location $repoRoot

#     # Activate venv if present
#     $venvPython = Join-Path $repoRoot '.venv\Scripts\python.exe'
#     if (-Not (Test-Path $venvPython)) {
#         Write-Host "Warning: .venv python not found. Ensure your virtualenv is activated or Python is on PATH."
#     }

#     $python = if (Test-Path $venvPython) { $venvPython } else { 'python' }

#     # Start uvicorn
#     Write-Host "Starting uvicorn on http://0.0.0.0:8000 ..."
#     $uvicornArgs = "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
#     Start-Process -FilePath $python -ArgumentList $uvicornArgs -WindowStyle Hidden

#     # Give the server a moment to start
#     Start-Sleep -Seconds 2

#     # Start ngrok if available
#     if (Get-Command ngrok -ErrorAction SilentlyContinue) {
#         Write-Host "Launching ngrok tunnel (http -> :8000). Press Ctrl+C to stop."
#         & ngrok http 8000
#     }
#     else {
#         Write-Host "ngrok not found on PATH. Install ngrok from https://ngrok.com/download and run: ngrok http 8000"
#     }
# }
# finally {
#     Pop-Location
# }
