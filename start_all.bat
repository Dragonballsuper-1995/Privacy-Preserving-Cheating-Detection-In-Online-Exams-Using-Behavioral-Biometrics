@echo off
echo Starting Cheating Detector Application...

:: Start Backend
echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

:: Start Frontend
echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo ---------------------------------------------------
echo Application is starting up!
echo Backend will allow connections on: http://127.0.0.1:8000
echo Frontend will be available at: http://localhost:3000
echo Direct admin login will be available at: http://localhost:3000/login/auto-admin
echo ---------------------------------------------------
pause
