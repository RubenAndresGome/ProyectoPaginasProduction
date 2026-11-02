import ckeditor.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_alter_categoria_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articulo_page',
            name='content',
            field=ckeditor.fields.RichTextField(blank=True, help_text='Opcional si el artículo usa bloques.', verbose_name='Contenido (clásico)'),
        ),
        migrations.CreateModel(
            name='Plantilla',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=80, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=90, unique=True)),
                ('tipo', models.CharField(choices=[('tutorial', 'Tutorial / How-to'), ('lista', 'Lista (listicle)'), ('caso', 'Caso de estudio'), ('comparativa', 'Comparativa A vs B'), ('principiante', 'Guía para principiantes'), ('matematico', 'Tema matemático'), ('libre', 'Libre')], default='libre', max_length=20)),
                ('descripcion', models.CharField(blank=True, max_length=255)),
                ('icono', models.CharField(default='file-lines', help_text='Ícono FontAwesome', max_length=40)),
                ('estructura', models.JSONField(default=list, help_text='Lista de {"tipo": ..., "datos": {...}}')),
                ('activa', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Plantilla de artículo',
                'verbose_name_plural': 'Plantillas de artículo',
                'ordering': ['nombre'],
            },
        ),
        migrations.AddField(
            model_name='articulo_page',
            name='plantilla',
            field=models.ForeignKey(blank=True, help_text='Al crear el artículo se insertan los bloques de la plantilla.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='articulos', to='blog.plantilla', verbose_name='Plantilla'),
        ),
        migrations.CreateModel(
            name='Bloque',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('titulo', 'Subtítulo'), ('parrafo', 'Párrafo'), ('imagen', 'Imagen'), ('enlace', 'Enlace'), ('cita', 'Cita'), ('lista', 'Lista'), ('codigo', 'Código'), ('formula', 'Fórmula LaTeX'), ('aviso', 'Aviso / nota'), ('video', 'Video (YouTube)'), ('tabla', 'Tabla')], max_length=20)),
                ('orden', models.PositiveIntegerField(db_index=True, default=0)),
                ('datos', models.JSONField(blank=True, default=dict)),
                ('imagen', models.ImageField(blank=True, upload_to='articulos_posts_blog/bloques/')),
                ('articulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bloques', to='blog.articulo_page')),
            ],
            options={
                'verbose_name': 'Bloque',
                'verbose_name_plural': 'Bloques',
                'ordering': ['orden', 'id'],
            },
        ),
    ]
