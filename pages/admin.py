from django.contrib import admin
from .models import Page, Home1Page # Importamos el nuevo modelo

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Page.
    """
    list_display = ('title', 'slug', 'visible', 'template')
    list_filter = ('visible', 'template')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'visible')
        }),
        ('Contenido y Apariencia', {
            'fields': ('template', 'content')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',) # Oculta esta sección por defecto
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

    def get_readonly_fields(self, request, obj=None):
        # El slug no se puede editar una vez creado para evitar romper URLs
        if obj:
            return self.readonly_fields + ('slug',)
        return self.readonly_fields

@admin.register(Home1Page)
class Home1PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'visible', 'created_at')
    list_filter = ('visible',)
    search_fields = ('title', 'hero_title', 'content_section_title', 'about_title')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'visible')
        }),
        ('Sección Hero', {
            'fields': ('hero_title', 'hero_subtitle', 'hero_background_image', 'hero_cta_text', 'hero_cta_link')
        }),
        ('Sección de Contenido Principal', {
            'fields': ('content_section_title', 'content_cta_text', 'content_cta_link')
        }),
        ('Cards de Contenido', {
            'fields': (
                ('card1_title', 'card1_image'), 'card1_description',
                ('card2_title', 'card2_image'), 'card2_description',
                ('card3_title', 'card3_image'), 'card3_description',
            ),
            'description': 'Configura las 3 tarjetas de características/productos.'
        }),
        ('Sección "About"', {
            'fields': ('about_title', 'about_text_paragraph1', 'about_text_paragraph2', 'about_image')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
