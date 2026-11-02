===============================================================================
📘 README: INTEGRACIÓN DE TAILWIND CSS CON DJANGO
===============================================================================

Este documento explica cómo configurar y utilizar Tailwind CSS en un proyecto
Django de manera local, sin dependencias de CDNs externos. Sigue estos pasos
para asegurar que Tailwind compile correctamente y Django sirva los estilos
sin errores.

-------------------------------------------------------------------------------
1. ESTRUCTURA DEL PROYECTO
-------------------------------------------------------------------------------

Organiza tu proyecto de la siguiente manera para evitar conflictos de rutas:

tu_proyecto/
|-- manage.py
|-- db.sqlite3
|-- tu_proyecto/              # Configuración de Django
|   |-- settings.py
|   |-- urls.py
|   `-- ...
|-- static/                   # Archivos estáticos globales
|   |-- src/
|   |   `-- styles.css        # Archivo de entrada de Tailwind
|   `-- css/
|       `-- dist/
|           `-- styles.css    # Archivo compilado (generado automáticamente)
|-- miapp/                    # Tu aplicación Django
|   |-- templates/
|   `-- ...
|-- theme/                    # App de templates base
|   |-- templates/
|   |   |-- base.html
|   |   `-- base_menu.html
|   `-- ...
`-- tailwind.config.js        # Configuración de Tailwind (en la raíz)

-------------------------------------------------------------------------------
2. CONFIGURACIÓN DE DJANGO (settings.py)
-------------------------------------------------------------------------------

2.1. Archivos Estáticos:

    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent.parent

    STATIC_URL = 'static/'
    STATIC_ROOT = BASE_DIR / "staticfiles"
    STATICFILES_DIRS = [
        BASE_DIR / "static",      # Carpeta static en la raíz
    ]

2.2. Configuración de Tailwind (si usas django-tailwind):

    INSTALLED_APPS = [
        # ... apps de Django
        'tailwind',
        'theme',                  # App que contiene los templates base
        'miapp',
    ]

    TAILWIND_APP_NAME = 'theme'
    TAILWIND_USE_STANDALONE_BINARY = True
    TAILWIND_STANDALONE_BINARY_VERSION = "v3.4.1"
    TAILWIND_CLI_SRC_CSS = "static/src/styles.css"
    TAILWIND_CLI_DIST_CSS = "static/css/dist/styles.css"

    INTERNAL_IPS = ["127.0.0.1"]

NOTA: Si usas el binario directo (sin django-tailwind), no necesitas estas
configuraciones. Solo asegura que STATICFILES_DIRS apunte a la carpeta correcta.

-------------------------------------------------------------------------------
3. CONFIGURACIÓN DE TAILWIND (tailwind.config.js)
-------------------------------------------------------------------------------

Crea o edita el archivo tailwind.config.js en la RAIZ DEL PROYECTO:

    module.exports = {
      content: [
        "./templates/**/*.html",
        "./miapp/templates/**/*.html",
        "./theme/templates/**/*.html",
      ],
      theme: {
        extend: {},
      },
      plugins: [],
    }

IMPORTANTE: Las rutas en "content" son relativas a la ubicación del archivo.

-------------------------------------------------------------------------------
4. ARCHIVO DE ENTRADA DE TAILWIND
-------------------------------------------------------------------------------

Crea "static/src/styles.css" con el siguiente contenido (v3.x):

    @tailwind base;
    @tailwind components;
    @tailwind utilities;

NOTA: Para Tailwind v4.x, usa @import "tailwindcss"; en su lugar.

-------------------------------------------------------------------------------
5. FLUJO DE TRABAJO: COMPILAR TAILWIND -> LANZAR DJANGO
-------------------------------------------------------------------------------

OPCIÓN A: Usando django-tailwind (Recomendado)

    1. Instalar binario: python manage.py tailwind install
    2. Iniciar compilador: python manage.py tailwind start (Terminal 1)
    3. Lanzar Django: python manage.py runserver (Terminal 2)

OPCIÓN B: Usando el Binario Directo (Sin django-tailwind)

    1. Descargar y dar permisos:
       curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.1/tailwindcss-linux-x64
       chmod +x tailwindcss-linux-x64
       mv tailwindcss-linux-x64 tailwindcss

    2. Iniciar compilador:
       ./tailwindcss -i static/src/styles.css -o static/css/dist/styles.css --watch

    3. Lanzar Django: python manage.py runserver (Terminal 2)

-------------------------------------------------------------------------------
6. VINCULAR EL CSS EN TUS TEMPLATES
-------------------------------------------------------------------------------

En "theme/templates/base.html":

    {% load static %}
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="{% static 'css/dist/styles.css' %}">
    </head>
    <body>
        <main class="container mx-auto px-4 py-8">
            {% block content %}{% endblock %}
        </main>
    </body>
    </html>

-------------------------------------------------------------------------------
7. VERIFICACIÓN
-------------------------------------------------------------------------------

7.1. Terminal Tailwind: Debería decir "Rebuilding... Done in XXXms".
7.2. Archivo generado: Ejecuta "ls -lh static/css/dist/styles.css" (no vacío).
7.3. Navegador: F12 -> Network -> CSS. styles.css debe dar estado 200.

-------------------------------------------------------------------------------
8. PROBLEMAS COMUNES Y SOLUCIONES
-------------------------------------------------------------------------------

PROBLEMA                     | CAUSA PROBABLE         | SOLUCIÓN
-----------------------------|------------------------|------------------------
Error 404 en styles.css      | STATICFILES_DIRS mal   | Revisar settings.py
Clases no se aplican         | Rutas en "content" mal | Revisar config.js
CSS vacío                    | No detecta clases      | Reiniciar compilador
'theme' isn't Tailwind app   | Estructura incorrecta  | tailwind init theme

-------------------------------------------------------------------------------
9. CUÁNDO REINICIAR
-------------------------------------------------------------------------------

- Cambiaste tailwind.config.js  -> SI (Reiniciar compilador)
- Cambiaste un archivo HTML     -> NO (Watch lo detecta)
- Cambiaste settings.py         -> SI (Reiniciar Django)
- Moviste archivos de lugar     -> SI (Reiniciar ambos)

-------------------------------------------------------------------------------
10. CHECKLIST DE IMPLEMENTACIÓN
-------------------------------------------------------------------------------

[ ] Estructura de directorios creada (static/src/, static/css/dist/)
[ ] static/src/styles.css con directivas @tailwind
[ ] tailwind.config.js en la raíz con rutas correctas
[ ] settings.py con STATICFILES_DIRS configurado
[ ] base.html con link a {% static 'css/dist/styles.css' %}
[ ] Tailwind corriendo en Terminal 1 (--watch)
[ ] Django corriendo en Terminal 2 (runserver)

-------------------------------------------------------------------------------
RESUMEN DEL FLUJO
-------------------------------------------------------------------------------

  TERMINAL 1: Tailwind (Watch mode)
  ./tailwindcss -i static/src/styles.css -o ... --watch
            |
            v
  TERMINAL 2: Django Server
  python manage.py runserver
            |
            v
  NAVEGADOR: http://127.0.0.1:8000/
  - CSS carga sin 404
  - Estilos aplicados con éxito

-------------------------------------------------------------------------------
REFERENCIAS: tailwindcss.com/docs | django-tailwind.readthedocs.io
===============================================================================