"""Carga inicial de los temas del entrenador (uno por generador en GENERADORES_MAP).
Idempotente: update_or_create por slug; no pisa temas editados manualmente salvo estos campos.
"""
from django.db import migrations

TEMAS = [
    # slug, nombre, categoria, icono FontAwesome, descripcion
    ("aritmetica", "Aritmética", "aritmetica", "calculator",
     "Operaciones básicas, fracciones, potencias y jerarquía de operaciones."),
    ("algebra-basica", "Álgebra Básica", "algebra_basica", "superscript",
     "Ecuaciones lineales, propiedad distributiva y ecuaciones cuadráticas."),
    ("algebra-avanzada", "Álgebra Avanzada", "algebra_avanzada", "square-root-variable",
     "Leyes de exponentes, logaritmos, sistemas de ecuaciones y productos notables."),
    ("geometria", "Geometría", "geometria", "shapes",
     "Áreas, perímetros, volúmenes y teorema de Pitágoras."),
    ("trigonometria", "Trigonometría", "trigonometria", "wave-square",
     "Razones trigonométricas, ángulos y resolución de triángulos."),
    ("conjuntos", "Lógica de Conjuntos", "conjuntos", "circle-nodes",
     "Unión, intersección, diferencia y complemento de conjuntos."),
    ("silogismos", "Silogismos", "silogismos", "brain",
     "Razonamiento deductivo con premisas y conclusiones."),
]


def cargar(apps, schema_editor):
    Tema = apps.get_model("entrenador", "Tema")
    for orden, (slug, nombre, categoria, icono, desc) in enumerate(TEMAS, start=1):
        Tema.objects.update_or_create(
            slug=slug,
            defaults=dict(nombre=nombre, categoria=categoria, icono=icono,
                          descripcion=desc, activo=True, orden=orden,
                          dificultad_minima=1, dificultad_maxima=10),
        )


def quitar(apps, schema_editor):
    apps.get_model("entrenador", "Tema").objects.filter(
        slug__in=[t[0] for t in TEMAS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("entrenador", "0002_alter_tema_options_tema_activo_tema_categoria_and_more"),
    ]
    operations = [migrations.RunPython(cargar, quitar)]
