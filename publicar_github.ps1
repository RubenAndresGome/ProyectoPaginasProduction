<#
  publicar_github.ps1 - Sube el proyecto a GitHub SIN filtrar llaves.
  Uso (PowerShell, en la raiz del proyecto):
      .\publicar_github.ps1 -Mensaje "Describe el cambio"
  Pasos: activa el hook anti-secretos, revisa archivos y TODO el historial,
  muestra lo que se subira, pide confirmacion, hace commit y push.
#>
param(
    [string]$Mensaje = "Actualiza plataforma MathMaster",
    [string]$Remoto = "https://github.com/RubenAndresGome/ProyectoPaginasProduction.git"
)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$py = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }

function Paso($m) { Write-Host "`n==> $m" -ForegroundColor Cyan }
function Falla($m) { Write-Host "`n[DETENIDO] $m" -ForegroundColor Red; exit 1 }

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Falla "No encuentro git." }
if (-not (Test-Path .git)) { git init -b main | Out-Null }

Paso "Activando hook pre-commit anti-secretos"
git config core.hooksPath adminExe/hooks

Paso "Buscando secretos en los archivos que se subirian"
& $py adminExe\escanear_secretos.py --todo
if ($LASTEXITCODE -ne 0) { Falla "Hay posibles secretos. Muevelos a .env o marcalos como permitidos." }

Paso "Buscando secretos en TODO el historial de git"
& $py adminExe\escanear_secretos.py --historial
if ($LASTEXITCODE -ne 0) { Falla "El historial ya contiene secretos: hay que reescribirlo antes de publicar (pide ayuda)." }

Paso "Pruebas automaticas"
& $py manage.py test --verbosity 0
if ($LASTEXITCODE -ne 0) { Falla "Las pruebas fallaron." }

git add -A
git update-index --chmod=+x adminExe/hooks/pre-commit 2>$null
Paso "Cambios que se subiran"
git status --short
$ok = Read-Host "`nEscribe SI para hacer commit y push"
if ($ok -ne "SI") { git reset -q; Falla "Cancelado por el usuario (no se cambio nada)." }

git commit -m $Mensaje
if ($LASTEXITCODE -ne 0) { Falla "El commit no se hizo (revisa el mensaje del hook)." }
if (-not (git remote 2>$null | Select-String -Quiet '^origin$')) { git remote add origin $Remoto }
git push -u origin main
if ($LASTEXITCODE -ne 0) { Falla "El push fallo." }
Write-Host "`nPublicado: $($Remoto -replace '\.git$','')" -ForegroundColor Green
