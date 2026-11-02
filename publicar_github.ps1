<# Sube el proyecto a GitHub. Uso:
   .\publicar_github.ps1 -Usuario TU_USUARIO_GITHUB
   Requiere haber creado VACIO https://github.com/TU_USUARIO/ProyectoPaginasProduction #>
param([Parameter(Mandatory)][string]$Usuario, [string]$Repo = "ProyectoPaginasProduction")
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "Instala Git en D:\DevTools\git" }
if (-not (Test-Path .git)) { git init -b main }
git add -A
Write-Host "`nArchivos que se subiran:" -ForegroundColor Cyan; git status --short
$sens = git ls-files --cached | Select-String -Pattern 'SuperUser|User\.txt|\.env$|sqlite3|Informe_Residencia'
if ($sens) { throw "Archivo sensible en el commit: $sens" }
git commit -m "Publicacion inicial: plataforma Django de matematicas remediales"
git remote remove origin 2>$null
git remote add origin "https://github.com/$Usuario/$Repo.git"
git push -u origin main
Write-Host "Publicado: https://github.com/$Usuario/$Repo" -ForegroundColor Green
