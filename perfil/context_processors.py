from .models import ConfiguracionSitio, RedSocial


def sitio(request):
    """Disponible en todas las plantillas: {{ sitio }} y {{ redes_sociales }}."""
    try:
        return {
            'sitio': ConfiguracionSitio.actual(),
            'redes_sociales': list(RedSocial.objects.filter(activa=True)),
        }
    except Exception:  # p. ej. antes de migrar
        return {}
