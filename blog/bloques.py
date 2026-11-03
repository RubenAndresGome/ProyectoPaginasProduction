"""Reglas de cada tipo de bloque: valores por defecto y limpieza de 'datos' (lista blanca).

Toda escritura desde el editor pasa por limpiar(): solo se guardan las claves permitidas,
con el tipo y la longitud esperados. El HTML se escapa al renderizar (autoescape)."""
from urllib.parse import urlparse

MAX_TEXTO = 10_000
MAX_CORTO = 300

DEFAULTS = {
    'titulo': {'texto': 'Nuevo subtítulo', 'nivel': 2},
    'parrafo': {'texto': 'Escribe aquí tu párrafo.'},
    'imagen': {'pie': '', 'alt': ''},
    'enlace': {'url': 'https://', 'texto': 'Texto del enlace', 'descripcion': ''},
    'cita': {'texto': 'Una cita inspiradora.', 'autor': ''},
    'lista': {'items': ['Elemento 1', 'Elemento 2'], 'ordenada': False},
    'codigo': {'codigo': 'print("Hola")', 'lenguaje': 'python'},
    'formula': {'latex': 'a^2 + b^2 = c^2'},
    'aviso': {'texto': 'Nota importante.', 'variante': 'info'},
    'video': {'url': ''},
    'tabla': {'columnas': ['Columna A', 'Columna B'], 'filas': [['', '']]},
}

ICONOS = {
    'titulo': 'heading', 'parrafo': 'paragraph', 'imagen': 'image', 'enlace': 'link', 'cita': 'quote-left',
    'lista': 'list-ul', 'codigo': 'code', 'formula': 'square-root-variable', 'aviso': 'circle-info',
    'video': 'video', 'tabla': 'table',
}


def _txt(v, maximo=MAX_CORTO):
    return str(v if v is not None else '')[:maximo]


def _url(v):
    v = _txt(v, 500).strip()
    if not v or v == 'https://':
        return v
    if v.startswith('/') and not v.startswith('//'):
        return v  # ruta interna del sitio
    return v if urlparse(v).scheme in ('http', 'https') else ''


def limpiar(tipo, datos):
    d = datos if isinstance(datos, dict) else {}
    if tipo == 'titulo':
        return {'texto': _txt(d.get('texto')), 'nivel': 3 if str(d.get('nivel')) == '3' else 2}
    if tipo == 'parrafo':
        return {'texto': _txt(d.get('texto'), MAX_TEXTO)}
    if tipo == 'imagen':
        return {'pie': _txt(d.get('pie')), 'alt': _txt(d.get('alt'))}
    if tipo == 'enlace':
        return {'url': _url(d.get('url')), 'texto': _txt(d.get('texto')), 'descripcion': _txt(d.get('descripcion'))}
    if tipo == 'cita':
        return {'texto': _txt(d.get('texto'), 2000), 'autor': _txt(d.get('autor'))}
    if tipo == 'lista':
        items = d.get('items') if isinstance(d.get('items'), list) else []
        return {'items': [_txt(i) for i in items][:100], 'ordenada': bool(d.get('ordenada'))}
    if tipo == 'codigo':
        return {'codigo': _txt(d.get('codigo'), MAX_TEXTO), 'lenguaje': _txt(d.get('lenguaje'), 30)}
    if tipo == 'formula':
        return {'latex': _txt(d.get('latex'), 2000)}
    if tipo == 'aviso':
        v = d.get('variante')
        return {'texto': _txt(d.get('texto'), 2000), 'variante': v if v in ('info', 'exito', 'alerta') else 'info'}
    if tipo == 'video':
        return {'url': _url(d.get('url'))}
    if tipo == 'tabla':
        cols = d.get('columnas') if isinstance(d.get('columnas'), list) else []
        cols = [_txt(c, 100) for c in cols][:12] or ['Columna']
        filas = d.get('filas') if isinstance(d.get('filas'), list) else []
        filas = [[_txt(c, 300) for c in (f if isinstance(f, list) else [])][:len(cols)] + [''] * max(0, len(cols) - len(f if isinstance(f, list) else []))
                 for f in filas][:100]
        return {'columnas': cols, 'filas': filas}
    raise ValueError(f'Tipo de bloque desconocido: {tipo}')
