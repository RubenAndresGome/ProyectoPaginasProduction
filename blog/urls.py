from django.urls import path

from . import editor_views as ed
from . import views

app_name = 'blog'

urlpatterns = [
    path('publicaciones/', views.lista_publicaciones, name='blog_publicaciones'),
    path('publicacion/<int:id>/', views.detalle_publicacion, name='detalle_publicacion'),
    path('publicacion/<int:id>/me-gusta/', views.me_gusta, name='me_gusta'),
    path('publicacion/<int:id>/compartir/', views.compartir, name='compartir'),
    path('publicacion/<int:id>/markdown/', views.exportar_markdown, name='markdown'),
    path('editor/metricas/', views.metricas, name='metricas'),
    # --- Editor visual (staff) ---
    path('editor/', ed.panel, name='editor_panel'),
    path('editor/nuevo/', ed.nuevo, name='editor_nuevo'),
    path('editor/<int:id>/', ed.editor, name='editor'),
    path('editor/<int:id>/eliminar/', ed.eliminar, name='editor_eliminar'),
    path('editor/<int:id>/api/meta/', ed.api_meta, name='api_meta'),
    path('editor/<int:id>/api/portada/', ed.api_portada, name='api_portada'),
    path('editor/<int:id>/api/agregar/', ed.api_agregar, name='api_agregar'),
    path('editor/<int:id>/api/reordenar/', ed.api_reordenar, name='api_reordenar'),
    path('editor/<int:id>/api/bloque/<int:bloque_id>/', ed.api_guardar, name='api_guardar'),
    path('editor/<int:id>/api/bloque/<int:bloque_id>/borrar/', ed.api_borrar, name='api_borrar'),
]
