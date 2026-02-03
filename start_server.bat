@echo off
echo Starting Garment Management System...
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting Django development server...
echo.
echo The application will be available at:
echo - Web Application: http://127.0.0.1:8000/
echo - Admin Panel: http://127.0.0.1:8000/admin/
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver 127.0.0.1:8000