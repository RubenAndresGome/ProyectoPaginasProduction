"""Tutor por reglas (sin IA externa, sin costo).

Entiende intenciones por palabras clave y responde con datos reales del usuario:
recomienda el tema con menor porcentaje de aciertos, resume su progreso y enlaza artículos."""
import unicodedata

from django.urls import reverse

TEMAS_CLAVE = {
    'aritmetica': ['aritmetica', 'suma', 'resta', 'multiplic', 'divis', 'fraccion', 'porcentaje', 'jerarquia'],
    'algebra-basica': ['algebra basica', 'ecuacion', 'despej', 'cuadratica', 'lineal', 'variable'],
    'algebra-avanzada': ['algebra avanzada', 'exponente', 'logaritmo', 'log ', 'sistema de ecuaciones', 'producto notable', 'binomio'],
    'geometria': ['geometria', 'pitagoras', 'area', 'perimetro', 'volumen', 'triangulo', 'circulo', 'angulo'],
    'trigonometria': ['trigonometria', 'seno', 'coseno', 'tangente', 'radian'],
    'conjuntos': ['conjunto', 'union', 'interseccion', 'venn', 'complemento'],
    'silogismos': ['silogismo', 'premisa', 'logica', 'deduc'],
}
SUGERENCIAS = ['¿Qué tema practico?', '¿Cómo voy?', 'Explícame Pitágoras', 'Hablar con Rubén']


def normalizar(t):
    t = unicodedata.normalize('NFKD', (t or '').lower())
    return ''.join(c for c in t if not unicodedata.combining(c)) + ' '


def _tiene(t, *palabras):
    return any(p in t for p in palabras)


def _link(texto, url):
    return {'texto': texto, 'url': url}


def _tema_por_texto(t):
    from entrenador.models import Tema
    for slug, claves in TEMAS_CLAVE.items():
        if _tiene(t, *claves):
            return Tema.objects.filter(slug=slug, activo=True).first()
    return None


def _articulo_relacionado(palabra):
    """Busca ignorando acentos y mayúsculas (SQLite no lo hace por sí solo)."""
    from blog.models import Articulo_Page
    clave = normalizar(palabra).strip()
    if not clave:
        return None
    for a in Articulo_Page.objects.filter(publicado=True).prefetch_related('bloques')[:300]:
        texto = a.title + ' ' + ' '.join(b.texto_plano() for b in a.bloques.all())
        if clave in normalizar(texto):
            return a
    return None


def _recomendar(usuario):
    from entrenador.models import Tema, TemaProgreso
    if not usuario.is_authenticated:
        t = Tema.objects.filter(activo=True).order_by('orden').first()
        return {'texto': 'Te recomiendo empezar por lo básico. Si creas una cuenta, guardo tu progreso y te recomiendo según tus errores.',
                'enlaces': [_link(f'Practicar {t.nombre}', reverse('entrenador:practicar_tema', args=[t.slug]))] if t else [],
                'sugerencias': ['Crear cuenta', '¿Qué es el entrenador?']}
    progresos = list(TemaProgreso.objects.filter(usuario=usuario, total_intentos__gte=3).select_related('tema'))
    practicados = {p.tema_id for p in TemaProgreso.objects.filter(usuario=usuario)}
    if progresos:
        debil = min(progresos, key=lambda p: (p.porcentaje_acierto, p.dificultad_actual))
        if debil.porcentaje_acierto < 70:
            return {'texto': f'Tu punto débil ahora es {debil.tema.nombre}: llevas {debil.porcentaje_acierto}% de aciertos en '
                             f'{debil.total_intentos} intentos (nivel {debil.dificultad_actual}). Practica ahí unos minutos.',
                    'enlaces': [_link(f'Practicar {debil.tema.nombre}', reverse('entrenador:practicar_tema', args=[debil.tema.slug]))],
                    'sugerencias': ['¿Cómo voy?', 'Explícame este tema']}
    nuevo = Tema.objects.filter(activo=True).exclude(id__in=practicados).order_by('orden').first()
    if nuevo:
        return {'texto': f'¡Vas bien en lo que has practicado! Te falta probar {nuevo.nombre}.',
                'enlaces': [_link(f'Empezar {nuevo.nombre}', reverse('entrenador:practicar_tema', args=[nuevo.slug]))],
                'sugerencias': ['¿Cómo voy?']}
    return {'texto': 'Ya practicaste todos los temas. Sigue subiendo de nivel donde tengas menos aciertos.',
            'enlaces': [_link('Ver mi progreso', reverse('perfil:mi_perfil'))], 'sugerencias': []}


