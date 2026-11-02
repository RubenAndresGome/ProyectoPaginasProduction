from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Articulo_Page, Categoria
from django.contrib.auth.decorators import login_required
@login_required(login_url='log_and_reg:login')
def lista_publicaciones(request):
    """
    Vista para listar, buscar y filtrar todas las publicaciones del blog.
    """
    queryset = Articulo_Page.objects.filter(publicado=True)
    
    # Obtener parámetros de la URL para mantenerlos en la paginación
    query_text = request.GET.get('q', '')
    category_slug = request.GET.get('cat', '')

    # Filtrar por texto de búsqueda
    if query_text:
        queryset = queryset.filter(
            Q(title__icontains=query_text) | Q(content__icontains=query_text)
        ).distinct()

    # Filtrar por categoría
    if category_slug:
        queryset = queryset.filter(categoria__slug=category_slug)

    # Ordenar
    queryset = queryset.order_by('-created_at')

    # Paginación
    paginator = Paginator(queryset, 6)  # 6 artículos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Obtener todas las categorías para el formulario de filtro
    categorias = Categoria.objects.all()

    context = {
        'page_obj': page_obj, # El objeto de página contiene todo lo necesario
        'categorias': categorias,
        'title': 'Publicaciones del Blog',
        'query_text': query_text,
        'selected_category_slug': category_slug,
    }
    
    return render(request, 'articulos/lista_publicaciones.html', context)
@login_required(login_url='log_and_reg:login')
def detalle_publicacion(request, id):
    """
    Vista para mostrar el detalle de una publicación.
    """
    articulo = get_object_or_404(Articulo_Page, id=id)
    return render(request, 'articulos/detalle_publicacion.html', {'articulo': articulo})
