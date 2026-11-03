# Política de seguridad

## Reportar una vulnerabilidad

Si encuentras un problema de seguridad, **no abras un issue público**. Escríbeme por la página de contacto del sitio
o mediante un [aviso privado de seguridad en GitHub](../../security/advisories/new). Respondo en un máximo de 7 días.

## Medidas implementadas

| Riesgo (OWASP Top 10 2021) | Medida |
|---|---|
| A01 Control de acceso | `@staff_member_required` en editor, métricas, bandeja y configuración; borradores ocultos; cada bloque se valida contra su artículo. Cubierto por pruebas. |
| A02 Fallas criptográficas | Contraseñas con PBKDF2 de Django; cookies `Secure`/`HttpOnly`/`SameSite`; HSTS y redirección HTTPS con `DEBUG=False`. |
| A03 Inyección / XSS | ORM de Django (sin SQL crudo); autoescape en plantillas; datos de bloques filtrados por lista blanca (`blog/bloques.py`); URLs `javascript:` rechazadas; CSP activa. |
| A04 Diseño inseguro | Acciones que modifican datos solo por POST + CSRF (incluye borrar y cerrar sesión). |
| A05 Configuración | `DEBUG=False` por defecto; el sitio no arranca con `SECRET_KEY` insegura en producción; secretos solo en `.env` (ignorado por git). |
| A06 Componentes vulnerables | `pip-audit` en cada push (CI). Aviso conocido: `django-ckeditor` (CKEditor 4) solo se usa en el admin. |
| A07 Autenticación | Validadores de contraseña de Django; bloqueo tras 5 intentos fallidos (15 min); `next` validado contra redirecciones abiertas. |
| A08 Integridad | Subidas limitadas a JPG/PNG/WebP/GIF ≤ 3 MB; dependencias fijadas por versión. |
| A09 Registro y monitoreo | Métricas de vistas y bandeja de mensajes; pendiente: registro de eventos de seguridad. |
| A10 SSRF | El servidor no descarga URLs proporcionadas por usuarios. |

## Fuera de alcance

Este es un proyecto académico/portafolio sin auditoría externa ni certificación.
