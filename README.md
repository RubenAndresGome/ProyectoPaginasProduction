# ProyectoPaginas — Plataforma web de Matemáticas Remediales

Aplicación web en **Django 6** con **Tailwind CSS** desarrollada durante mi Residencia Profesional (ITESS).
Combina un CMS de páginas dinámicas, un blog con búsqueda y filtrado por categorías, autenticación de
usuarios y un **entrenador de matemáticas** que genera ejercicios aleatorios con notación LaTeX.

> 🔗 **Demo:** _pendiente_ · 👤 **Autor:** Rubén Andrés Gómez Molina

![Vista principal](docs/screenshots/home.png)

## Funcionalidades

- **CMS de páginas (`pages`)**: páginas creadas desde el admin con editor enriquecido (CKEditor) y plantillas dinámicas.
- **Blog (`blog`)**: publicaciones con categorías, URLs amigables por *slug*, búsqueda de texto y filtros combinables.
- **Entrenador (`entrenador`)**: generadores de ejercicios de aritmética, álgebra básica y avanzada, trigonometría,
  geometría, conjuntos y silogismos; cada ejercicio incluye su explicación paso a paso en LaTeX.
- **Usuarios (`login_and_reg`)**: registro e inicio de sesión.
- **Interfaz**: Tailwind CSS compilado localmente (sin CDN), modo oscuro, plantillas base reutilizables.

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
├── mainapp/       páginas principales y CRUD de artículos
├── pages/         CMS de páginas dinámicas
├── blog/          publicaciones y categorías
├── entrenador/    generadores de ejercicios (generators/*.py) y servicios
├── login_and_reg/ autenticación
└── theme/         plantillas base y estilos
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
pip install -r requirements.txt
cp .env.example .env            # usa SQLite por defecto
python manage.py migrate && python manage.py createsuperuser
python manage.py runserver
```
Abre <http://127.0.0.1:8000/>.

## Configuración

Todas las opciones sensibles se leen de `.env` (ver [`.env.example`](.env.example)); ninguna credencial vive en el código.

## Despliegue

Guía de despliegue gratuito en PythonAnywhere: [`docs/DEPLOY_PYTHONANYWHERE.md`](docs/DEPLOY_PYTHONANYWHERE.md).
