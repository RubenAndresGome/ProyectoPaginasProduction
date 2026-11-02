from django import forms
from mainapp.models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'publico' , 'image']
        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500'}),
            'content': forms.Textarea(
                attrs={'class': 'w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 resize-none',
                       'rows': 5
                       }),
            'publico': forms.CheckboxInput(
                attrs={
                    'class': 'w-5 h-5 text-cyan-500 bg-slate-900 border-slate-700 rounded focus:ring-cyan-500'
                }
            ),
            'image': forms.ClearableFileInput(
                attrs=
                {'class': 'block w-full text-slate-300 file:mr-4 '
                          'file:py-2 file:px-4 file:rounded-lg'
                          ' file:border-0 file:text-sm file:font-semibold file:bg-cyan-600'
                          ' file:text-white hover:file:bg-cyan-500'}
            ),
        }
        labels = {
            'title': 'Título del Artículo',
            'content': 'Contenido',
            'publico': 'Visibilidad'
        }

    # Validación personalizada
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 4:
            raise forms.ValidationError('El título debe tener al menos 4 caracteres.')
        return title

