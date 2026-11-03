from django.urls import path

from . import views

app_name = 'mensajes'

urlpatterns = [
    path('enviar/', views.enviar, name='enviar'),
    path('mis-mensajes/', views.mis_mensajes, name='mis_mensajes'),
    path('bandeja/', views.bandeja, name='bandeja'),
    path('bandeja/<int:id>/', views.detalle, name='detalle'),
    path('tutor/', views.bot_responder, name='bot'),
]