def _progreso(usuario):
    if not usuario.is_authenticated:
        return {'texto': 'Para ver tu progreso necesitas iniciar sesión.',
                'enlaces': [_link('Iniciar sesión', reverse('log_and_reg:login'))], 'sugerencias': SUGERENCIAS[:1]}
    from perfil.servicios import resumen
    s = resumen(usuario)
    if not s['total']:
        return {'texto': 'Aún no tienes ejercicios resueltos. ¡Empieza hoy y arranca tu racha!',
                'enlaces': [_link('Elegir tema', reverse('entrenador:inicio'))], 'sugerencias': ['¿Qué tema practico?']}
    return {'texto': f"Llevas {s['total']} ejercicios con {s['precision']}% de precisión, racha de {s['racha']} "
                     f"día{'s' if s['racha'] != 1 else ''} y {s['dominados']} tema(s) dominado(s).",
            'enlaces': [_link('Ver mi perfil', reverse('perfil:mi_perfil'))], 'sugerencias': ['¿Qué tema practico?']}


def responder(texto, usuario):
    t = normalizar(texto)
    if not t.strip():
        return {'texto': 'Escríbeme algo 🙂', 'enlaces': [], 'sugerencias': SUGERENCIAS}
    if _tiene(t, 'hola', 'buenas', 'hey', 'saludos') and len(t) < 25:
        nombre = f', {usuario.first_name or usuario.username}' if usuario.is_authenticated else ''
        return {'texto': f'¡Hola{nombre}! Soy el tutor de MathMaster. Te ayudo a decidir qué practicar y a encontrar explicaciones.',
                'enlaces': [], 'sugerencias': SUGERENCIAS}
    if _tiene(t, 'como voy', 'mi progreso', 'estadistic', 'racha', 'mis resultados'):
        return _progreso(usuario)
    if _tiene(t, 'que practico', 'que tema', 'recomienda', 'recomiendas', 'debil', 'que estudio', 'por donde empiezo'):
        return _recomendar(usuario)
    if _tiene(t, 'ruben', 'contacto', 'humano', 'persona', 'hablar con', 'whatsapp', 'correo'):
        return {'texto': 'Puedes dejarle un mensaje a Rubén desde la página de contacto; te responde por ahí o por WhatsApp.',
                'enlaces': [_link('Ir a contacto', reverse('mainapp:contacto'))], 'sugerencias': []}
    if _tiene(t, 'crear cuenta', 'registr'):
        return {'texto': 'Crear cuenta es gratis y guarda tu progreso.', 'enlaces': [_link('Crear cuenta', reverse('log_and_reg:register'))], 'sugerencias': []}
    if _tiene(t, 'entrenador', 'como funciona', 'que es esto'):
        return {'texto': 'El entrenador genera ejercicios al azar. Con 3 aciertos seguidos sube la dificultad; si fallas, '
                         'te muestra la explicación paso a paso.', 'enlaces': [_link('Probarlo', reverse('entrenador:inicio'))],
                'sugerencias': ['¿Qué tema practico?']}
    tema = _tema_por_texto(t)
    if tema:
        enlaces = [_link(f'Practicar {tema.nombre}', reverse('entrenador:practicar_tema', args=[tema.slug]))]
        palabra = next((p.strip() for p in TEMAS_CLAVE.get(tema.slug, []) if p in t), tema.nombre)
        art = _articulo_relacionado(palabra) or _articulo_relacionado(tema.nombre.split()[0])
        if art:
            enlaces.insert(0, _link(f'Leer: {art.title}', reverse('blog:detalle_publicacion', args=[art.id])))
        return {'texto': f'Eso es de {tema.nombre}. {tema.descripcion}'.strip(), 'enlaces': enlaces,
                'sugerencias': ['¿Qué tema practico?']}
    if _tiene(t, 'gracias', 'thanks'):
        return {'texto': '¡Con gusto! Sigue practicando 💪', 'enlaces': [], 'sugerencias': []}
    return {'texto': 'No estoy seguro de entenderte. Puedo recomendarte qué practicar, decirte cómo vas o buscar '
                     'explicaciones de un tema (por ejemplo: "ecuaciones", "Pitágoras", "logaritmos").',
            'enlaces': [], 'sugerencias': SUGERENCIAS}
