from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Vista original que puedes mantener si quieres
    # path('', views.listar, name='listar_articulos'), 
    path('publicaciones/', views.lista_publicaciones, name='blog_publicaciones'),
    path('publicacion/<int:id>/', views.detalle_publicacion, name='detalle_publicacion'),
    #path('categoria/<int:categoria_id>/',views.)
]