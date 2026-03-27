@echo off
setlocal

set "ROOT=%~dp0"

echo Starting Document Pipeline full stack...
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.

if not exist "%ROOT%\.venv\Scripts\python.exe" (
  echo [ERROR] Python virtual environment not found at .venv\Scripts\python.exe
  echo Create it first with: python -m venv .venv
  exit /b 1
)

start "DocPipe Backend" cmd /k "cd /d "%ROOT%" ^&^& .\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"
start "DocPipe Frontend" cmd /k "cd /d "%ROOT%\frontend" ^&^& npm run dev"

echo Both services were launched in separate terminals.
echo Press Ctrl+C in each terminal to stop.
