from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Tema(models.Model):
    CATEGORIAS = [
        ('aritmetica', 'Aritmética'),
        ('geometria', 'Geometría'),
        ('trigonometria', 'Trigonometría'),
        ('algebra_basica', 'Álgebra Básica'),
        ('algebra_avanzada', 'Álgebra Avanzada'),
        ('conjuntos', 'Lógica de Conjuntos'),
        ('silogismos', 'Silogismos'),
    ]

    nombre = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True, max_length=80, blank=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='aritmetica')
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=50, blank=True, default='shapes', help_text="Clase FontAwesome del ícono (ej: shapes)")
    icono_svg = models.TextField(blank=True, help_text="SVG inline del ícono")
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    # Niveles de dificultad que este tema soporta
    dificultad_minima = models.PositiveIntegerField(default=1)
    dificultad_maxima = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = "Tema"
        verbose_name_plural = "Temas"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Pregunta(models.Model):
    """
    Almacena cada pregunta generada para:
    - Historial del alumno
    - Evitar repetición reciente
    """
    TIPO_RESPUESTA = [
        ('numerica', 'Numérica'),
        ('opcion_multiple', 'Opción múltiple'),
        ('seleccion_multiple', 'Selección múltiple'),
        ('texto_libre', 'Texto libre'),
    ]

    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name='preguntas')
    enunciado_latex = models.TextField()
    tipo_respuesta = models.CharField(max_length=20, choices=TIPO_RESPUESTA)

    # Para respuesta numérica
    respuesta_numerica = models.FloatField(null=True, blank=True)
    tolerancia = models.FloatField(default=0.01, help_text="Margen de error aceptado")

    # Metadatos de generación
    dificultad = models.PositiveIntegerField(default=1)
    parametros_json = models.JSONField(default=dict, help_text="Operandos usados para regenerar")
    explicacion_latex = models.TextField(blank=True, help_text="Explicación paso a paso")
    timestamp_generacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp_generacion']
        indexes = [
            models.Index(fields=['tema', 'dificultad']),
        ]

    def __str__(self):
        return f"{self.tema.nombre} (Dificultad {self.dificultad}) - {self.tipo_respuesta}"


class OpcionRespuesta(models.Model):
    """
    Opciones para preguntas de selección múltiple.
    La correcta se marca con es_correcta=True.
    """
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='opciones')
    texto = models.CharField(max_length=300)
    texto_latex = models.TextField(blank=True, help_text="Si tiene fórmulas")
    es_correcta = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.texto} ({'Correcta' if self.es_correcta else 'Incorrecta'})"


class RegistroRespuesta(models.Model):
    """
    Cada intento de un usuario a una pregunta.
    Reemplaza el guardado simple de la tabla Intento.
    """
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='respuestas')
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='registros')
    respuesta_dada = models.TextField()  # Lo que escribió/eligió el usuario
    es_correcta = models.BooleanField()
    tiempo_segundos = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['usuario', 'es_correcta']),
            models.Index(fields=['usuario', 'pregunta']),
        ]

    def __str__(self):
        return f"{self.usuario.username} - {self.pregunta.tema.nombre} - {'Correcto' if self.es_correcta else 'Incorrecto'}"


class TemaProgreso(models.Model):
    """
    Progreso de un usuario en un tema específico.
    Se actualiza tras cada respuesta correcta/incorrecta.
    """
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='progresos')
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name='progresos')
    dificultad_actual = models.PositiveIntegerField(default=1)
    aciertos_consecutivos = models.PositiveIntegerField(default=0)
    fallos_consecutivos = models.PositiveIntegerField(default=0)
    total_aciertos = models.PositiveIntegerField(default=0)
    total_intentos = models.PositiveIntegerField(default=0)
    ultima_practica = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['usuario', 'tema']

    @property
    def porcentaje_acierto(self):
        if self.total_intentos == 0:
            return 0
        return round((self.total_aciertos / self.total_intentos) * 100, 1)

    def __str__(self):
        return f"{self.usuario.username} - {self.tema.nombre} (Nivel {self.dificultad_actual})"
