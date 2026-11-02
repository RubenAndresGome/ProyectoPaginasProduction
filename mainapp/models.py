from django.db import models

# Create your models here.
"""/*
Instructor recomienda que los modelos tegan el nombre de 1 articulo en singular
Buscar models en documentacion
*/"""


class Article(models.Model):

    title = models.CharField(max_length=250,verbose_name="Titulo")
    content = models.TextField(verbose_name="Contenido")
    publico=models.BooleanField(default=False ,verbose_name="Publicado")
    publication_date = models.DateField(auto_now_add=True,verbose_name="Fecha de publicacion")
    created_date_at = models.DateField(auto_now_add=True,verbose_name="Fecha de creacion")
    updated_date_at = models.DateField(auto_now=True,verbose_name="Fecha de actualizacion")
    image = models.ImageField(upload_to="articles", null=True, blank=True, verbose_name="Miniatura")
    pass

    class Meta:
        verbose_name = "Articulo"
        verbose_name_plural = "Articulos"
        ordering = ["-created_date_at"]
        #ordering = ['id']
        #ordering = ['-id']
    def __str__(self):
        publicado=""
        if self.publico:
            publicado="(Publicado)"
        else:
            publicado="(No publicado: privado)"
        return f"""{self.title}**{self.created_date_at}**{publicado}"""
        pass



class Category(models.Model):

    name=models.CharField(max_length=250)
    description=models.TextField()
    created_at_date = models.DateField(auto_now_add=True)
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        pass
    pass
