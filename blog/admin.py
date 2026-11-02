from django.contrib import admin
from django.utils.html import format_html_join

from .models import Articulo_Page, Bloque, Categoria, Plantilla


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class BloqueInline(admin.StackedInline):
    model = Bloque
    extra = 0
    fields = ('orden', 'tipo', 'datos', 'imagen')
    ordering = ('orden',)


@admin.register(Articulo_Page)
class ArticuloPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'plantilla', 'num_bloques', 'user', 'publicado', 'created_at')
    list_filter = ('publicado', 'plantilla', 'categoria')
    search_fields = ('title', 'content')
    filter_horizontal = ('categoria',)
    inlines = [BloqueInline]
    readonly_fields = ('ayuda_bloques',)
    fieldsets = (
        (None, {'fields': ('title', 'user', 'plantilla', 'imagen', 'categoria', 'publicado')}),
        ('Contenido clásico (opcional)', {'classes': ('collapse',), 'fields': ('content',)}),
        ('Formato de los bloques', {'classes': ('collapse',), 'fields': ('ayuda_bloques',)}),
    )

    @admin.display(description='Bloques')
    def num_bloques(self, obj):
        return obj.bloques.count()

    @admin.display(description='Campos de "datos" por tipo')
    def ayuda_bloques(self, obj=None):
        return format_html_join('', '<p><b>{}</b>: <code>{}</code></p>', Bloque.ESQUEMA.items())

    def get_changeform_initial_data(self, request):
        return {'user': request.user.pk}

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        art = form.instance
        # Artículo nuevo (o sin bloques) con plantilla: insertar sus elementos
        if art.plantilla_id and not art.bloques.exists():
            n = art.aplicar_plantilla()
            self.message_user(request, f'Se insertaron {n} bloques desde la plantilla "{art.plantilla}".')


@admin.register(Plantilla)
class PlantillaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'num_elementos', 'activa')
    list_filter = ('tipo', 'activa')
    prepopulated_fields = {'slug': ('nombre',)}

    @admin.display(description='Elementos')
    def num_elementos(self, obj):
        return len(obj.estructura or [])
