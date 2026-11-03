from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import redirect, render

from . import servicios
from .forms import ConfiguracionForm, PerfilForm, RedesFormSet, UsuarioForm
from .models import ConfiguracionSitio, Perfil, RedSocial


@login_required(login_url='log_and_reg:login')
def mi_perfil(request):
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    seccion = request.POST.get('seccion') if request.method == 'POST' else None

    f_usuario = UsuarioForm(request.POST if seccion == 'perfil' else None, instance=request.user)
    f_perfil = PerfilForm(request.POST if seccion == 'perfil' else None,
                          request.FILES if seccion == 'perfil' else None, instance=perfil)
    f_sitio = f_redes = None
    if request.user.is_staff:
        config = ConfiguracionSitio.actual()
        f_sitio = ConfiguracionForm(request.POST if seccion == 'sitio' else None, instance=config)
        f_redes = RedesFormSet(request.POST if seccion == 'sitio' else None,
                               queryset=RedSocial.objects.all(), prefix='redes')

    if seccion == 'perfil':
        if f_usuario.is_valid() and f_perfil.is_valid():
            with transaction.atomic():
                f_usuario.save()
                f_perfil.save()
            messages.success(request, 'Perfil actualizado.')
            return redirect('perfil:mi_perfil')
        messages.error(request, 'Revisa los campos marcados.')
    elif seccion == 'sitio':
        if not request.user.is_staff:
            raise PermissionDenied
        if f_sitio.is_valid() and f_redes.is_valid():
            with transaction.atomic():
                f_sitio.save()
                f_redes.save()
            messages.success(request, 'Configuración del sitio guardada. Ya se ve en el pie de página.')
            return redirect('/perfil/#sitio')
        messages.error(request, 'Revisa los campos de la configuración del sitio.')

    return render(request, 'perfil/mi_perfil.html', {
        'perfil': perfil, 'stats': servicios.resumen(request.user),
        'f_usuario': f_usuario, 'f_perfil': f_perfil, 'f_sitio': f_sitio, 'f_redes': f_redes,
        'abrir_sitio': seccion == 'sitio',
    })
