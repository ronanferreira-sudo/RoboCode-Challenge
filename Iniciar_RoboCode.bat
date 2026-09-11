@echo off
title RoboCode Challenge Launcher
cd /d "c:\projetos\RoboCode Challenge"
echo ========================================================
echo   Iniciando o RoboCode Challenge...
echo ========================================================
echo.
echo Abrindo a plataforma no navegador...
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8000"
.\venv\Scripts\python run.py
pause
