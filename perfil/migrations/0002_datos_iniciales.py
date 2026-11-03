from django.db import migrations


def cargar(apps, schema_editor):
    Config = apps.get_model('perfil', 'ConfiguracionSitio')
    Red = apps.get_model('perfil', 'RedSocial')
    Perfil = apps.get_model('perfil', 'Perfil')
    User = apps.get_model('auth', 'User')
    Config.objects.get_or_create(pk=1)
    if not Red.objects.exists():
        Red.objects.create(nombre='GitHub', url='https://github.com/RubenAndresGome', icono='fab fa-github', orden=1)
        Red.objects.create(nombre='WhatsApp', url='https://wa.me/524661074921', icono='fab fa-whatsapp', orden=2)
    for u in User.objects.all():  # perfiles para usuarios que ya existían
        Perfil.objects.get_or_create(user=u)


class Migration(migrations.Migration):
    dependencies = [('perfil', '0001_initial'), ('auth', '0012_alter_user_first_name_max_length')]
    operations = [migrations.RunPython(cargar, migrations.RunPython.noop)]
