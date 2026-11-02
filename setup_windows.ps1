<#
  setup_windows.ps1 - Prepara ProyectoPaginas en Windows.
  REGLA: toda herramienta nueva se instala en D:\ (por defecto D:\DevTools).
  Uso (PowerShell, en la raiz del proyecto):
      powershell -ExecutionPolicy Bypass -File .\setup_windows.ps1
  Idempotente: se puede ejecutar varias veces.
#>
param(
    [string]$ToolsRoot = "D:\DevTools",
    [string]$PythonVersion = "3.12",
    [string]$TailwindVersion = "v3.4.1"
)
$ErrorActionPreference = "Stop"
$Proj = $PSScriptRoot
Set-Location $Proj

function Step($m) { Write-Host "`n==> $m" -ForegroundColor Cyan }

# --- 1. Rutas en D: (persistentes a nivel usuario) -------------------------
Step "Configurando rutas de herramientas en $ToolsRoot"
$vars = @{
    UV_INSTALL_DIR        = "$ToolsRoot\uv"
    UV_PYTHON_INSTALL_DIR = "$ToolsRoot\python"
    UV_CACHE_DIR          = "$ToolsRoot\cache\uv"
    PIP_CACHE_DIR         = "$ToolsRoot\cache\pip"
    npm_config_cache      = "$ToolsRoot\cache\npm"
}
foreach ($k in $vars.Keys) {
    New-Item -ItemType Directory -Force -Path $vars[$k] | Out-Null
    Set-Item -Path "env:$k" -Value $vars[$k]
    [Environment]::SetEnvironmentVariable($k, $vars[$k], "User")
}
New-Item -ItemType Directory -Force -Path "$ToolsRoot\tailwind" | Out-Null

# --- 2. uv (gestor de Python/paquetes) en D:\DevTools\uv --------------------
$uv = "$ToolsRoot\uv\uv.exe"
if (-not (Test-Path $uv)) {
    Step "Instalando uv en $ToolsRoot\uv"
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
}
if (-not (Test-Path $uv)) { throw "uv no quedo en $uv" }

# --- 3. Python 3.12 (Django 6 lo exige; Pillow 10.1 no tiene wheel para 3.13)
Step "Instalando Python $PythonVersion en $ToolsRoot\python"
& $uv python install $PythonVersion

# --- 4. Entorno virtual del proyecto (.venv, ignorado por git) -------------
$py = "$Proj\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Step "Creando .venv"
    & $uv venv "$Proj\.venv" --python $PythonVersion
}
Step "Instalando dependencias (requirements-windows.txt)"
& $uv pip install --python $py -r "$Proj\requirements-windows.txt"

# --- 5. Tailwind standalone para Windows -----------------------------------
$tw = "$ToolsRoot\tailwind\tailwindcss-$TailwindVersion.exe"
if (-not (Test-Path $tw)) {
    Step "Descargando Tailwind $TailwindVersion (Windows x64)"
    Invoke-WebRequest -UseBasicParsing `
        -Uri "https://github.com/tailwindlabs/tailwindcss/releases/download/$TailwindVersion/tailwindcss-windows-x64.exe" `
        -OutFile $tw
}
[Environment]::SetEnvironmentVariable("TAILWIND_BIN", $tw, "User")
$env:TAILWIND_BIN = $tw

# --- 6. .env de desarrollo (SQLite) ----------------------------------------
if (-not (Test-Path "$Proj\.env")) {
    Step "Creando .env de desarrollo (SQLite)"
    $key = & $py -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
    $lineas = (Get-Content "$Proj\.env.example") -replace '^SECRET_KEY=.*', "SECRET_KEY=$key"
    [IO.File]::WriteAllLines("$Proj\.env", $lineas, (New-Object Text.UTF8Encoding $false))  # UTF-8 sin BOM
}

# --- 7. Verificacion --------------------------------------------------------
Step "Compilando CSS y verificando Django"
& $tw -i "$Proj\static\src\styles.css" -o "$Proj\static\css\dist\styles.css" --minify
& $py manage.py check
& $py manage.py migrate --noinput
Write-Host "`nListo. Ejecuta run_windows.bat para levantar el servidor." -ForegroundColor Green
Write-Host "Abre una NUEVA terminal para que las variables de usuario (UV_*, TAILWIND_BIN) tomen efecto." -ForegroundColor Yellow
