@echo off
setlocal

set "ROOT=%~dp0"

echo ============================================
echo   Document Pipeline - Full Stack Dev Mode
echo ============================================
echo.
echo   Backend (FastAPI):    http://localhost:8000
echo   API Server (Express): http://localhost:3001
echo   Frontend (Vite):      http://localhost:5173
echo.
echo ============================================
echo.

if not exist "%ROOT%.venv\Scripts\python.exe" (
  echo [ERROR] Python virtual environment not found at .venv\Scripts\python.exe
  echo Create it first with: python -m venv .venv
  exit /b 1
)

REM Start FastAPI backend on port 8000
start "DocPipe Backend (FastAPI)" cmd /k "cd /d "%ROOT%" && .venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Start Express API server on port 3001 (proxies to FastAPI)
start "DocPipe API Server (Express)" cmd /k "cd /d "%ROOT%frontend\artifacts\api-server" && set "PORT=3001" && set "FASTAPI_URL=http://localhost:8000" && node build.mjs && node --enable-source-maps dist/index.mjs"

REM Start Vite frontend dev server on port 5173 (proxies /api to Express)
start "DocPipe Frontend (Vite)" cmd /k "cd /d "%ROOT%frontend\artifacts\doc-workspace" && set "PORT=5173" && set "BASE_PATH=/" && set "API_PORT=3001" && npx vite --host 0.0.0.0"

echo All three services launched in separate terminal windows.
echo Press Ctrl+C in each terminal to stop.
