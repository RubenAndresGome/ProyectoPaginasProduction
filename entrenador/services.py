import random
from django.utils import timezone
from .models import Tema, Pregunta, OpcionRespuesta, RegistroRespuesta, TemaProgreso
from .generators import GENERADORES_MAP

class MotorAdaptativo:
    def __init__(self, usuario, tema=None):
        self.usuario = usuario
        self.tema = tema

    def obtener_o_crear_progreso(self, tema):
        progreso, created = TemaProgreso.objects.get_or_create(
            usuario=self.usuario,
            tema=tema,
            defaults={
                'dificultad_actual': tema.dificultad_minima,
                'aciertos_consecutivos': 0,
                'fallos_consecutivos': 0,
                'total_aciertos': 0,
                'total_intentos': 0
            }
        )
        return progreso

    def generar_pregunta_adaptativa(self) -> Pregunta:
        # Si no hay tema seleccionado, elegir uno activo al azar
        tema_activo = self.tema
        if not tema_activo:
            temas_activos = Tema.objects.filter(activo=True)
            if not temas_activos.exists():
                raise ValueError("No hay temas activos disponibles en el sistema.")
            tema_activo = random.choice(temas_activos)

        # Obtener progreso del usuario para este tema
        progreso = self.obtener_o_crear_progreso(tema_activo)
        dificultad = progreso.dificultad_actual

        # Obtener generador correspondiente
        generator_class = GENERADORES_MAP.get(tema_activo.categoria)
        if not generator_class:
            raise ValueError(f"No hay generador implementado para la categoría '{tema_activo.categoria}'.")

        generator = generator_class(dificultad=dificultad, max_dificultad=tema_activo.dificultad_maxima)
        pg = generator.generar()

        # Guardar pregunta generada en la base de datos
        pregunta = Pregunta.objects.create(
            tema=tema_activo,
            enunciado_latex=pg.enunciado_latex,
            tipo_respuesta=pg.tipo_respuesta,
            respuesta_numerica=pg.respuesta_numerica,
            tolerancia=pg.tolerancia,
            dificultad=pg.dificultad,
            parametros_json=pg.parametros,
            explicacion_latex=pg.explicacion_latex
        )

        # Si tiene opciones (opción múltiple), guardarlas
        if pg.opciones:
            for opt in pg.opciones:
                OpcionRespuesta.objects.create(
                    pregunta=pregunta,
                    texto=opt['texto'],
                    texto_latex=opt.get('texto_latex', ''),
                    es_correcta=opt['es_correcta'],
                    orden=opt['orden']
                )

        return pregunta

    def evaluar_y_registrar(self, pregunta: Pregunta, respuesta_usuario: str, tiempo_segundos: float = None) -> bool:
        # Evaluar corrección de la respuesta
        correcto = False
        respuesta_limpia = respuesta_usuario.strip()

        if pregunta.tipo_respuesta == 'numerica':
            try:
                val = float(respuesta_limpia.replace(',', '.'))
                correcto = abs(val - pregunta.respuesta_numerica) <= pregunta.tolerancia
            except (ValueError, TypeError):
                correcto = False
        elif pregunta.tipo_respuesta in ['opcion_multiple', 'seleccion_multiple']:
            # Comprobar si la respuesta coincide con alguna de las opciones correctas
            # Puede ser por el ID de la opción (si se envía el ID) o por el texto exacto
            opciones_correctas = pregunta.opciones.filter(es_correcta=True)
            
            # Buscar por ID
            if respuesta_limpia.isdigit():
                if opciones_correctas.filter(id=int(respuesta_limpia)).exists():
                    correcto = True
            
            # O buscar por coincidencia exacta de texto / texto latex
            if not correcto:
                for opt in opciones_correctas:
                    if opt.texto.strip() == respuesta_limpia or opt.texto_latex.strip() == respuesta_limpia:
                        correcto = True
                        break
        else:
            # En caso de texto_libre u otros
            opcion_correcta = pregunta.opciones.filter(es_correcta=True).first()
            if opcion_correcta and opcion_correcta.texto.strip().lower() == respuesta_limpia.lower():
                correcto = True

        # Crear registro de la respuesta
        RegistroRespuesta.objects.create(
            usuario=self.usuario,
            pregunta=pregunta,
            respuesta_dada=respuesta_usuario,
            es_correcta=correcto,
            tiempo_segundos=tiempo_segundos
        )

        # Actualizar progreso y dificultad adaptativa
        progreso = self.obtener_o_crear_progreso(pregunta.tema)
        progreso.total_intentos += 1
        progreso.ultima_practica = timezone.now()

        if correcto:
            progreso.total_aciertos += 1
            progreso.aciertos_consecutivos += 1
            progreso.fallos_consecutivos = 0

            # Subir dificultad tras 3 aciertos consecutivos
            if progreso.aciertos_consecutivos >= 3:
                if progreso.dificultad_actual < pregunta.tema.dificultad_maxima:
                    progreso.dificultad_actual += 1
                progreso.aciertos_consecutivos = 0  # Reiniciar racha para el nuevo nivel
        else:
            progreso.fallos_consecutivos += 1
            progreso.aciertos_consecutivos = 0

            # Bajar dificultad tras 2 fallos consecutivos
            if progreso.fallos_consecutivos >= 2:
                if progreso.dificultad_actual > pregunta.tema.dificultad_minima:
                    progreso.dificultad_actual -= 1
                progreso.fallos_consecutivos = 0  # Reiniciar fallos

        progreso.save()
        return correcto
