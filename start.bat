@echo off
REM Navigate to your Django project directory
cd /d "C:\Users\desktop\Desktop\cantine\cantine"

REM Start the Django development server
start cmd /k "python manage.py runserver"

REM Wait briefly to ensure the server starts before opening the browser
timeout /t 5 /nobreak > NUL

REM Open the default web browser to your Django app
start "" "http://127.0.0.1:8000/"
