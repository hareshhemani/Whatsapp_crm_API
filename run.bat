@echo off
title WhatsApp CRM Automation
echo.
echo ==========================================
echo    Starting WhatsApp CRM Automation...
echo ==========================================
echo.

:: Start the browser after a short delay to give the server time to initialize
start "" "http://localhost:8000"

:: Run the FastAPI application
python -m app.main

pause
