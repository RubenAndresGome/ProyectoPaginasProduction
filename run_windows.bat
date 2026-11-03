@echo off
setlocal
title ProyectoPaginas - Servidor de desarrollo (Windows)
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] No existe .venv. Ejecuta primero:
    echo     powershell -ExecutionPolicy Bypass -File .\setup_windows.ps1
    pause & exit /b 1
)
set "PY=.venv\Scripts\python.exe"

:: --- Tailwind: TAILWIND_BIN (si lo definiste) o el descargado y verificado en adminExe\dist
if "%TAILWIND_BIN%"=="" set "TAILWIND_BIN=%~dp0adminExe\dist\toolsForWindows\tailwindcss.exe"
if not exist "%TAILWIND_BIN%" (
    echo [INFO] Descargando herramientas verificadas con SHA-256...
    "%PY%" adminExe\descargar_tools.py --plataforma windows
    if errorlevel 1 ( echo [ERROR] No se pudieron descargar las herramientas. & pause & exit /b 1 )
    set "TAILWIND_BIN=%~dp0adminExe\dist\toolsForWindows\tailwindcss.exe"
)

echo [OK] Base de datos SQLite (db.sqlite3) - migraciones...
"%PY%" manage.py migrate --noinput

echo [OK] Admin de prueba...
"%PY%" manage.py shell -c "exec(open('scripts/crear_admin_local.py', encoding='utf-8').read())"

echo [OK] Articulos de demostracion...
"%PY%" manage.py blog_demo

echo [OK] Compilando CSS una vez y abriendo Tailwind en modo watch...
"%TAILWIND_BIN%" -i static\src\styles.css -o static\css\dist\styles.css
start "Tailwind Watch" cmd /k ""%TAILWIND_BIN%" -i static\src\styles.css -o static\css\dist\styles.css --watch"

echo.
echo   Sitio:  http://127.0.0.1:8000/
echo   Admin:  http://127.0.0.1:8000/admin/   (admin / 1234)
echo.
start "" "http://127.0.0.1:8000/"
"%PY%" manage.py runserver
pause
