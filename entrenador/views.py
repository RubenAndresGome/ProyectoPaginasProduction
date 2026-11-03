from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q, Sum, Avg
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils import timezone
from datetime import timedelta

from .models import Tema, Pregunta, OpcionRespuesta, RegistroRespuesta, TemaProgreso
from .services import MotorAdaptativo

def calcular_racha(usuario):
    """Calcula la racha de días consecutivos practicando del usuario."""
    intentos = RegistroRespuesta.objects.filter(usuario=usuario).values_list('timestamp', flat=True).order_by('-timestamp')
    if not intentos:
        return 0
        
    fechas_set = {timezone.localdate(f) for f in intentos}
    hoy = timezone.localdate()
    racha = 0
    dia = hoy
    
    if dia in fechas_set:
        racha += 1
        dia -= timedelta(days=1)
        while dia in fechas_set:
            racha += 1
            dia -= timedelta(days=1)
    elif (dia - timedelta(days=1)) in fechas_set:
        # La racha cuenta si ayer se practicó aunque hoy todavía no
        dia -= timedelta(days=1)
        while dia in fechas_set:
            racha += 1
            dia -= timedelta(days=1)
            
    return racha

def calcular_xp_y_rango(usuario):
    """Calcula de forma simulada la XP total y el rango según los aciertos."""
    aciertos = RegistroRespuesta.objects.filter(usuario=usuario, es_correcta=True).count()
    xp = aciertos * 150 + 200  # 150 XP por acierto, base de 200 XP
    
    if xp >= 5000:
        rango = 'SSS'
    elif xp >= 3000:
        rango = 'SS'
    elif xp >= 1500:
        rango = 'S'
    elif xp >= 800:
        rango = 'A'
    elif xp >= 400:
        rango = 'B'
    else:
        rango = 'C'
        
    return xp, rango


COLORES_TEMA = {
    'aritmetica':        {'gradient': 'linear-gradient(135deg, #10b981, #059669)', 'desc': '#a7f3d0', 'badge_bg': 'rgba(16,185,129,0.12)', 'badge_text': '#34d399', 'glow': '16,185,129'},
    'geometria':         {'gradient': 'linear-gradient(135deg, #3b82f6, #2563eb)', 'desc': '#bfdbfe', 'badge_bg': 'rgba(59,130,246,0.12)', 'badge_text': '#60a5fa', 'glow': '59,130,246'},
    'trigonometria':     {'gradient': 'linear-gradient(135deg, #d946ef, #c026d3)', 'desc': '#f5d0fe', 'badge_bg': 'rgba(217,70,239,0.12)', 'badge_text': '#e879f9', 'glow': '217,70,239'},
    'algebra_basica':    {'gradient': 'linear-gradient(135deg, #f97316, #ea580c)', 'desc': '#fed7aa', 'badge_bg': 'rgba(249,115,22,0.12)', 'badge_text': '#fb923c', 'glow': '249,115,22'},
    'algebra_avanzada':  {'gradient': 'linear-gradient(135deg, #a855f7, #9333ea)', 'desc': '#e9d5ff', 'badge_bg': 'rgba(168,85,247,0.12)', 'badge_text': '#c084fc', 'glow': '168,85,247'},
    'conjuntos':         {'gradient': 'linear-gradient(135deg, #06b6d4, #0891b2)', 'desc': '#a5f3fc', 'badge_bg': 'rgba(6,182,212,0.12)',  'badge_text': '#22d3ee', 'glow': '6,182,212'},
    'silogismos':        {'gradient': 'linear-gradient(135deg, #14b8a6, #0d9488)', 'desc': '#99f6e4', 'badge_bg': 'rgba(20,184,166,0.12)', 'badge_text': '#2dd4bf', 'glow': '20,184,166'},
}

