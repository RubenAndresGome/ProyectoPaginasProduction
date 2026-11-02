from blog.models import Categoria

def get_categorias(request):
    categorias = Categoria.objects.all().order_by('name')
    return {
        'categorias': categorias
    }
