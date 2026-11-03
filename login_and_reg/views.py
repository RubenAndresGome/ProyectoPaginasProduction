from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.cache import cache
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST


def _clave_intentos(request, usuario):
    ip = request.META.get('REMOTE_ADDR', '')
    return f'login-fallos:{ip}:{(usuario or "").lower()[:150]}'


def _destino_seguro(request):
    """Respeta ?next= solo si apunta a este mismo sitio (evita redirecciones abiertas)."""
    destino = request.POST.get('next') or request.GET.get('next')
    if destino and url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()},
                                                   require_https=request.is_secure()):
        return destino
    return 'mainapp:inicio'

def register_page(request):
    if request.method == 'POST':
        register_form = UserCreationForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            messages.success(request, 'Te has registrado correctamente. ¡Ahora puedes iniciar sesión!')
            return redirect('mainapp:inicio')
    else:
        register_form = UserCreationForm()

    # Agregar clases CSS a todos los campos del formulario
    for field in register_form.fields.values():
        field.widget.attrs.update({
            # Actualizado a bordes más sutiles y anillo índigo
            'class': 'w-full rounded-lg border-slate-300 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 py-2.5 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors'
        })

    return render(request, 'users/registro.html', {
        'title': 'Registro de Usuario',
        'register_form': register_form
    })


def login_page(request):
    if request.user.is_authenticated:
        return redirect('mainapp:inicio')
    if request.method == 'POST':
        clave = _clave_intentos(request, request.POST.get('username'))
        if cache.get(clave, 0) >= settings.LOGIN_MAX_INTENTOS:
            minutos = settings.LOGIN_BLOQUEO_SEGUNDOS // 60
            messages.error(request, f'Demasiados intentos fallidos. Espera {minutos} minutos e inténtalo de nuevo.')
            login_form = AuthenticationForm(request)
        else:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                cache.delete(clave)
                messages.success(request, f'Bienvenido de nuevo, {user.get_username()}.')
                return redirect(_destino_seguro(request))
            cache.set(clave, cache.get(clave, 0) + 1, settings.LOGIN_BLOQUEO_SEGUNDOS)
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        login_form = AuthenticationForm()

    # Agregar clases CSS a todos los campos del formulario
    for field in login_form.fields.values():
        field.widget.attrs.update({
            # Actualizado a bordes más sutiles y anillo índigo
            'class': 'w-full rounded-lg border-slate-300 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 py-2.5 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors'
        })

    return render(request, 'users/login.html', {
        'title': 'Iniciar Sesión',
        'login_form': login_form
    })
@require_POST
def logout_user(request):
    """Solo por POST + CSRF: un enlace externo no puede cerrar tu sesión."""
    logout(request)
    messages.success(request, 'Sesión cerrada.')
    return redirect('mainapp:inicio')
