from django.urls import path

from . import views

app_name = 'perfil'

urlpatterns = [
    path('', views.mi_perfil, name='mi_perfil'),
]
