"""Estadísticas del entrenador para el perfil (sin lógica en las vistas)."""
from datetime import timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from entrenador.models import RegistroRespuesta, TemaProgreso


def racha_dias(usuario):
    """Días consecutivos con al menos una respuesta, contando desde hoy (o ayer)."""
    fechas = set(RegistroRespuesta.objects.filter(usuario=usuario)
                 .annotate(d=TruncDate('timestamp')).values_list('d', flat=True))
    dia = timezone.localdate()
    if dia not in fechas:
        dia -= timedelta(days=1)
    racha = 0
    while dia in fechas:
        racha += 1
        dia -= timedelta(days=1)
    return racha


def actividad_14_dias(usuario):
    """Lista de 14 dicts {fecha, total, correctas} para la gráfica de barras."""
    hoy = timezone.localdate()
    desde = hoy - timedelta(days=13)
    filas = (RegistroRespuesta.objects.filter(usuario=usuario, timestamp__date__gte=desde)
             .annotate(d=TruncDate('timestamp')).values('d')
             .annotate(total=Count('id'), correctas=Count('id', filter=Q(es_correcta=True))))
    por_dia = {f['d']: f for f in filas}
    maximo = max([f['total'] for f in filas] or [1])
    salida = []
    for i in range(14):
        d = desde + timedelta(days=i)
        f = por_dia.get(d, {'total': 0, 'correctas': 0})
        salida.append({'fecha': d, 'total': f['total'], 'correctas': f['correctas'],
                       'alto': round(100 * f['total'] / maximo) if maximo else 0})
    return salida


def resumen(usuario):
    regs = RegistroRespuesta.objects.filter(usuario=usuario)
    total = regs.count()
    correctas = regs.filter(es_correcta=True).count()
    progresos = list(TemaProgreso.objects.filter(usuario=usuario).select_related('tema')
                     .order_by('-dificultad_actual'))
    return {
        'total': total,
        'correctas': correctas,
        'precision': round(100 * correctas / total) if total else 0,
        'racha': racha_dias(usuario),
        'progresos': progresos,
        'dominados': sum(1 for p in progresos if p.dificultad_actual >= p.tema.dificultad_maxima),
        'actividad': actividad_14_dias(usuario),
    }
