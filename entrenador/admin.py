from django.contrib import admin
from .models import Tema, Pregunta, OpcionRespuesta, RegistroRespuesta, TemaProgreso

class OpcionRespuestaInline(admin.TabularInline):
    model = OpcionRespuesta
    extra = 2


@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre',)}
    list_display = ('nombre', 'categoria', 'slug', 'activo', 'orden', 'dificultad_minima', 'dificultad_maxima')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre', 'descripcion')


@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ('id', 'tema', 'tipo_respuesta', 'dificultad', 'timestamp_generacion')
    list_filter = ('tema', 'tipo_respuesta', 'dificultad')
    search_fields = ('enunciado_latex',)
    inlines = [OpcionRespuestaInline]


@admin.register(OpcionRespuesta)
class OpcionRespuestaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pregunta', 'texto', 'es_correcta', 'orden')
    list_filter = ('es_correcta',)
    search_fields = ('texto',)


@admin.register(RegistroRespuesta)
class RegistroRespuestaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'get_tema', 'es_correcta', 'tiempo_segundos', 'timestamp')
    list_filter = ('es_correcta', 'pregunta__tema', 'timestamp')
    search_fields = ('usuario__username', 'respuesta_dada')

    def get_tema(self, obj):
        return obj.pregunta.tema.nombre
    get_tema.short_description = 'Tema'


@admin.register(TemaProgreso)
class TemaProgresoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tema', 'dificultad_actual', 'aciertos_consecutivos', 'total_aciertos', 'total_intentos', 'porcentaje_acierto', 'ultima_practica')
    list_filter = ('tema', 'dificultad_actual', 'ultima_practica')
    search_fields = ('usuario__username', 'tema__nombre')
