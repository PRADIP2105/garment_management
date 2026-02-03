@echo off
echo Starting Garment Management Mobile App...
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting Flet mobile application...
echo Make sure the Django server is running at http://127.0.0.1:8000/
echo.

python mobile_app.py