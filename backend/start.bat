@echo off
echo =========================================
echo Starting Recipe Management Backend
echo =========================================
echo.

cd /d "%~dp0"

if not exist "venv\" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/3] Checking for .env file...
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo Please copy env.example to .env and configure it.
    pause
    exit /b 1
)

echo [3/3] Starting Django development server...
echo.
echo Backend will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/api/swagger/
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver

pause
