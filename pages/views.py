from django.shortcuts import render, get_object_or_404
from django.db.models import Q # Importamos Q para la búsqueda
from .models import Page, Home1Page # Importamos el nuevo modelo Home1Page
from blog.models import Articulo_Page, Categoria # Importamos los modelos necesarios
from django.contrib.auth.decorators import login_required
@login_required(login_url='log_and_reg:login')
def page_detail(request, slug):
    """
    Vista para renderizar una página dinámica.
    """
    page = get_object_or_404(Page, slug=slug, visible=True)
    
    context = {
        'page': page
    }
    
    # Si la plantilla es la de listado de blog, hacemos la magia
    if page.template == 'pages/layouts/listado_blog.html':
        # Obtenemos la base de la consulta de artículos
        articulos_query = Articulo_Page.objects.filter(publicado=True)

        # Obtenemos los parámetros de la URL
        search_query = request.GET.get('q', '')
        category_slug = request.GET.get('cat', '')

        # Filtrar por texto de búsqueda
        if search_query:
            articulos_query = articulos_query.filter(
                Q(title__icontains=search_query) | Q(content__icontains=search_query)
            ).distinct()
        
        # Filtrar por categoría si existe
        if category_slug:
            articulos_query = articulos_query.filter(categoria__slug=category_slug)

        # Obtenemos todas las categorías para el formulario de filtros
        categorias = Categoria.objects.all()

        # Añadimos todo al contexto
        context['articulos'] = articulos_query.order_by('-created_at')
        context['categorias'] = categorias
    
    return render(request, page.template, context)

# --- NUEVAS VISTAS PARA LAYOUTS ESPECÍFICOS ---
@login_required(login_url='log_and_reg:login')
def home_1_page_detail(request, slug):
    """
    Vista para renderizar una página Home1Page específica.
    """
    page = get_object_or_404(Home1Page, slug=slug, visible=True)
    return render(request, 'pages/moldes_pages/home_1_page.html', {'page': page})
