from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ConfiguracionSitio(models.Model):
    """Registro único (pk=1) con la identidad del sitio. Se edita desde el perfil del admin."""
    nombre = models.CharField(max_length=60, default='MathMaster')
    lema = models.CharField(max_length=160, default='Matemáticas remediales con práctica adaptativa.')
    autor = models.CharField(max_length=100, default='Rubén Andrés Gómez Molina')
    whatsapp = models.CharField(max_length=20, blank=True, default='524661074921',
                                help_text='Solo dígitos con lada de país, sin + ni espacios. Ej: 524661074921')
    email = models.EmailField(blank=True)

    class Meta:
        verbose_name = 'Configuración del sitio'
        verbose_name_plural = 'Configuración del sitio'

    def __str__(self):
        return self.nombre

    def clean(self):
        if self.whatsapp and not self.whatsapp.isdigit():
            raise ValidationError({'whatsapp': 'Usa solo dígitos, por ejemplo 524661074921.'})

    def save(self, *args, **kwargs):
        self.pk = 1  # siempre el mismo registro
        super().save(*args, **kwargs)

    @classmethod
    def actual(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def whatsapp_url(self):
        return f'https://wa.me/{self.whatsapp}' if self.whatsapp else ''

    @property
    def telefono_legible(self):
        d = self.whatsapp
        if len(d) == 12 and d.startswith('52'):
            return f'+52 {d[2:5]} {d[5:8]} {d[8:]}'
        return f'+{d}' if d else ''


class RedSocial(models.Model):
    ICONOS = [
        ('fab fa-github', 'GitHub'), ('fab fa-linkedin', 'LinkedIn'), ('fab fa-whatsapp', 'WhatsApp'),
        ('fab fa-x-twitter', 'X / Twitter'), ('fab fa-instagram', 'Instagram'), ('fab fa-facebook', 'Facebook'),
        ('fab fa-youtube', 'YouTube'), ('fab fa-tiktok', 'TikTok'), ('fas fa-envelope', 'Correo'),
        ('fas fa-globe', 'Sitio web'),
    ]
    nombre = models.CharField(max_length=40)
    url = models.CharField(max_length=300, help_text='https://… o mailto:…')
    icono = models.CharField(max_length=40, choices=ICONOS, default='fas fa-globe')
    orden = models.PositiveSmallIntegerField(default=0)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['orden', 'id']
        verbose_name = 'Red social'
        verbose_name_plural = 'Redes sociales'

    def __str__(self):
        return self.nombre

    def clean(self):
        if urlparse(self.url).scheme not in ('http', 'https', 'mailto'):
            raise ValidationError({'url': 'Debe empezar con https://, http:// o mailto:'})


def ruta_avatar(instance, filename):
    return f'avatares/{instance.user_id}/{filename}'


class Perfil(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    avatar = models.ImageField(upload_to=ruta_avatar, blank=True)
    bio = models.CharField(max_length=280, blank=True)
    carrera = models.CharField(max_length=100, blank=True)
    semestre = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return f'Perfil de {self.user}'
