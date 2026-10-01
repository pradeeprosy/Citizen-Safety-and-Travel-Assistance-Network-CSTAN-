@echo off
echo =========================================================
echo    CSTAN - Citizen Safety and Travel Assistance Network
echo =========================================================
echo.

:: Check for python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b 1
)

:: Install requirements if not present
echo [1/3] Verifying dependencies...
python -m pip install -r requirements.txt --quiet

:: Seed database if cstan.db does not exist
if not exist cstan.db (
    echo [2/3] Initializing and seeding demo database...
    python seed_data.py
) else (
    echo [2/3] Database found.
)

:: Start Flask app
echo [3/3] Launching CSTAN application server on http://127.0.0.1:5000 ...
echo.
echo =========================================================
echo   Tourist Demo: tourist@cstan.org / password123
echo   Admin Demo:   admin@cstan.org   / admin123
echo =========================================================
echo.
start http://127.0.0.1:5000
python app.py
pause
