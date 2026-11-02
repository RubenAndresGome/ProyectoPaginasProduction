
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from mainapp.models import Article
from mainapp.forms import ArticleForm

def index(request):
    return render(request, "paginas_principales/index.html")

def hola_mundo(request):
    return render(request, "paginas_principales/hola_mundo.html")

def pagina_pruebas(request, redirigir=0):
    if redirigir == 1:
        return redirect('mainapp:contacto', nombre='Ruben', apellidos='Andres')

    return render(request, "paginas_principales/pagina_pruebas.html", {
        'texto_test':"Hola como estas",
        'lista':["1","2","3","3"]
    })

def contacto(request, nombre="User", apellidos="Lastname"):
    return render(request, "paginas_principales/contacto.html", {
        "title": f"Contacto {nombre} {apellidos}"
    })

# --- Vistas para Artículos (CRUD) ---
def buscar_articulos(request):
    query = request.GET.get('q', '').strip()
    if query:
        articulos = Article.objects.filter(title__icontains=query).order_by('-created_date_at')
        mensaje = f"🔍 Resultados para: '{query}'"
    else:
        articulos = Article.objects.all().order_by('-created_date_at')
        mensaje = "📚 Todos los artículos"
        
    return render(request, 'actions_articules/articulos.html', {
        'articulos': articulos,
        'query': query,
        'mensaje': mensaje,
        'total': articulos.count()
    })

def articulo_get(request, id):
    article = get_object_or_404(Article, id=id)
    return render(request, "actions_articules/articulo_detalle.html", {'article': article})

@staff_member_required
def articulo_editar(request, id):
    article = get_object_or_404(Article, id=id)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Artículo '{article.title}' editado correctamente")
            return redirect('mainapp:articulo_get', id=article.id)
    else:
        form = ArticleForm(instance=article)
    return render(request,
                  'actions_articules/crear_and_editar_articulo_form.html',
                  {'form': form, 'editando': True})

@staff_member_required
def create_full_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)  # incluye FILES para la imagen
        if form.is_valid():
            article = form.save()
            messages.success(request, f"✅ Artículo '{article.title}' creado correctamente")
            return redirect('mainapp:articulos_get')
    else:
        form = ArticleForm()
        
    return render(request, 'actions_articules/crear_and_editar_articulo_form.html',
                  {'form': form, 'editando': False})

@staff_member_required
@require_POST
def borrar_articulo(request, id):
    article = get_object_or_404(Article, id=id)
    titulo = article.title
    article.delete()
    messages.success(request, f"✅ Artículo '{titulo}' eliminado correctamente")
    return redirect('mainapp:articulos_get')