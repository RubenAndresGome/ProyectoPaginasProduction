"""Crea/actualiza el superusuario de PRUEBA 'admin' / '1234'.
Solo se ejecuta con DEBUG=True (nunca en produccion).
Uso: .venv\Scripts\python.exe manage.py shell -c "exec(open('scripts/crear_admin_local.py', encoding='utf-8').read())"
"""
from django.conf import settings
from django.contrib.auth import get_user_model

if not settings.DEBUG:
    print("[SKIP] DEBUG=False: no se crea el admin de prueba.")
else:
    User = get_user_model()
    u, creado = User.objects.get_or_create(username="admin", defaults={"email": "admin@local.test"})
    u.is_staff = u.is_superuser = u.is_active = True
    u.set_password("1234")  # set_password omite los validadores: valido solo en local
    u.save()
    print(f"[OK] Admin de prueba {'creado' if creado else 'actualizado'}: admin / 1234  ->  http://127.0.0.1:8000/admin/")
