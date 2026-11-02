from django.urls import path
from . import views

app_name = 'login_and_reg'

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('registro/', views.register_page, name='register'),
    path('logout/', views.logout_user, name='logout')
]
