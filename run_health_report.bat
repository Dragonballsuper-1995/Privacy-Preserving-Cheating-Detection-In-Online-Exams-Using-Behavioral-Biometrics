@echo off
echo ============================================================
echo   Project Health Report Generator
echo ============================================================
echo.

cd /d "%~dp0"
call backend\venv\Scripts\activate.bat

echo Installing report dependencies (if needed)...
pip install pylint radon pip-audit -q 2>nul

echo.
echo Running health report generator...
echo.
cd backend
python scripts/generate_health_report.py

echo.
echo ============================================================
echo   Report saved to: docs\PROJECT_HEALTH_REPORT.md
echo ============================================================
pause
