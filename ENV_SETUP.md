# Configuración de Seguridad: Variables de Entorno (`.env`)

## ¿Qué es `.env`?

El archivo `.env` (Environment File) contiene configuraciones sensibles del proyecto Django que **NUNCA deben ser commitidas a git**. Incluye:

- `SECRET_KEY` — clave secreta para encriptación
- `DEBUG` — modo de depuración
- Credenciales de base de datos
- Configuraciones de seguridad (HTTPS, cookies)

---

## 📋 Configuración Rápida (Desarrollo Local)

### 1. Copiar el archivo de ejemplo
```bash
cp .env.example .env
```

El archivo `.env` ya contiene valores por defecto apropiados para **desarrollo local**.

### 2. Verificar que funciona
```bash
python manage.py check
```

Deberías ver solo advertencias de CKEditor y ckeditor (seguras de ignorar en desarrollo).

---

## 🔐 Para Producción ⚠️

Si vas a desplegar en producción, **DEBES** actualizar `.env` con valores seguros:

### Generar SECRET_KEY segura
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copia el resultado y pégalo en `.env`:
```env
SECRET_KEY=tu-clave-aleatoria-super-larga-aqui
```

### Activar HTTPS & Cookies Seguras
```env
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
```

---

## 📖 Variables Disponibles

Consulta `.env.example` para ver todas las variables configurables:

| Variable | Descripción | Ejemplo (Desarrollo) | Ejemplo (Producción) |
|---|---|---|---|
| `DEBUG` | Modo depuración | `True` | `False` |
| `SECRET_KEY` | Clave secreta Django | `django-insecure-...` | (generada con get_random_secret_key) |
| `ALLOWED_HOSTS` | Dominios permitidos | `localhost,127.0.0.1` | `tudominio.com,www.tudominio.com` |
| `DB_ENGINE` | Motor de BD | `django.db.backends.mysql` | igual |
| `DB_NAME` | Nombre de BD | `django` | `produccion_db` |
| `SECURE_SSL_REDIRECT` | Forzar HTTPS | `False` | `True` |
| `SESSION_COOKIE_SECURE` | Cookies solo HTTPS | `False` | `True` |

---

## ✅ Cómo Django Lee `.env`

El archivo `settings.py` usa `django-environ` para leer automáticamente todas las variables desde `.env`:

```python
import environ

env = environ.Env()
environ.Env.read_env()

DEBUG = env.bool('DEBUG', default=True)
SECRET_KEY = env.str('SECRET_KEY', default='...')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost'])
```

Si una variable no está en `.env`, Django usa el valor `default`.

---

## 🛡️ Seguridad Automática en Producción

Cuando `DEBUG=False`, Django **automáticamente activa** estas protecciones:

```
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
```

---

## ❌ Errores Comunes

### Error: "Invalid HTTP_HOST header"
**Causa:** Host no está en `ALLOWED_HOSTS`  
**Solución:** Añade el host a `.env`:
```env
ALLOWED_HOSTS=localhost,127.0.0.1,tu-ip,tu-dominio
```

### Error: "SECRET_KEY is not set"
**Causa:** El .env no existe o `SECRET_KEY` está vacía  
**Solución:** Copia `.env.example` a `.env` y edita

### Error: "Database connection refused"
**Causa:** Credenciales de BD incorrectas en `.env`  
**Solución:** Verifica `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

---

## 📝 Preguntas Frecuentes

**P: ¿Puedo commitiar `.env`?**  
R: **NO.** El `.env` está en `.gitignore` por seguridad. Solo commitia `.env.example`.

**P: ¿Cómo comparto `.env` con mi equipo?**  
R: Comparte `.env.example` (con valores por defecto) en git. Cada persona copia y personaliza su propio `.env`.

**P: ¿Qué valores necesito en producción?**  
R: Al menos:
- `DEBUG=False`
- `SECRET_KEY=` (valor generado con get_random_secret_key)
- `ALLOWED_HOSTS=` (tu dominio)
- Credenciales correctas de BD
- `SECURE_SSL_REDIRECT=True` (si usas HTTPS)

---

## 🚀 Próximos Pasos

1. ✅ Copia `.env.example` a `.env`
2. ✅ Ejecuta `python manage.py check --deploy` para ver si hay advertencias
3. ✅ En producción, genera una SECRET_KEY segura
4. ✅ Activa HTTPS y configura `SECURE_SSL_REDIRECT=True`

---

**Última actualización:** 2026-05-24  
**Django:** 6.0.3  
**Python:** 3.12+
