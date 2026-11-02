# Despliegue gratuito en PythonAnywhere

Plan gratuito: 1 app en `TUUSUARIO.pythonanywhere.com`, sin tarjeta. Hay que renovar con un clic cada 3 meses
(botón *Run until 3 months from today* en la pestaña **Web**).

## 1. Consola Bash (pestaña *Consoles*)
```bash
git clone https://github.com/TUUSUARIO/ProyectoPaginasProduction.git
cd ProyectoPaginasProduction
python3.12 -m venv ~/.venvs/paginas
source ~/.venvs/paginas/bin/activate
pip install -r requirements.txt
cp .env.example .env
```
Edita `.env`:
```env
DEBUG=False
SECRET_KEY=<python -c "from django.core.management.utils import get_random_secret_key as g;print(g())">
ALLOWED_HOSTS=TUUSUARIO.pythonanywhere.com
CSRF_TRUSTED_ORIGINS=https://TUUSUARIO.pythonanywhere.com
SECURE_SSL_REDIRECT=False
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 2. Pestaña *Web* → *Add a new web app* → **Manual configuration** → Python 3.12
- **Virtualenv:** `/home/TUUSUARIO/.venvs/paginas`
- **Static files:** URL `/static/` → `/home/TUUSUARIO/ProyectoPaginasProduction/staticfiles`
- **Static files:** URL `/media/` → `/home/TUUSUARIO/ProyectoPaginasProduction/media`
- **WSGI file** (reemplazar contenido):
```python
import os, sys
path = '/home/TUUSUARIO/ProyectoPaginasProduction'
if path not in sys.path:
    sys.path.insert(0, path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'ProyectoPaginas.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```
- Pulsa **Reload**.

## 3. Actualizar tras cambios
```bash
cd ~/ProyectoPaginasProduction && git pull
source ~/.venvs/paginas/bin/activate
python manage.py migrate && python manage.py collectstatic --noinput
```
y **Reload** en la pestaña Web.
