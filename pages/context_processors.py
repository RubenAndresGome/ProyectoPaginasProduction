from .models import Page

def get_pages(request):
    """
    Context processor para obtener las páginas visibles y pasarlas a todas las plantillas.
    """
    # CORREGIDO: Se usa 'title' en lugar de 'titulo' para coincidir con el modelo.
    pages = Page.objects.filter(visible=True).values_list('id', 'title', 'slug')
    
    return {
        'pages': pages
    }
