# AGENTS.md — ProyectoPaginas (Django)

Guía operativa para agentes de IA (Claude, Copilot, Codex, Gemini…).
**Ubicación canónica en Windows:**
`D:\DocumentosWin\PROGRAMACION\Nueva carpeta\pythonProyects\DJANGO\ProyectoPaginas\ProyectoPaginasProduction`

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
cd "D:\DocumentosWin\PROGRAMACION\Nueva carpeta\pythonProyects\DJANGO\ProyectoPaginas\ProyectoPaginasProduction"
powershell -ExecutionPolicy Bypass -File .\setup_windows.ps1   # una vez (idempotente)
.\run_windows.bat   # día a día: SQLite + admin de prueba (admin/1234) + Tailwind watch
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
- `theme` — **base única**: `base.html` (menú + footer + toasts + tutor) y `base_pura.html` (sin menú, para login).
  `_head.html` compartido. Componentes CSS (`btn-primario`, `tarjeta`, `campo`, `nav-link`…) en `static/src/styles.css`
  (`@layer components`). Nunca crear otra base: extender una de estas dos.
- `mainapp` — portada (`index`), contacto (con formulario de `mensajes`) y CRUD clásico `Article` (solo staff, borrar por POST).
- `blog` — artículos por bloques, plantillas, editor visual (`editor_views.py`, staff), likes, vistas, compartir,
  métricas y exportación a Markdown (`markdown.py`). Lectura pública; borradores solo staff.
- `entrenador` — generadores (`generators/*.py`, salida LaTeX `\[ ... \]`; las `\\` son LaTeX, **no** rutas) y motor adaptativo.
- `perfil` — `Perfil` (señal post_save), `ConfiguracionSitio` (registro único pk=1) y `RedSocial`; context processor
  `sitio` → `{{ sitio }}` y `{{ redes_sociales }}` en todas las plantillas. Edición del sitio: solo staff en `/perfil/`.
- `mensajes` — `Mensaje` (contacto, honeypot `sitio_web`, 3/hora por sesión), bandeja staff, `bot.py` (tutor por reglas).
- `pages` — CMS de páginas dinámicas (sin cambios); `pages/templates/layauts/` son plantillas HTML descargadas.
- `login_and_reg` — namespace **`log_and_reg`** (definido en `include()`), no `login_and_reg`.
- Estáticos: `static/src/styles.css` → `static/css/dist/styles.css` (se versiona; el servidor no compila Tailwind).

### Motor de artículos por bloques (`blog`)
- `Plantilla.estructura` (JSON) = lista de `{"tipo", "datos"}`; al crear un `Articulo_Page` con plantilla,
  `aplicar_plantilla()` inserta cada elemento como un `Bloque` (FK `articulo`, `orden`, `datos` JSON, `imagen`).
- Tipos y campos de `datos`: `Bloque.ESQUEMA`. Cada tipo se pinta con `blog/templates/articulos/bloques/_<tipo>.html`
  (autoescape activo: nunca usar `|safe` sobre `datos`).
- Plantillas base en `blog/plantillas_base/` (sembradas por la migración 0007). Demo: `manage.py blog_demo`.
- `content` (CKEditor) queda como contenido clásico opcional para artículos antiguos.

## 5. Configuración (`.env` en la RAÍZ)

`settings.py` lee `BASE_DIR / '.env'` (ruta explícita; antes buscaba junto a settings.py).
- `DB_ENGINE=django.db.backends.sqlite3` → `NAME = BASE_DIR / DB_NAME` (portable).
- MySQL en Windows: instalar servidor en `D:\DevTools\mysql`, cambiar `DB_*` en `.env`.
  `mysqlclient` trae wheel para Windows/Py3.12; si falla, usar SQLite.
- Ver `.env.example` y `ENV_SETUP.md`.

## 5a. Herramientas y secretos (`adminExe/`)

- Herramientas externas SOLO vía `adminExe/requirements-tools.txt` + `descargar_tools.py` (SHA-256 obligatorio).
  Nunca descargar binarios sin hash ni versionarlos: `adminExe/dist/` está en `.gitignore`.
- Salidas: `adminExe/dist/toolsForWindows/` (.exe) y `adminExe/dist/toolsForLinux/` (bin/ + `.deb`).
- Antes de cualquier commit corre el hook `adminExe/hooks/pre-commit` (`git config core.hooksPath adminExe/hooks`).
  Si marca algo: moverlo a `.env`; solo datos de prueba llevan `# secretos: permitido`.
- Publicar: `.\publicar_github.ps1 -Mensaje "..."` (escanea archivos + historial y corre pruebas antes del push).

## 5b. Pruebas

- `manage.py test` (40 pruebas: permisos, XSS, CSRF, editor, métricas, tutor, generadores). CI: `.github/workflows/ci.yml`.
- Toda vista nueva de staff: `@staff_member_required`; toda acción que modifica datos: `@require_POST` + CSRF.
- Todo dato de bloque pasa por `blog.bloques.limpiar()` (lista blanca). Nunca `|safe` sobre datos de usuario.
- Archivos apartados para borrar: `_to_delete/` (ignorado por git).

## 6. Convenciones

- Idioma: español en código de dominio, comentarios y UI.
- Finales de línea gobernados por `.gitattributes` (LF; CRLF solo `.bat/.ps1`).
- Archivos en UTF-8. En Python abre archivos con `encoding="utf-8"` explícito
  (Windows usa cp1252 por defecto).
- Antes de terminar una tarea: `manage.py check` + `manage.py test` deben pasar.

## 7. Pendientes conocidos

- Dos sistemas de artículos: `mainapp.Article` (CRUD clásico) y `blog.Articulo_Page` (bloques). Migrar el primero
  al segundo y retirar el CRUD clásico.
- `django-ckeditor` empaqueta CKEditor 4 sin soporte (aviso `ckeditor.W001`); el editor por bloques ya no lo necesita.
- `.._` en la raíz es basura AppleDouble (macOS); ignorado por git.
