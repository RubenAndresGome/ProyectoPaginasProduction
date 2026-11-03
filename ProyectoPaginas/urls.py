from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mainapp.urls')),
    path('blog/', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('login_and_reg.urls', namespace='log_and_reg')),
    path('entrenador/', include('entrenador.urls')),
    path('perfil/', include('perfil.urls')),
    path('mensajes/', include('mensajes.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    urlpatterns = [path('__debug__/', include('debug_toolbar.urls'))] + urlpatterns

admin.site.site_header = 'MathMaster · Administración'
admin.site.site_title = 'MathMaster'
admin.site.index_title = "Panel de gestión"
