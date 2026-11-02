"""Crea artículos de demostración (uno por plantilla, con contenido real). Idempotente.
Uso: python manage.py blog_demo"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from blog.models import Articulo_Page, Bloque, Categoria, Plantilla
from blog.plantillas_base import A, C, E, F, I, L, P, T, TB

DEMOS = [
    ("tema-matematico", "Teorema de Pitágoras explicado", "Matemáticas", [
        T("Teoría"), P("En todo triángulo rectángulo, el cuadrado de la hipotenusa es igual a la suma de los cuadrados de los catetos."),
        T("Fórmula"), F("c = \\sqrt{a^2 + b^2}"),
        T("Ejemplo resuelto"), P("Si los catetos miden 3 y 4, entonces c = √(9 + 16) = √25 = 5."),
        A("Tip: las ternas 3-4-5 y 5-12-13 aparecen muy seguido en exámenes.", "info"),
        E("/entrenador/practicar/geometria/", "Practica geometría en el entrenador", "Ejercicios adaptativos generados al azar"),
    ]),
    ("tutorial", "Cómo ejecutar este proyecto Django en Windows", "Desarrollo", [
        P("Guía para levantar la plataforma localmente en Windows sin WSL."),
        T("Lo que necesitas"), L(["Windows 10/11", "PowerShell", "Espacio en el disco D:"]),
        T("Pasos"), L(["Ejecuta setup_windows.ps1", "Ejecuta run_windows.bat", "Abre http://127.0.0.1:8000/"], ordenada=True),
        {"tipo": "codigo", "datos": {"lenguaje": "powershell", "codigo": "powershell -ExecutionPolicy Bypass -File .\\setup_windows.ps1\n.\\run_windows.bat"}},
        A("Si PowerShell bloquea el script, usa -ExecutionPolicy Bypass solo para esa ejecución.", "alerta"),
    ]),
    ("lista", "5 hábitos para estudiar matemáticas", "Matemáticas", [
        P("Pequeños cambios que mejoran tu rendimiento en matemáticas remediales."),
        T("1. Practica un poco cada día"), P("Quince minutos diarios superan a tres horas el domingo."),
        T("2. Explica en voz alta"), P("Si puedes explicarlo, lo entendiste."),
        T("3. Revisa tus errores"), P("El historial del entrenador muestra en qué temas fallas más."),
        T("4. Sube la dificultad gradualmente"), P("El motor adaptativo lo hace por ti."),
        T("5. Descansa"), C("La práctica constante vence al talento que no practica.", "Anónimo"),
    ]),
    ("comparativa", "SQLite vs MySQL para proyectos Django", "Desarrollo", [
        P("Qué base de datos conviene según la etapa del proyecto."),
        TB(["Criterio", "SQLite", "MySQL"], [["Instalación", "Ninguna", "Servidor aparte"], ["Concurrencia", "Baja", "Alta"], ["Ideal para", "Desarrollo y demos", "Producción"]]),
        T("Veredicto"), A("SQLite para desarrollar y demos; MySQL o PostgreSQL cuando hay usuarios concurrentes.", "exito"),
    ]),
]


class Command(BaseCommand):
    help = "Crea artículos de demostración con bloques"

    def handle(self, *args, **opts):
        autor = get_user_model().objects.filter(is_superuser=True).order_by('id').first()
        if not autor:
            self.stderr.write("No hay superusuario. Crea uno primero (crear_admin_local.py).")
            return
        creados = 0
        for slug, titulo, cat_nombre, bloques in DEMOS:
            if Articulo_Page.objects.filter(title=titulo).exists():
                continue
            cat, _ = Categoria.objects.get_or_create(name=cat_nombre, defaults={'descripcion': cat_nombre})
            art = Articulo_Page.objects.create(title=titulo, user=autor, publicado=True,
                                               plantilla=Plantilla.objects.filter(slug=slug).first())
            art.categoria.add(cat)
            Bloque.objects.bulk_create([Bloque(articulo=art, tipo=b['tipo'], datos=b['datos'], orden=i)
                                        for i, b in enumerate(bloques, 1)])
            creados += 1
        self.stdout.write(self.style.SUCCESS(f"[OK] Artículos demo creados: {creados}"))