@login_required(login_url='log_and_reg:login')
def seleccionar_tema(request):
    """Página para elegir un tema antes de practicar"""
    temas = list(Tema.objects.filter(activo=True))
    
    # Asociar el progreso correspondiente de cada tema para el usuario actual
    progresos_dict = {p.tema_id: p for p in TemaProgreso.objects.filter(usuario=request.user)}
    fallback = COLORES_TEMA['aritmetica']
    max_intentos = -1
    tema_destacado = None
    
    for tema in temas:
        tema.progreso = progresos_dict.get(tema.id)
        color_info = COLORES_TEMA.get(tema.categoria, fallback)
        tema.gradient = color_info['gradient']
        tema.desc_color = color_info['desc']
        tema.badge_bg = color_info['badge_bg']
        tema.badge_text = color_info['badge_text']
        tema.glow_color = color_info['glow']
        # Detectar el tema con más progreso para bento grid featured
        if tema.progreso and tema.progreso.total_intentos > max_intentos:
            max_intentos = tema.progreso.total_intentos
            tema_destacado = tema
    
    for tema in temas:
        tema.es_destacado = (tema == tema_destacado)
        
    racha_dias = calcular_racha(request.user)
    xp, rango = calcular_xp_y_rango(request.user)
    
    context = {
        'temas': temas,
        'racha_dias': racha_dias,
        'rango': rango,
        'xp': xp
    }
    return render(request, 'entrenador/seleccionar_tema.html', context)


@login_required(login_url='log_and_reg:login')
def practicar(request, slug=None):
    """Vista principal del ejercicio adaptativo"""
    tema = None
    if slug:
        tema = get_object_or_404(Tema, slug=slug, activo=True)

    # 1. Procesamiento de POST (Respuesta enviada)
    if request.method == 'POST':
        pregunta_id = request.session.get('pregunta_id')
        if not pregunta_id:
            # Si expira la sesión de la pregunta, redirigir a seleccionar
            return redirect('entrenador:inicio')

        pregunta = get_object_or_404(Pregunta, id=pregunta_id)
        respuesta_usuario = request.POST.get('respuesta', '').strip()
        
        tiempo_segundos = None
        try:
            tiempo_val = request.POST.get('tiempo_segundos')
            if tiempo_val:
                tiempo_segundos = float(tiempo_val)
        except (TypeError, ValueError):
            pass

        motor = MotorAdaptativo(request.user, pregunta.tema)
        correcto = motor.evaluar_y_registrar(pregunta, respuesta_usuario, tiempo_segundos=tiempo_segundos)
        
        # Limpiar la pregunta actual de la sesión
        del request.session['pregunta_id']

        # Mensajes de feedback con el resultado
        if correcto:
            mensaje = "✅ ¡Correcto! Excelente deducción."
        else:
            if pregunta.tipo_respuesta == 'numerica':
                mensaje = f"❌ Incorrecto. La respuesta correcta era: {pregunta.respuesta_numerica}"
            else:
                op_correcta = pregunta.opciones.filter(es_correcta=True).first()
                correcta_texto = op_correcta.texto if op_correcta else "Desconocido"
                mensaje = f"❌ Incorrecto. La opción correcta era: {correcta_texto}"

        # Obtener la opción correcta en caso de que sea opción múltiple para mostrar en el resultado
        opcion_correcta = None
        if pregunta.tipo_respuesta in ['opcion_multiple', 'seleccion_multiple']:
            opcion_correcta = pregunta.opciones.filter(es_correcta=True).first()

        return render(request, 'entrenador/resultado.html', {
            'mensaje': mensaje,
            'correcto': correcto,
            'pregunta': pregunta,
            'opcion_correcta': opcion_correcta,
            'respuesta_dada': respuesta_usuario,
            'tema': pregunta.tema,
        })

    # 2. Procesamiento de GET (Carga o regeneración del ejercicio)
    try:
        motor = MotorAdaptativo(request.user, tema)
        pregunta = motor.generar_pregunta_adaptativa()
        request.session['pregunta_id'] = pregunta.id
    except ValueError as e:
        return HttpResponse(f"<h1>Error de Configuración</h1><p>{str(e)}</p>")

    return render(request, 'entrenador/practicar.html', {
        'pregunta': pregunta,
        'tema': pregunta.tema,
    })


