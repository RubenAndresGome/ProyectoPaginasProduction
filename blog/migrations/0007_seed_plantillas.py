from django.db import migrations


def cargar(apps, schema_editor):
    from blog.plantillas_base import PLANTILLAS
    Plantilla = apps.get_model('blog', 'Plantilla')
    for p in PLANTILLAS:
        datos = {k: v for k, v in p.items() if k != 'slug'}
        Plantilla.objects.update_or_create(slug=p['slug'], defaults=datos)


def quitar(apps, schema_editor):
    from blog.plantillas_base import PLANTILLAS
    apps.get_model('blog', 'Plantilla').objects.filter(slug__in=[p['slug'] for p in PLANTILLAS]).delete()


class Migration(migrations.Migration):
    dependencies = [('blog', '0006_bloques_y_plantillas')]
    operations = [migrations.RunPython(cargar, quitar)]
