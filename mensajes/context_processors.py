def no_leidos(request):
    if getattr(request, 'user', None) and request.user.is_staff:
        from .models import Mensaje
        return {'mensajes_no_leidos': Mensaje.objects.filter(leido=False).count()}
    return {}
