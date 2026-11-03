from django import forms
from django.contrib.auth import get_user_model
from django.forms import modelformset_factory

from .models import ConfiguracionSitio, Perfil, RedSocial

CSS = 'campo'


class _Estilo:
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        for f in self.fields.values():
            if not isinstance(f.widget, (forms.CheckboxInput, forms.ClearableFileInput)):
                f.widget.attrs.setdefault('class', CSS)


class UsuarioForm(_Estilo, forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']
        labels = {'first_name': 'Nombre', 'last_name': 'Apellidos', 'email': 'Correo'}


class PerfilForm(_Estilo, forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['avatar', 'bio', 'carrera', 'semestre']
        labels = {'bio': 'Sobre ti', 'carrera': 'Carrera', 'semestre': 'Semestre'}
        widgets = {'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Cuéntanos algo en 280 caracteres'})}

    def clean_avatar(self):
        img = self.cleaned_data.get('avatar')
        if img and hasattr(img, 'size') and img.size > 2 * 1024 * 1024:
            raise forms.ValidationError('La imagen debe pesar menos de 2 MB.')
        return img


class ConfiguracionForm(_Estilo, forms.ModelForm):
    class Meta:
        model = ConfiguracionSitio
        fields = ['nombre', 'lema', 'autor', 'whatsapp', 'email']
        labels = {'nombre': 'Nombre del sitio', 'lema': 'Lema', 'autor': 'Autor (pie de página)',
                  'whatsapp': 'WhatsApp', 'email': 'Correo de contacto'}


class RedSocialForm(_Estilo, forms.ModelForm):
    class Meta:
        model = RedSocial
        fields = ['nombre', 'icono', 'url', 'orden', 'activa']


RedesFormSet = modelformset_factory(RedSocial, form=RedSocialForm, extra=1, can_delete=True)
