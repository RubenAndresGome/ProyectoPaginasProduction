# CLAUDE.md — ProyectoPaginas

@AGENTS.md

Las reglas comunes están en `AGENTS.md` (importado arriba). Esto añade solo lo específico de Claude.

## Entorno
- SO de trabajo: **Windows**. Proyecto en
  `D:\DocumentosWin\PROGRAMACION\Nueva carpeta\pythonProyects\DJANGO\ProyectoPaginas`
  (ruta con espacios → entrecomillar siempre).
- Shell preferida: PowerShell. No asumir bash/WSL; no proponer `source`, `chmod`, `./binario`.
- Intérprete: `.\.venv\Scripts\python.exe` (no `python` global).
- **Cualquier instalación nueva → `D:\DevTools\<herramienta>`**. Pide confirmación antes de instalar.

## Flujo de trabajo
1. Leer `ARQUITECTURA.md` antes de tocar `pages` o `blog` (lógica no trivial de plantillas dinámicas).
2. Cambios pequeños y verificables; tras cada cambio de modelos: `makemigrations` → `migrate`.
3. Verificar con `manage.py check` y `manage.py test` antes de dar algo por terminado.
4. Si cambias clases Tailwind en plantillas nuevas, añade la ruta al `content` de `tailwind.config.js`
   (hoy solo cubre `mainapp` y `theme`; `pages`, `blog`, `login_and_reg`, `entrenador` faltan).

## No hacer
- No editar `db.sqlite3`, `media/` ni migraciones aplicadas.
- No reintroducir `environ.Env.read_env()` sin ruta.
- No "arreglar" las `\\` de `entrenador/generators` (son LaTeX).