@login_required(login_url='log_and_reg:login')
def historial(request):
    """Historial de intentos del usuario autenticado"""
    intentos = RegistroRespuesta.objects.filter(usuario=request.user).select_related('pregunta__tema').order_by('-timestamp')[:50]
    return render(request, 'entrenador/historial.html', {'intentos': intentos})


@staff_member_required
def dashboard(request):
    """Dashboard analítico avanzado solo para docentes/admin"""
    # 1. Filtros Reactivos
    tema_filtrado = request.GET.get('tema')
    rango_fechas = request.GET.get('fecha', 'todos')
    
    qs_intentos = RegistroRespuesta.objects.all()
    
    if tema_filtrado:
        qs_intentos = qs_intentos.filter(pregunta__tema_id=tema_filtrado)
        
    if rango_fechas == 'hoy':
        qs_intentos = qs_intentos.filter(timestamp__date=timezone.localdate())
    elif rango_fechas == 'semana':
        hace_una_semana = timezone.now() - timedelta(days=7)
        qs_intentos = qs_intentos.filter(timestamp__gte=hace_una_semana)
    elif rango_fechas == 'mes':
        hace_un_mes = timezone.now() - timedelta(days=30)
        qs_intentos = qs_intentos.filter(timestamp__gte=hace_un_mes)

    # 2. Métricas Generales (Afectadas por filtros)
    total_estudiantes = qs_intentos.values('usuario').distinct().count()
    total_intentos = qs_intentos.count()
    correctos = qs_intentos.filter(es_correcta=True).count()
    porcentaje = (correctos / total_intentos * 100) if total_intentos else 0
    
    # 3. Métricas de Tiempo y Frustración
    tiempo_promedio = qs_intentos.filter(tiempo_segundos__isnull=False).aggregate(avg_time=Avg('tiempo_segundos'))['avg_time'] or 0
    
    # 4. Clase Activa (LED - últimos 5 minutos)
    hace_5_minutos = timezone.now() - timedelta(minutes=5)
    estudiantes_activos_5m = RegistroRespuesta.objects.filter(timestamp__gte=hace_5_minutos).values('usuario').distinct().count()
    clase_activa = estudiantes_activos_5m > 0

    # 5. Agrupar estadísticas de desempeño por estudiante (top 10 por intentos)
    datos_estudiantes = (
        qs_intentos.values('usuario', 'usuario__username')
        .annotate(
            correctos=Count('id', filter=Q(es_correcta=True)),
            incorrectos=Count('id', filter=Q(es_correcta=False)),
            total=Count('id')
        )
        .order_by('-total')[:10]
    )

    nombres = [e['usuario__username'] for e in datos_estudiantes]
    correctos_list = [e['correctos'] for e in datos_estudiantes]
    incorrectos_list = [e['incorrectos'] for e in datos_estudiantes]
    usuarios_top_ids = [e['usuario'] for e in datos_estudiantes]

    # 6. Alertas Tempranas (Últimos 15 intentos por alumno)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    alertas = []
    
    # Analizamos los usuarios que están activos en el filtro
    usuarios_activos = User.objects.filter(id__in=qs_intentos.values('usuario')).distinct()
    for u in usuarios_activos:
        ultimos_15 = RegistroRespuesta.objects.filter(usuario=u).order_by('-timestamp')[:15]
        tot = ultimos_15.count()
        if tot > 0:
            corr_15 = sum(1 for r in ultimos_15 if r.es_correcta)
            porc_15 = (corr_15 / tot) * 100
            racha_actual = calcular_racha(u)
            
            if porc_15 < 40 or racha_actual == 0:
                alertas.append({
                    'id': u.id,
                    'username': u.username,
                    'porcentaje_15': round(porc_15, 1),
                    'total_15': tot,
                    'racha': racha_actual,
                    'razon': 'Tasa de acierto crítica (<40%)' if porc_15 < 40 else 'Racha de días inactiva'
                })
    # Limitar a top 5 alertas más urgentes (tasa de acierto más baja)
    alertas = sorted(alertas, key=lambda x: x['porcentaje_15'])[:5]

    # 7. Criptonita Académica (Error Heatmap por Categorías de Tema)
    errores_por_categoria = (
        qs_intentos.values('pregunta__tema__categoria')
        .annotate(
            total=Count('id'),
            incorrectos=Count('id', filter=Q(es_correcta=False))
        )
    )
    
    categorias_map = dict(Tema.CATEGORIAS)
    heatmap_labels = []
    heatmap_data = []
    for item in errores_por_categoria:
        cat_code = item['pregunta__tema__categoria']
        cat_name = categorias_map.get(cat_code, cat_code.capitalize())
        tot_cat = item['total']
        inc_cat = item['incorrectos']
        tasa_error = (inc_cat / tot_cat * 100) if tot_cat > 0 else 0
        heatmap_labels.append(cat_name)
        heatmap_data.append(round(tasa_error, 1))

    # 8. Distribución del Motor Adaptativo
    # Contamos la cantidad de registros en TemaProgreso por nivel de dificultad actual
    progresos = TemaProgreso.objects.all()
    if tema_filtrado:
        progresos = progresos.filter(tema_id=tema_filtrado)
        
    basico = progresos.filter(dificultad_actual__lte=3).count()
    medio = progresos.filter(dificultad_actual__gt=3, dificultad_actual__lte=7).count()
    avanzado = progresos.filter(dificultad_actual__gt=7).count()
    
    distribucion_motor = [basico, medio, avanzado]

    # Para el dropdown de temas en los filtros
    todos_temas = Tema.objects.filter(activo=True).order_by('nombre')

    context = {
        # Filtros
        'todos_temas': todos_temas,
        'tema_filtrado': int(tema_filtrado) if tema_filtrado else None,
        'rango_fechas': rango_fechas,
        # Estadísticas principales
        'total_estudiantes': total_estudiantes,
        'total_intentos': total_intentos,
        'porcentaje_acierto': round(porcentaje, 1),
        'tiempo_promedio': round(tiempo_promedio, 1),
        'clase_activa': clase_activa,
        'estudiantes_activos_5m': estudiantes_activos_5m,
        # Alertas Tempranas
        'alertas': alertas,
        # Gráfico 1: Desempeño por estudiante
        'nombres': nombres,
        'correctos_list': correctos_list,
        'incorrectos_list': incorrectos_list,
        'datos_estudiantes': datos_estudiantes, # Para la tabla del bento grid
        # Gráfico 2: Radar Error Heatmap
        'heatmap_labels': heatmap_labels,
        'heatmap_data': heatmap_data,
        # Gráfico 3: Doughnut Distribución Adaptativa
        'distribucion_motor': distribucion_motor,
    }
    return render(request, 'entrenador/dashboard.html', context)


