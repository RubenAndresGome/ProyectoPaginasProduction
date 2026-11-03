from django.contrib import admin

from .models import Mensaje


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('asunto', 'nombre', 'email', 'creado', 'leido', 'respondido')
    list_filter = ('leido', 'creado')
    search_fields = ('asunto', 'nombre', 'email', 'cuerpo')

    @admin.display(boolean=True)
    def respondido(self, obj):
        return obj.respondido
