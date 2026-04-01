@echo off
echo ========================================
echo   Garment Management System - Starting
echo ========================================

:: Activate virtual environment if exists
if exist ".venv\Scripts\activate.bat" (
    echo [1/4] Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo [1/4] No venv found, using system Python...
)

:: Run Django migrations
echo [2/4] Running migrations...
python manage.py migrate --run-syncdb

:: Collect static files
echo [3/4] Collecting static files...
python manage.py collectstatic --noinput

:: Start Django in a new window
echo [4/4] Starting Django server at http://192.168.1.32:8000 ...
start "Django Web Server" cmd /k "python manage.py runserver 0.0.0.0:8000"

:: Wait 3 seconds then open browser
timeout /t 3 /nobreak >nul
start http://localhost:8000

:: Install mobile dependencies if node_modules missing
if not exist "mobile-app\node_modules" (
    echo [5/5] Installing mobile app dependencies...
    cd mobile-app
    npm install
    cd ..
)

:: Start Ionic in a new window
echo [5/5] Starting Ionic mobile app at http://192.168.1.32:8100 ...
start "Ionic Mobile App" cmd /k "cd mobile-app && ionic serve --host=0.0.0.0 --port=8100"

echo ========================================
echo   Both servers are starting up!
echo   Web:    http://localhost:8000
echo   Mobile: http://localhost:8100
echo   LAN Web:    http://192.168.1.32:8000
echo   LAN Mobile: http://192.168.1.32:8100
echo ========================================
pause
