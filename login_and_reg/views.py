from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

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
        login_form = AuthenticationForm(request, data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido de nuevo, {username}!')
                return redirect('mainapp:inicio')
            else:
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
@login_required()
def logout_user(request):
        logout(request)
        return redirect('mainapp:inicio')
