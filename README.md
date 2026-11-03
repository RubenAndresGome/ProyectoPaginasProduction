# MathMaster — Plataforma web de Matemáticas Remediales

![CI](https://github.com/RubenAndresGome/ProyectoPaginasProduction/actions/workflows/ci.yml/badge.svg)

Aplicación web en **Django 6** con **Tailwind CSS** desarrollada durante mi Residencia Profesional (ITESS).
Combina un CMS de páginas dinámicas, un blog con búsqueda y filtrado por categorías, autenticación de
usuarios y un **entrenador de matemáticas** que genera ejercicios aleatorios con notación LaTeX.

> 🔗 **Demo:** _pendiente_ · 👤 **Autor:** Rubén Andrés Gómez Molina

![Vista principal](docs/screenshots/home.png)

## Funcionalidades

**Para estudiantes**
- **Entrenador adaptativo** (`entrenador`): 7 temas (aritmética, álgebra básica y avanzada, geometría, trigonometría,
  conjuntos y silogismos) con ejercicios generados al azar en 10 niveles; sube de nivel con aciertos seguidos y
  muestra la explicación paso a paso en LaTeX.
- **Perfil** (`perfil`): racha de días, precisión, temas dominados, actividad de 14 días y nivel por tema.
- **Tutor** (`mensajes`): chat por reglas que recomienda el tema con menos aciertos usando tus datos reales,
  resume tu progreso y enlaza artículos relacionados (sin servicios de pago).
- **Blog público** con búsqueda dentro del contenido, me gusta, compartir (Web Share / WhatsApp / LinkedIn / X)
  y descarga de cada artículo en **Markdown**.

**Para el administrador**
- **Editor visual por bloques** con vista previa en vivo renderizada por el servidor (lo que ves es lo que se publica):
  11 tipos de bloque (texto, imagen, tabla, fórmula, código, video…), plantillas (tutorial, lista, caso de estudio,
  comparativa, guía, tema matemático), reordenar, insertar, subir imágenes y publicar/despublicar.
- **Métricas** del blog: vistas únicas por día, me gusta, compartidos y tiempo de lectura.
- **Configuración del sitio** desde el perfil: nombre, lema, WhatsApp y redes del pie de página con vista previa.
- **Bandeja de mensajes** del formulario de contacto (anti-spam con honeypot y límite por hora); el usuario ve la respuesta.

**Ingeniería**
- 40 pruebas automatizadas (permisos, XSS, CSRF, editor, métricas, tutor, generadores) en GitHub Actions.
- Datos de bloques validados con lista blanca en el servidor; autoescape en todas las plantillas.
- Sistema de diseño único (Tailwind + componentes), modo claro/oscuro y navegación accesible con teclado.

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12, Django 6.0, django-environ |
| Base de datos | SQLite (desarrollo) / MySQL (opcional) |
| Frontend | Tailwind CSS 3.4, plantillas Django, MathJax/LaTeX |
| Contenido | django-ckeditor, Pillow |
| Producción | WhiteNoise, configuración por variables de entorno |

## Arquitectura

```
ProyectoPaginas/   configuración (settings, urls, wsgi)
├── mainapp/       portada, contacto y CRUD clásico de artículos
├── blog/          artículos por bloques, plantillas, editor visual, métricas, Markdown
├── entrenador/    generadores de ejercicios (generators/*.py) y motor adaptativo
├── perfil/        perfil de usuario y configuración del sitio (redes del footer)
├── mensajes/      contacto, bandeja del admin y tutor por reglas
├── pages/         CMS de páginas dinámicas
├── login_and_reg/ autenticación
└── theme/         base única, menú, pie de página y componentes
```
Detalle de flujos y decisiones de diseño: [`ARQUITECTURA.md`](ARQUITECTURA.md).

## Ejecutar localmente

**Windows**
```powershell
powershell -ExecutionPolicy Bypass -File .\setup_windows.ps1   # instala en D:\DevTools, crea .venv y .env
.\run_windows.bat
```

**Linux / macOS**
```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env            # usa SQLite por defecto
python manage.py migrate && python manage.py createsuperuser
python manage.py runserver
```
Abre <http://127.0.0.1:8000/>.

## Herramientas y seguridad del repositorio

Las herramientas externas (Tailwind, uv) no se versionan: se descargan verificadas con SHA-256
para Windows (`.exe`) o Linux (paquete `.deb`) desde un manifiesto tipo requirements:

```bash
python adminExe/descargar_tools.py --plataforma todas   # adminExe/dist/toolsForWindows y toolsForLinux
```

Un hook pre-commit y un job de CI bloquean llaves, contraseñas y archivos sensibles
(`.env`, bases de datos, llaves privadas). Detalles en [`adminExe/README.md`](adminExe/README.md).

```bash
git config core.hooksPath adminExe/hooks   # una vez por clon
```

## Pruebas

```bash
python manage.py test          # Windows: .\.venv\Scripts\python.exe manage.py test
```

## Configuración

Todas las opciones sensibles se leen de `.env` (ver [`.env.example`](.env.example)); ninguna credencial vive en el código.

## Despliegue

Guía de despliegue gratuito en PythonAnywhere: [`docs/DEPLOY_PYTHONANYWHERE.md`](docs/DEPLOY_PYTHONANYWHERE.md).
