from django.contrib import admin
from .models import Categoria, Articulo_Page

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)} # Autocompleta el slug desde el nombre

@admin.register(Articulo_Page)
class ArticuloPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'publicado', 'created_at')
    list_filter = ('publicado', 'user', 'categoria')
    search_fields = ('title', 'content')
    filter_horizontal = ('categoria',) # Mejor interfaz para ManyToMany
