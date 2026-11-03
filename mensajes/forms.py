from django import forms

from .models import Mensaje


class ContactoForm(forms.ModelForm):
    # Trampa para bots: campo oculto que una persona nunca llena
    sitio_web = forms.CharField(required=False, widget=forms.TextInput(attrs={'tabindex': '-1', 'autocomplete': 'off'}))

    class Meta:
        model = Mensaje
        fields = ['nombre', 'email', 'asunto', 'cuerpo']
        labels = {'nombre': 'Tu nombre', 'email': 'Tu correo', 'asunto': 'Asunto', 'cuerpo': 'Mensaje'}
        widgets = {'cuerpo': forms.Textarea(attrs={'rows': 5})}

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        for n, f in self.fields.items():
            if n != 'sitio_web':
                f.widget.attrs.setdefault('class', 'campo')
        self.fields['cuerpo'].widget.attrs['placeholder'] = '¿En qué te puedo ayudar?'

    def es_spam(self):
        return bool(self.cleaned_data.get('sitio_web'))


class RespuestaForm(forms.Form):
    respuesta = forms.CharField(max_length=3000, widget=forms.Textarea(attrs={'rows': 5, 'class': 'campo'}),
                                label='Tu respuesta')
