from django.apps import AppConfig


class PerfilConfig(AppConfig):
    name = 'perfil'
    verbose_name = 'Perfil y configuración del sitio'

    def ready(self):
        from . import signals  # noqa: F401
