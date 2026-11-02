from urllib.parse import urlparse

from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
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
    content = RichTextField(verbose_name='Contenido (clásico)', blank=True,
                            help_text='Opcional si el artículo usa bloques.')
    plantilla = models.ForeignKey('Plantilla', null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name='articulos', verbose_name='Plantilla',
                                  help_text='Al crear el artículo se insertan los bloques de la plantilla.')
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

    @property
    def usa_bloques(self):
        return self.bloques.exists()

    @property
    def resumen(self):
        """Texto plano corto para tarjetas: primer párrafo o el contenido clásico."""
        from django.utils.html import strip_tags
        from django.utils.text import Truncator
        primero = self.bloques.filter(tipo=Bloque.PARRAFO).first()
        texto = primero.datos.get('texto', '') if primero else strip_tags(self.content or '')
        return Truncator(texto).words(30)

    @property
    def minutos_lectura(self):
        from django.utils.html import strip_tags
        palabras = sum(len(b.texto_plano().split()) for b in self.bloques.all())
        palabras += len(strip_tags(self.content or '').split())
        return max(1, round(palabras / 200))

    def aplicar_plantilla(self, plantilla=None):
        """Inserta como bloques cada elemento de la plantilla (al final de los existentes)."""
        plantilla = plantilla or self.plantilla
        if not plantilla:
            return 0
        base = self.bloques.count()
        nuevos = [Bloque(articulo=self, tipo=el['tipo'], orden=base + i + 1, datos=el.get('datos', {}))
                  for i, el in enumerate(plantilla.estructura)]
        Bloque.objects.bulk_create(nuevos)
        return len(nuevos)


class Plantilla(models.Model):
    """Estructura reutilizable: lista ordenada de bloques iniciales."""
    TIPOS = [
        ('tutorial', 'Tutorial / How-to'),
        ('lista', 'Lista (listicle)'),
        ('caso', 'Caso de estudio'),
        ('comparativa', 'Comparativa A vs B'),
        ('principiante', 'Guía para principiantes'),
        ('matematico', 'Tema matemático'),
        ('libre', 'Libre'),
    ]
    nombre = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='libre')
    descripcion = models.CharField(max_length=255, blank=True)
    icono = models.CharField(max_length=40, default='file-lines', help_text='Ícono FontAwesome')
    estructura = models.JSONField(default=list, help_text='Lista de {"tipo": ..., "datos": {...}}')
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Plantilla de artículo'
        verbose_name_plural = 'Plantillas de artículo'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def clean(self):
        validos = {t for t, _ in Bloque.TIPOS}
        if not isinstance(self.estructura, list):
            raise ValidationError({'estructura': 'Debe ser una lista de bloques.'})
        for i, el in enumerate(self.estructura, 1):
            if not isinstance(el, dict) or el.get('tipo') not in validos:
                raise ValidationError({'estructura': f'Elemento {i}: tipo inválido. Válidos: {sorted(validos)}'})

    def __str__(self):
        return self.nombre


class Bloque(models.Model):
    """Un elemento del artículo. 'datos' guarda el contenido según el tipo."""
    TITULO, PARRAFO, IMAGEN, ENLACE, CITA, LISTA = 'titulo', 'parrafo', 'imagen', 'enlace', 'cita', 'lista'
    CODIGO, FORMULA, AVISO, VIDEO, TABLA = 'codigo', 'formula', 'aviso', 'video', 'tabla'
    TIPOS = [
        (TITULO, 'Subtítulo'), (PARRAFO, 'Párrafo'), (IMAGEN, 'Imagen'), (ENLACE, 'Enlace'),
        (CITA, 'Cita'), (LISTA, 'Lista'), (CODIGO, 'Código'), (FORMULA, 'Fórmula LaTeX'),
        (AVISO, 'Aviso / nota'), (VIDEO, 'Video (YouTube)'), (TABLA, 'Tabla'),
    ]
    # Campos esperados en 'datos' por tipo (documentación + ayuda en admin)
    ESQUEMA = {
        TITULO: '{"texto": "...", "nivel": 2}',
        PARRAFO: '{"texto": "..."}',
        IMAGEN: '{"pie": "...", "alt": "..."}  (+ archivo en el campo Imagen)',
        ENLACE: '{"url": "https://...", "texto": "...", "descripcion": "..."}',
        CITA: '{"texto": "...", "autor": "..."}',
        LISTA: '{"items": ["...", "..."], "ordenada": false}',
        CODIGO: '{"codigo": "...", "lenguaje": "python"}',
        FORMULA: '{"latex": "a^2 + b^2 = c^2"}',
        AVISO: '{"texto": "...", "variante": "info|exito|alerta"}',
        VIDEO: '{"url": "https://www.youtube.com/watch?v=..."}',
        TABLA: '{"columnas": ["A", "B"], "filas": [["1", "2"]]}',
    }

    articulo = models.ForeignKey(Articulo_Page, on_delete=models.CASCADE, related_name='bloques')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    orden = models.PositiveIntegerField(default=0, db_index=True)
    datos = models.JSONField(default=dict, blank=True)
    imagen = models.ImageField(upload_to='articulos_posts_blog/bloques/', blank=True)

    class Meta:
        ordering = ['orden', 'id']
        verbose_name = 'Bloque'
        verbose_name_plural = 'Bloques'

    def __str__(self):
        return f'{self.get_tipo_display()} #{self.orden}'

    def clean(self):
        url = (self.datos or {}).get('url')
        if url and urlparse(url).scheme not in ('http', 'https'):
            raise ValidationError({'datos': 'La URL debe empezar con http:// o https://'})

    @property
    def plantilla_html(self):
        return f'articulos/bloques/_{self.tipo}.html'

    @property
    def youtube_id(self):
        """Extrae el ID de un enlace de YouTube (watch?v=, youtu.be/, /embed/)."""
        import re
        m = re.search(r'(?:v=|youtu\.be/|embed/)([\w-]{11})', (self.datos or {}).get('url', ''))
        return m.group(1) if m else ''

    def texto_plano(self):
        d = self.datos or {}
        partes = [str(d.get(k, '')) for k in ('texto', 'pie', 'descripcion', 'autor')]
        partes += [str(x) for x in d.get('items', [])]
        return ' '.join(p for p in partes if p)
