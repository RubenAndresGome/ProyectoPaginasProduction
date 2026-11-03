# CLAUDE.md — ProyectoPaginas

@AGENTS.md

Las reglas comunes están en `AGENTS.md` (importado arriba). Esto añade solo lo específico de Claude.

## Entorno
- SO de trabajo: **Windows**. Proyecto en
  `D:\DocumentosWin\PROGRAMACION\Nueva carpeta\pythonProyects\DJANGO\ProyectoPaginas\ProyectoPaginasProduction`
  (ruta con espacios → entrecomillar siempre).
- Shell preferida: PowerShell. No asumir bash/WSL; no proponer `source`, `chmod`, `./binario`.
- Intérprete: `.\.venv\Scripts\python.exe` (no `python` global).
- **Cualquier instalación nueva → `D:\DevTools\<herramienta>`**. Pide confirmación antes de instalar.

## Flujo de trabajo
1. Leer `ARQUITECTURA.md` antes de tocar `pages` o `blog` (lógica no trivial de plantillas dinámicas).
2. Cambios pequeños y verificables; tras cada cambio de modelos: `makemigrations` → `migrate`.
3. Verificar con `manage.py check`, `makemigrations --check` y `manage.py test` antes de dar algo por terminado;
   agrega pruebas para cada vista o permiso nuevo.
4. Apps nuevas: añádelas a la lista `apps` de `tailwind.config.js` y recompila el CSS
   (`& $env:TAILWIND_BIN -i static\src\styles.css -o static\css\dist\styles.css --minify`).
5. Plantillas nuevas: extender `base.html` (o `base_pura.html`) y usar los componentes (`btn-primario`, `tarjeta`, `campo`).

## No hacer
- No editar `db.sqlite3`, `media/` ni migraciones aplicadas.
- No reintroducir `environ.Env.read_env()` sin ruta.
- No "arreglar" las `\\` de `entrenador/generators` (son LaTeX).
