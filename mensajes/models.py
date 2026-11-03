from django.conf import settings
from django.db import models


class Mensaje(models.Model):
    nombre = models.CharField(max_length=80)
    email = models.EmailField()
    asunto = models.CharField(max_length=120)
    cuerpo = models.TextField(max_length=3000)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                on_delete=models.SET_NULL, related_name='mensajes')
    creado = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    respuesta = models.TextField(blank=True, max_length=3000)
    respondido_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = 'Mensaje de contacto'
        verbose_name_plural = 'Mensajes de contacto'

    def __str__(self):
        return f'{self.asunto} — {self.nombre}'

    @property
    def respondido(self):
        return bool(self.respuesta)
