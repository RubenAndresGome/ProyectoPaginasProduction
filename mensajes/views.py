import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import bot
from .forms import ContactoForm, RespuestaForm
from .models import Mensaje

MAX_POR_HORA = 3


def _limite_superado(request):
    """Máximo MAX_POR_HORA mensajes por sesión cada hora (anti-spam simple)."""
    ahora = timezone.now().timestamp()
    envios = [t for t in request.session.get('envios_contacto', []) if ahora - t < 3600]
    request.session['envios_contacto'] = envios
    return len(envios) >= MAX_POR_HORA


@require_POST
def enviar(request):
    form = ContactoForm(request.POST)
    if _limite_superado(request):
        messages.error(request, 'Enviaste varios mensajes seguidos. Intenta de nuevo en una hora o escribe por WhatsApp.')
        return redirect('mainapp:contacto')
    if form.is_valid():
        if not form.es_spam():
            m = form.save(commit=False)
            if request.user.is_authenticated:
                m.usuario = request.user
            m.save()
            request.session['envios_contacto'] = request.session['envios_contacto'] + [timezone.now().timestamp()]
        messages.success(request, 'Mensaje enviado. Te responderé lo antes posible.')
        return redirect('mainapp:contacto')
    request.session['contacto_errores'] = {'datos': request.POST.dict(), 'errores': form.errors.get_json_data()}
    messages.error(request, 'Revisa los campos del formulario.')
    return redirect('mainapp:contacto')


@login_required(login_url='log_and_reg:login')
def mis_mensajes(request):
    return render(request, 'mensajes/mis_mensajes.html',
                  {'mensajes_usuario': Mensaje.objects.filter(usuario=request.user)})


@staff_member_required
def bandeja(request):
    filtro = request.GET.get('f', 'todos')
    qs = Mensaje.objects.select_related('usuario')
    if filtro == 'sin_leer':
        qs = qs.filter(leido=False)
    elif filtro == 'pendientes':
        qs = qs.filter(respuesta='')
    return render(request, 'mensajes/bandeja.html', {'lista': qs, 'filtro': filtro})


@staff_member_required
def detalle(request, id):
    m = get_object_or_404(Mensaje, id=id)
    if not m.leido:
        m.leido = True
        m.save(update_fields=['leido'])
    form = RespuestaForm(request.POST or None, initial={'respuesta': m.respuesta})
    if request.method == 'POST':
        if request.POST.get('accion') == 'no_leido':
            Mensaje.objects.filter(id=id).update(leido=False)
            return redirect('mensajes:bandeja')
        if request.POST.get('accion') == 'eliminar':
            m.delete()
            messages.success(request, 'Mensaje eliminado.')
            return redirect('mensajes:bandeja')
        if form.is_valid():
            m.respuesta = form.cleaned_data['respuesta']
            m.respondido_en = timezone.now()
            m.save()
            messages.success(request, 'Respuesta guardada.' + (' El usuario la verá en «Mis mensajes».' if m.usuario_id else ''))
            return redirect('mensajes:detalle', id=id)
    return render(request, 'mensajes/detalle.html', {'m': m, 'form': form})


@require_POST
def bot_responder(request):
    try:
        texto = str(json.loads(request.body or b'{}').get('texto', ''))[:300]
    except ValueError:
        texto = ''
    return JsonResponse(bot.responder(texto, request.user))
