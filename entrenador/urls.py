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
]
