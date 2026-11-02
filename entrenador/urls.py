from django.urls import path
from . import views

app_name = 'entrenador'

urlpatterns = [
    path('', views.seleccionar_tema, name='inicio'),
    path('practicar/', views.practicar, name='practicar'),
    path('practicar/<slug:slug>/', views.practicar, name='practicar_tema'),
    path('historial/', views.historial, name='historial'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/estudiante/<int:user_id>/', views.detalle_estudiante_ajax, name='detalle_estudiante_ajax'),
    # Placeholder URLs for new navigation
    path('hola-mundo/', views.placeholder_view, name='hola_mundo'),
    path('test/', views.placeholder_view, name='test'),
    path('contacto/', views.placeholder_view, name='contacto'),
    path('blog/', views.placeholder_view, name='blog'),
    path('matematicas/', views.placeholder_view, name='matematicas'),
    path('articulos/', views.placeholder_view, name='articulos'),
]
