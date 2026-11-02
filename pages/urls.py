from django.urls import path
from . import views

urlpatterns = [
    # Ruta genérica para las páginas dinámicas (Page model)
    path('<slug:slug>/', views.page_detail, name='page_detail'),
    
    # --- NUEVAS RUTAS PARA LAYOUTS ESPECÍFICOS ---
    # Ruta para las páginas Home1Page
    path('home1/<slug:slug>/', views.home_1_page_detail, name='home_1_page_detail'),
]
