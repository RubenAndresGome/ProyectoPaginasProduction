"""Exporta un artículo (bloques + metadatos) a Markdown con front matter YAML."""
from django.utils.html import strip_tags


def _esc(t):
    return str(t or '').replace('\r', '')


def bloque_a_md(b, url_base=''):
    d = b.datos or {}
    t = b.tipo
    if t == 'titulo':
        return f"{'###' if str(d.get('nivel')) == '3' else '##'} {_esc(d.get('texto'))}"
    if t == 'parrafo':
        return _esc(d.get('texto'))
    if t == 'imagen':
        src = (url_base + b.imagen.url) if b.imagen else ''
        md = f"![{_esc(d.get('alt') or d.get('pie'))}]({src})" if src else ''
        return md + (f"\n*{_esc(d.get('pie'))}*" if d.get('pie') else '')
    if t == 'enlace':
        desc = f" — {_esc(d.get('descripcion'))}" if d.get('descripcion') else ''
        url = d.get('url', '')
        url = url_base + url if url.startswith('/') else url
        return f"[{_esc(d.get('texto') or url)}]({url}){desc}"
    if t == 'cita':
        lineas = '\n'.join(f'> {l}' for l in _esc(d.get('texto')).split('\n'))
        return lineas + (f"\n>\n> — {_esc(d.get('autor'))}" if d.get('autor') else '')
    if t == 'lista':
        items = d.get('items') or []
        return '\n'.join(f"{i}. {_esc(x)}" if d.get('ordenada') else f"- {_esc(x)}" for i, x in enumerate(items, 1))
    if t == 'codigo':
        return f"```{_esc(d.get('lenguaje'))}\n{_esc(d.get('codigo'))}\n```"
    if t == 'formula':
        return f"$$\n{_esc(d.get('latex'))}\n$$"
    if t == 'aviso':
        tipo = {'alerta': 'WARNING', 'exito': 'TIP'}.get(d.get('variante'), 'NOTE')
        return f"> [!{tipo}]\n" + '\n'.join(f'> {l}' for l in _esc(d.get('texto')).split('\n'))
    if t == 'video':
        return f"[▶ Ver video]({_esc(d.get('url'))})" if d.get('url') else ''
    if t == 'tabla':
        cols = d.get('columnas') or []
        if not cols:
            return ''
        celda = lambda x: _esc(x).replace('|', '\\|').replace('\n', ' ')
        filas = [f"| {' | '.join(celda(c) for c in cols)} |", f"|{'---|' * len(cols)}"]
        filas += [f"| {' | '.join(celda(c) for c in f)} |" for f in (d.get('filas') or [])]
        return '\n'.join(filas)
    return ''


def articulo_a_md(articulo, url_base=''):
    cats = ', '.join(c.name for c in articulo.categoria.all())
    cab = [
        '---',
        f'title: "{_esc(articulo.title).replace(chr(34), chr(39))}"',
        f'author: "{articulo.user.get_full_name() or articulo.user.username}"',
        f'date: {articulo.created_at:%Y-%m-%d}',
        f'categories: [{cats}]',
        f'source: {url_base}/blog/publicacion/{articulo.id}/',
        '---', '', f'# {_esc(articulo.title)}', '',
    ]
    partes = [bloque_a_md(b, url_base) for b in articulo.bloques.all()]
    if articulo.content:
        partes.append(strip_tags(articulo.content))
    return '\n'.join(cab) + '\n' + '\n\n'.join(p for p in partes if p) + '\n'
