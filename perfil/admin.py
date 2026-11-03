from django.contrib import admin

from .models import ConfiguracionSitio, Perfil, RedSocial


@admin.register(ConfiguracionSitio)
class ConfiguracionSitioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'autor', 'whatsapp')

    def has_add_permission(self, request):
        return not ConfiguracionSitio.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RedSocial)
class RedSocialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'url', 'orden', 'activa')
    list_editable = ('orden', 'activa')


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'carrera', 'semestre')
    search_fields = ('user__username', 'carrera')
