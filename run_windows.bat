@echo off
setlocal
title ProyectoPaginas - Servidor de desarrollo (Windows)
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] No existe .venv. Ejecuta primero:
    echo     powershell -ExecutionPolicy Bypass -File .\setup_windows.ps1
    pause & exit /b 1
)
if "%TAILWIND_BIN%"=="" set "TAILWIND_BIN=D:\DevTools\tailwind\tailwindcss-v3.4.1.exe"

echo [OK] Migraciones...
".venv\Scripts\python.exe" manage.py migrate --noinput

echo [OK] Tailwind en modo watch (ventana aparte)...
start "Tailwind Watch" cmd /k ""%TAILWIND_BIN%" -i static\src\styles.css -o static\css\dist\styles.css --watch"

echo [OK] Django en http://127.0.0.1:8000/
".venv\Scripts\python.exe" manage.py runserver
pause
