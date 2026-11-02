from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify

class Categoria(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nombre de la Categoria')
    slug = models.SlugField(max_length=120, unique=True, blank=True, verbose_name='Slug') # ESTADO FINAL
    descripcion = models.CharField(max_length=255, verbose_name='Descripcion')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creacion')
    modified_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de modificacion')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.name

class Articulo_Page(models.Model):
    title = models.CharField(max_length=100, verbose_name='Titulo')
    content = RichTextField(verbose_name='Contenido')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    imagen = models.ImageField(
        verbose_name='Imagen',
        blank=True,
        upload_to='articulos_posts_blog/'
    )
    categoria = models.ManyToManyField(Categoria, verbose_name='Categorias', blank=True, related_name="articulos")
    publicado = models.BooleanField(verbose_name='Publicado o No? ', default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creacion')
    modified_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de modificacion')

    class Meta:
        verbose_name = 'Articulo blog'
        verbose_name_plural = 'Articulos del blog'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
