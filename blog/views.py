from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError
from django.db.models import Count, F, Q as _Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from .markdown import articulo_a_md
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Articulo_Page, Categoria, MeGusta, VistaArticulo
from django.contrib.auth.decorators import login_required
def lista_publicaciones(request):
    """
    Vista para listar, buscar y filtrar todas las publicaciones del blog.
    """
    queryset = (Articulo_Page.objects.filter(publicado=True)
                .select_related('plantilla', 'user').prefetch_related('categoria', 'bloques'))
    
    # Obtener parámetros de la URL para mantenerlos en la paginación
    query_text = request.GET.get('q', '')
    category_slug = request.GET.get('cat', '')

    # Filtrar por texto de búsqueda
    if query_text:
        queryset = queryset.filter(
            Q(title__icontains=query_text) | Q(content__icontains=query_text)
            | Q(bloques__datos__icontains=query_text)
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
def detalle_publicacion(request, id):
    """
    Vista para mostrar el detalle de una publicación.
    """
    qs = Articulo_Page.objects.select_related('user', 'plantilla').prefetch_related('categoria', 'bloques')
    if not request.user.is_staff:
        qs = qs.filter(publicado=True)  # los borradores solo los ve el staff
    articulo = get_object_or_404(qs, id=id)
    if articulo.publicado and not request.user.is_staff:
        _registrar_vista(request, articulo)
    return render(request, 'articulos/detalle_publicacion.html', {
        'articulo': articulo,
        'total_megusta': articulo.me_gusta.count(),
        'me_gusta': request.user.is_authenticated and articulo.me_gusta.filter(usuario=request.user).exists(),
        'url_absoluta': request.build_absolute_uri(),
    })


def _visitante(request):
    if request.user.is_authenticated:
        return f'u{request.user.pk}'
    if not request.session.session_key:
        request.session.save()
    return f's{request.session.session_key}'


def _registrar_vista(request, articulo):
    try:
        VistaArticulo.objects.get_or_create(articulo=articulo, visitante=_visitante(request),
                                            fecha=timezone.localdate())
    except IntegrityError:  # dos peticiones simultáneas
        pass


def _publicado(id):
    return get_object_or_404(Articulo_Page, id=id, publicado=True)


@require_POST
def me_gusta(request, id):
    articulo = _publicado(id)
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'login': reverse('log_and_reg:login') + f'?next={reverse("blog:detalle_publicacion", args=[id])}'}, status=401)
    obj, creado = MeGusta.objects.get_or_create(articulo=articulo, usuario=request.user)
    if not creado:
        obj.delete()
    return JsonResponse({'ok': True, 'me_gusta': creado, 'total': articulo.me_gusta.count()})


@require_POST
def compartir(request, id):
    articulo = _publicado(id)
    ya = request.session.setdefault('compartidos', [])
    if id not in ya:  # una vez por sesión
        Articulo_Page.objects.filter(id=id).update(veces_compartido=F('veces_compartido') + 1)
        request.session['compartidos'] = ya + [id]
    articulo.refresh_from_db(fields=['veces_compartido'])
    return JsonResponse({'ok': True, 'total': articulo.veces_compartido})


def exportar_markdown(request, id):
    qs = Articulo_Page.objects.select_related('user').prefetch_related('categoria', 'bloques')
    if not request.user.is_staff:
        qs = qs.filter(publicado=True)
    articulo = get_object_or_404(qs, id=id)
    md = articulo_a_md(articulo, url_base=request.build_absolute_uri('/').rstrip('/'))
    resp = HttpResponse(md, content_type='text/markdown; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="{slugify(articulo.title) or "articulo"}.md"'
    return resp


@staff_member_required
def metricas(request):
    hace30 = timezone.localdate() - timedelta(days=29)
    articulos = (Articulo_Page.objects
                 .annotate(vistas_total=Count('vistas', distinct=True),
                           vistas_30=Count('vistas', filter=_Q(vistas__fecha__gte=hace30), distinct=True),
                           likes=Count('me_gusta', distinct=True))
                 .order_by('-vistas_total', '-likes'))
    por_dia = dict(VistaArticulo.objects.filter(fecha__gte=hace30).values_list('fecha')
                   .annotate(n=Count('id')).values_list('fecha', 'n'))
    maximo = max(por_dia.values() or [1])
    serie = [{'fecha': hace30 + timedelta(days=i), 'n': por_dia.get(hace30 + timedelta(days=i), 0)} for i in range(30)]
    for p in serie:
        p['alto'] = round(100 * p['n'] / maximo) if maximo else 0
    return render(request, 'editor/metricas.html', {
        'articulos': articulos, 'serie': serie,
        'totales': {
            'vistas': VistaArticulo.objects.count(),
            'vistas_30': sum(p['n'] for p in serie),
            'likes': MeGusta.objects.count(),
            'compartidos': sum(a.veces_compartido for a in articulos),
        },
    })
