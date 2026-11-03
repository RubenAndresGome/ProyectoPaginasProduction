"""Editor visual de artículos por bloques (solo staff).

Las rutas JSON reciben POST con CSRF y devuelven el HTML de la vista previa ya renderizado
con las MISMAS plantillas que la página pública (lo que ves es lo que se publica)."""
import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.db.models import Count, F, Max
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from . import bloques as reglas
from .models import Articulo_Page, Bloque, Categoria, Plantilla

TIPOS_IMAGEN = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
MAX_IMAGEN = 3 * 1024 * 1024


def _preview(request, articulo):
    return render_to_string('articulos/_cuerpo.html', {'articulo': articulo}, request=request)


def _bloque_json(b):
    return {'id': b.id, 'tipo': b.tipo, 'datos': b.datos, 'orden': b.orden,
            'imagen': b.imagen.url if b.imagen else '', 'icono': reglas.ICONOS.get(b.tipo, 'square')}


def _json_body(request):
    try:
        return json.loads(request.body or b'{}')
    except ValueError:
        return None


def _ok(request, articulo, **extra):
    articulo.save(update_fields=['modified_at'])  # marca la fecha de edición
    return JsonResponse({'ok': True, 'preview': _preview(request, articulo), **extra})


# ---------- Páginas ----------
@staff_member_required
def panel(request):
    articulos = (Articulo_Page.objects.select_related('plantilla')
                 .annotate(n_bloques=Count('bloques')).order_by('-modified_at'))
    return render(request, 'editor/panel.html', {'articulos': articulos})


@staff_member_required
def nuevo(request):
    plantillas = Plantilla.objects.filter(activa=True)
    if request.method == 'POST':
        titulo = (request.POST.get('titulo') or '').strip()[:100]
        if not titulo:
            messages.error(request, 'Escribe un título para el artículo.')
            return redirect('blog:editor_nuevo')
        pk = request.POST.get('plantilla', '')
        plantilla = plantillas.filter(pk=pk).first() if pk.isdigit() else None
        with transaction.atomic():
            art = Articulo_Page.objects.create(title=titulo, user=request.user, publicado=False, plantilla=plantilla)
            n = art.aplicar_plantilla() if plantilla else 0
        messages.success(request, f'Borrador creado{f" con {n} bloques" if n else ""}. Edita y publica cuando esté listo.')
        return redirect('blog:editor', art.id)
    return render(request, 'editor/nuevo.html', {'plantillas': plantillas, 'iconos': reglas.ICONOS})


@staff_member_required
def editor(request, id):
    art = get_object_or_404(Articulo_Page.objects.prefetch_related('categoria'), id=id)
    return render(request, 'editor/editor.html', {
        'articulo': art,
        'bloques_json': [_bloque_json(b) for b in art.bloques.all()],
        'tipos': [{'tipo': t, 'nombre': n, 'icono': reglas.ICONOS[t]} for t, n in Bloque.TIPOS],
        'categorias': Categoria.objects.all(),
        'cats_sel': list(art.categoria.values_list('id', flat=True)),
        'preview': _preview(request, art),
    })


# ---------- API JSON ----------
@staff_member_required
@require_POST
def api_meta(request, id):
    art = get_object_or_404(Articulo_Page, id=id)
    d = _json_body(request)
    if d is None:
        return HttpResponseBadRequest('JSON inválido')
    titulo = str(d.get('titulo', art.title)).strip()[:100]
    if not titulo:
        return JsonResponse({'ok': False, 'error': 'El título no puede quedar vacío.'}, status=400)
    art.title = titulo
    art.publicado = bool(d.get('publicado', art.publicado))
    art.save()
    if isinstance(d.get('categorias'), list):
        art.categoria.set(Categoria.objects.filter(id__in=[int(x) for x in d['categorias'] if str(x).isdigit()]))
    return _ok(request, art)


@staff_member_required
@require_POST
def api_agregar(request, id):
    art = get_object_or_404(Articulo_Page, id=id)
    d = _json_body(request) or {}
    tipo = d.get('tipo')
    if tipo not in reglas.DEFAULTS:
        return HttpResponseBadRequest('Tipo inválido')
    despues_de = d.get('despues_de')
    with transaction.atomic():
        if despues_de:
            ref = get_object_or_404(Bloque, id=despues_de, articulo=art)
            art.bloques.filter(orden__gt=ref.orden).update(orden=F('orden') + 1)
            orden = ref.orden + 1
        else:
            orden = (art.bloques.aggregate(m=Max('orden'))['m'] or 0) + 1
        b = Bloque.objects.create(articulo=art, tipo=tipo, orden=orden, datos=dict(reglas.DEFAULTS[tipo]))
    return _ok(request, art, bloque=_bloque_json(b), bloques=[_bloque_json(x) for x in art.bloques.all()])


@staff_member_required
@require_POST
def api_guardar(request, id, bloque_id):
    art = get_object_or_404(Articulo_Page, id=id)
    b = get_object_or_404(Bloque, id=bloque_id, articulo=art)
    if request.content_type.startswith('multipart/'):
        archivo = request.FILES.get('imagen')
        if archivo:
            if archivo.content_type not in TIPOS_IMAGEN or archivo.size > MAX_IMAGEN:
                return JsonResponse({'ok': False, 'error': 'Usa JPG, PNG, WebP o GIF de hasta 3 MB.'}, status=400)
            b.imagen = archivo
        datos = json.loads(request.POST.get('datos') or '{}')
    else:
        datos = (_json_body(request) or {}).get('datos', {})
    b.datos = reglas.limpiar(b.tipo, datos)
    b.save()
    return _ok(request, art, bloque=_bloque_json(b))


@staff_member_required
@require_POST
def api_borrar(request, id, bloque_id):
    art = get_object_or_404(Articulo_Page, id=id)
    get_object_or_404(Bloque, id=bloque_id, articulo=art).delete()
    return _ok(request, art)


@staff_member_required
@require_POST
def api_reordenar(request, id):
    art = get_object_or_404(Articulo_Page, id=id)
    ids = (_json_body(request) or {}).get('ids', [])
    propios = set(art.bloques.values_list('id', flat=True))
    if not isinstance(ids, list) or set(map(int, ids)) != propios:
        return HttpResponseBadRequest('La lista de bloques no coincide con el artículo.')
    with transaction.atomic():
        for i, bid in enumerate(ids, 1):
            Bloque.objects.filter(id=bid, articulo=art).update(orden=i)
    return _ok(request, art)


@staff_member_required
@require_POST
def api_portada(request, id):
    art = get_object_or_404(Articulo_Page, id=id)
    archivo = request.FILES.get('imagen')
    if request.POST.get('quitar'):
        art.imagen = None
    elif not archivo or archivo.content_type not in TIPOS_IMAGEN or archivo.size > MAX_IMAGEN:
        return JsonResponse({'ok': False, 'error': 'Usa JPG, PNG, WebP o GIF de hasta 3 MB.'}, status=400)
    else:
        art.imagen = archivo
    art.save()
    return _ok(request, art, portada=art.imagen.url if art.imagen else '')


@staff_member_required
@require_POST
def eliminar(request, id):
    art = get_object_or_404(Articulo_Page, id=id)
    titulo = art.title
    art.delete()
    messages.success(request, f'Se eliminó «{titulo}».')
    return redirect('blog:editor_panel')

