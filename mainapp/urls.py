from django.urls import path
from . import views

app_name = 'mainapp' # Añadido el namespace de la aplicación

urlpatterns = [
    path('', views.index, name='index'),
    path('hola-mundo/', views.hola_mundo, name='hola_mundo'),
    path('inicio/', views.index, name='inicio'),
    path('test/', views.pagina_pruebas, name='Test'),
    path('test/<int:redirigir>/', views.pagina_pruebas, name='Test'),
    path('contacto/', views.contacto, name='contacto'),
    path('contacto/<str:nombre>/', views.contacto, name='contacto'),
    path('contacto/<str:nombre>/<str:apellidos>/', views.contacto, name='contacto'),
    # Artículos
    path('articulos/', views.buscar_articulos, name='articulos_get'),
    path('articulo/<int:id>/', views.articulo_get, name='articulo_get'),
    path('editar-articulo/<int:id>/', views.articulo_editar, name='articulo_editar'),
    path('borrar-articulo/<int:id>/', views.borrar_articulo, name='borrar_articulo'),
    path('crear-articulo/', views.create_full_article, name='create_full_article'),
]
