@echo off
echo =========================================
echo Starting Recipe Management Backend (LOCAL MODE)
echo =========================================
echo.
echo Using SQLite database (no Supabase needed)
echo.

cd /d "%~dp0"

call venv\Scripts\activate.bat

set DJANGO_SETTINGS_MODULE=config.settings.local

echo Starting server at http://localhost:8000
echo Press Ctrl+C to stop
echo.

python manage.py runserver