@staff_member_required
def detalle_estudiante_ajax(request, user_id):
    """Retorna la ficha analítica de un estudiante individual vía AJAX"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    estudiante = get_object_or_404(User, id=user_id)
    
    # Calcular métricas individuales
    total_intentos = RegistroRespuesta.objects.filter(usuario=estudiante).count()
    correctos = RegistroRespuesta.objects.filter(usuario=estudiante, es_correcta=True).count()
    porcentaje = (correctos / total_intentos * 100) if total_intentos else 0
    
    racha = calcular_racha(estudiante)
    xp, rango = calcular_xp_y_rango(estudiante)
    
    # Últimos 10 intentos detallados
    ultimos_intentos = RegistroRespuesta.objects.filter(usuario=estudiante).select_related('pregunta__tema').order_by('-timestamp')[:10]
    
    # Progreso por temas
    progresos_temas = TemaProgreso.objects.filter(usuario=estudiante).select_related('tema')
    
    # Mapeo de categorías para labels legibles
    categorias_map = dict(Tema.CATEGORIAS)
    for p in progresos_temas:
        p.tema.categoria_label = categorias_map.get(p.tema.categoria, p.tema.categoria.capitalize())
    
    context = {
        'estudiante': estudiante,
        'total_intentos': total_intentos,
        'porcentaje_acierto': round(porcentaje, 1),
        'racha': racha,
        'xp': xp,
        'rango': rango,
        'ultimos_intentos': ultimos_intentos,
        'progresos_temas': progresos_temas,
    }
    return render(request, 'entrenador/partials/ficha_estudiante.html', context)

