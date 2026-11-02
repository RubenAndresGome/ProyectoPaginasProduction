# AGENTS.md — ProyectoPaginas (Django)

Guía operativa para agentes de IA (Claude, Copilot, Codex, Gemini…).
**Ubicación canónica en Windows:**
`D:\DocumentosWin\PROGRAMACION\Nueva carpeta\pythonProyects\DJANGO\ProyectoPaginas`

> La ruta contiene **espacios** (`Nueva carpeta`). Entrecomilla SIEMPRE las rutas
> en PowerShell, CMD y scripts. Arquitectura funcional detallada: `ARQUITECTURA.md`.

---

## 1. Reglas no negociables

1. **Toda herramienta nueva se instala en `D:\`** — raíz `D:\DevTools\`. Nunca en `C:\`.
   | Herramienta | Ruta |
   |---|---|
   | uv | `D:\DevTools\uv\uv.exe` |
   | Python 3.12 (gestionado por uv) | `D:\DevTools\python\` |
   | Caché uv / pip / npm | `D:\DevTools\cache\{uv,pip,npm}` |
   | Tailwind standalone | `D:\DevTools\tailwind\tailwindcss-v3.4.1.exe` (`%TAILWIND_BIN%`) |
   Variables de usuario ya definidas por `setup_windows.ps1`: `UV_INSTALL_DIR`,
   `UV_PYTHON_INSTALL_DIR`, `UV_CACHE_DIR`, `PIP_CACHE_DIR`, `npm_config_cache`, `TAILWIND_BIN`.
   Si instalas algo distinto (Node, MySQL, etc.) usa `D:\DevTools\<nombre>` y documéntalo aquí.
2. **Python 3.12 exacto.** Django 6.0 requiere ≥3.12 y `Pillow==10.1.0` no tiene wheel para 3.13.
3. **El proyecto debe seguir funcionando en Linux** (origen). Nada de rutas `C:\`/`D:\`
   dentro del código: usa `BASE_DIR / ...` (`pathlib`). Las rutas de disco solo viven en
   scripts de Windows y en `.env`.
4. **No commitear**: `.env`, `.venv/`, `db.sqlite3`, `media/`, binarios de Tailwind.
5. **No tocar migraciones existentes**; crea nuevas con `makemigrations`.

## 2. Arranque en Windows

```powershell
cd "D:\DocumentosWin\PROGRAMACION\Nueva carpeta\pythonProyects\DJANGO\ProyectoPaginas"
powershell -ExecutionPolicy Bypass -File .\setup_windows.ps1   # una vez (idempotente)
.\run_windows.bat                                               # día a día
```
Comandos sueltos (sin activar venv):
```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py test
& $env:TAILWIND_BIN -i static\src\styles.css -o static\css\dist\styles.css --watch
```
Activar venv: `.\.venv\Scripts\Activate.ps1` (PowerShell) / `.venv\Scripts\activate.bat` (CMD).

## 3. Equivalencias Linux → Windows

| Linux (original) | Windows |
|---|---|
| `source venv/bin/activate` | `.\.venv\Scripts\Activate.ps1` |
| `./tailwindcss ...` (ELF, **no ejecuta en Windows**) | `& $env:TAILWIND_BIN ...` |
| `requirements.txt` | `requirements-windows.txt` (sin gunicorn/uWSGI) |
| MySQL vía `systemctl` | SQLite por defecto en `.env`; MySQL opcional (sección 5) |
| `cp .env.example .env` | lo hace `setup_windows.ps1` |
| `./script.sh` | equivalente `.ps1`/`.bat`; no asumir bash |

## 4. Arquitectura (resumen)

- `ProyectoPaginas/` — settings, urls raíz, wsgi/asgi.
- `mainapp` — páginas estáticas + CRUD `Article`; templatetags en `mainapp/templatetags/filters.py`.
- `pages` — CMS de páginas dinámicas; context processor `get_pages`.
- `blog` — `Articulo_Page` + `Categoria` (slug); context processor `get_categorias`.
- `login_and_reg` — autenticación/registro.
- `entrenador` — generadores de ejercicios matemáticos (`entrenador/generators/*.py`, salida LaTeX `\[ ... \]`; las `\\` son escapes LaTeX, **no** separadores de ruta: no "corregirlas").
- `theme` — plantillas base (`TEMPLATES.DIRS = BASE_DIR/'theme'/'templates'`).
- Estáticos: entrada Tailwind `static/src/styles.css` → salida `static/css/dist/styles.css`
  (la que cargan las plantillas). Config: `tailwind.config.js` (v3, `darkMode: 'class'`).
- Editor enriquecido: `django-ckeditor`. Debug toolbar activa solo con `DEBUG=True`.

## 5. Configuración (`.env` en la RAÍZ)

`settings.py` lee `BASE_DIR / '.env'` (ruta explícita; antes buscaba junto a settings.py).
- `DB_ENGINE=django.db.backends.sqlite3` → `NAME = BASE_DIR / DB_NAME` (portable).
- MySQL en Windows: instalar servidor en `D:\DevTools\mysql`, cambiar `DB_*` en `.env`.
  `mysqlclient` trae wheel para Windows/Py3.12; si falla, usar SQLite.
- Ver `.env.example` y `ENV_SETUP.md`.

## 6. Convenciones

- Idioma: español en código de dominio, comentarios y UI.
- Finales de línea gobernados por `.gitattributes` (LF; CRLF solo `.bat/.ps1`).
- Archivos en UTF-8. En Python abre archivos con `encoding="utf-8"` explícito
  (Windows usa cp1252 por defecto).
- Antes de terminar una tarea: `manage.py check` + `manage.py test` deben pasar.

## 7. Pendientes conocidos

- `settings.py` conserva una contraseña MySQL por defecto en código: moverla solo a `.env`.
- `.._` en la raíz es basura AppleDouble (macOS); se puede borrar.
- `tailwindcss` (ELF Linux) se mantiene para el flujo Linux; en Windows se ignora.
