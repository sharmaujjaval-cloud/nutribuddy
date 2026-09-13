@echo off
echo ========================================================
echo   🥗 NutriBuddy - SDG 2 Zero Hunger Assistant
echo ========================================================
echo.

set PORT=8501
netstat -ano | findstr 0.0.0.0:8501 >nul
if not errorlevel 1 (
    echo [Info] Port 8501 is in use. Using alternate port 8502...
    set PORT=8502
)

echo Launching NutriBuddy on port %PORT%...
echo Local address: http://localhost:%PORT%
echo.

if exist .venv\Scripts\streamlit.exe (
    .venv\Scripts\streamlit.exe run app.py --server.port %PORT%
) else (
    streamlit run app.py --server.port %PORT%
)

pause
