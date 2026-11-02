from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify

# Opciones de plantilla para el selector en el admin (se mantienen)
TEMPLATE_CHOICES = [
    ('pages/layouts/pagina_estandar.html', 'Página Estándar (Con menú y pie de página)'),
    ('pages/layouts/pagina_limpia.html', 'Página Limpia (Para landing pages, sin menú)'),
    ('pages/layouts/listado_blog.html', 'Página con Listado de Artículos del Blog'),
]

class Page(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL amigable (slug)")
    content = RichTextField(verbose_name="Contenido", blank=True)
    visible = models.BooleanField(default=True, verbose_name="¿Visible?")
    template = models.CharField(
        max_length=100,
        choices=TEMPLATE_CHOICES,
        default='pages/layouts/pagina_estandar.html',
        verbose_name="Plantilla a usar"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Página"
        verbose_name_plural = "Páginas"
        ordering = ['title']

    def __str__(self):
        return self.title

# --- NUEVOS MODELOS PARA LAYOUTS ESPECÍFICOS ---

class Home1Page(models.Model):
    # Campos base para identificación
    title = models.CharField(max_length=200, verbose_name="Título de la Página (Admin)")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="URL amigable")
    visible = models.BooleanField(default=True, verbose_name="¿Visible?")

    # Sección Hero
    hero_title = models.CharField(max_length=200, verbose_name="Título del Hero")
    hero_subtitle = models.TextField(verbose_name="Subtítulo del Hero", blank=True)
    hero_background_image = models.ImageField(
        upload_to='pages/moldes_pages/home1/hero/',
        blank=True,
        null=True,
        verbose_name="Imagen de Fondo del Hero"
    )
    hero_cta_text = models.CharField(max_length=50, verbose_name="Texto del Botón CTA Hero")
    hero_cta_link = models.URLField(verbose_name="Enlace del Botón CTA Hero", blank=True)

    # Sección Home Content (Título principal y CTA)
    content_section_title = models.CharField(max_length=200, verbose_name="Título de la Sección de Contenido")
    content_cta_text = models.CharField(max_length=50, verbose_name="Texto del Botón CTA Contenido")
    content_cta_link = models.URLField(verbose_name="Enlace del Botón CTA Contenido", blank=True)

    # Cards de Contenido (3 cards)
    # Card 1
    card1_image = models.ImageField(upload_to='pages/moldes_pages/home1/cards/', blank=True, null=True, verbose_name="Imagen Card 1")
    card1_title = models.CharField(max_length=100, verbose_name="Título Card 1")
    card1_description = models.TextField(verbose_name="Descripción Card 1", blank=True)
    # Card 2
    card2_image = models.ImageField(upload_to='pages/moldes_pages/home1/cards/', blank=True, null=True, verbose_name="Imagen Card 2")
    card2_title = models.CharField(max_length=100, verbose_name="Título Card 2")
    card2_description = models.TextField(verbose_name="Descripción Card 2", blank=True)
    # Card 3
    card3_image = models.ImageField(upload_to='pages/moldes_pages/home1/cards/', blank=True, null=True, verbose_name="Imagen Card 3")
    card3_title = models.CharField(max_length=100, verbose_name="Título Card 3")
    card3_description = models.TextField(verbose_name="Descripción Card 3", blank=True)

    # Sección About
    about_title = models.CharField(max_length=200, verbose_name="Título de la Sección About")
    about_text_paragraph1 = RichTextField(verbose_name="Párrafo 1 About", blank=True)
    about_text_paragraph2 = RichTextField(verbose_name="Párrafo 2 About", blank=True)
    about_image = models.ImageField(
        upload_to='pages/moldes_pages/home1/about/',
        blank=True,
        null=True,
        verbose_name="Imagen de la Sección About"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Página Home 1"
        verbose_name_plural = "Páginas Home 1"
        ordering = ['title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
