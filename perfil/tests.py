from django.contrib.auth.models import User
from django.test import TestCase

from .models import ConfiguracionSitio, Perfil, RedSocial


class PerfilTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'a@a.com', '1234')
        self.alumno = User.objects.create_user('alumno', password='x')

    def test_perfil_creado_automaticamente(self):
        self.assertTrue(Perfil.objects.filter(user=self.alumno).exists())

    def test_requiere_login(self):
        self.assertEqual(self.client.get('/perfil/').status_code, 302)

    def test_alumno_edita_su_perfil_pero_no_el_sitio(self):
        self.client.force_login(self.alumno)
        r = self.client.get('/perfil/')
        self.assertContains(r, 'Racha')
        self.assertNotContains(r, 'Sitio y redes')
        self.client.post('/perfil/', {'seccion': 'perfil', 'first_name': 'Ana', 'last_name': '', 'email': '',
                                      'carrera': 'ISC', 'semestre': '5', 'bio': ''})
        self.alumno.refresh_from_db()
        self.assertEqual((self.alumno.first_name, self.alumno.perfil.carrera), ('Ana', 'ISC'))
        self.assertEqual(self.client.post('/perfil/', {'seccion': 'sitio', 'nombre': 'HACK'}).status_code, 403)

    def _datos_sitio(self, extra_url):
        redes = list(RedSocial.objects.all())
        d = {'seccion': 'sitio', 'nombre': 'Nuevo', 'lema': 'Lema', 'autor': 'Yo', 'whatsapp': '524661074921', 'email': '',
             'redes-TOTAL_FORMS': str(len(redes) + 1), 'redes-INITIAL_FORMS': str(len(redes)),
             'redes-MIN_NUM_FORMS': '0', 'redes-MAX_NUM_FORMS': '1000'}
        for i, r in enumerate(redes):
            d.update({f'redes-{i}-id': r.id, f'redes-{i}-nombre': r.nombre, f'redes-{i}-icono': r.icono,
                      f'redes-{i}-url': r.url, f'redes-{i}-orden': r.orden, f'redes-{i}-activa': 'on'})
        n = len(redes)
        d.update({f'redes-{n}-nombre': 'LinkedIn', f'redes-{n}-icono': 'fab fa-linkedin', f'redes-{n}-url': extra_url,
                  f'redes-{n}-orden': '9', f'redes-{n}-activa': 'on'})
        return d

    def test_admin_edita_sitio_y_se_ve_en_el_footer(self):
        self.client.force_login(self.admin)
        r = self.client.post('/perfil/', self._datos_sitio('https://linkedin.com/in/yo'))
        self.assertEqual(r.status_code, 302)
        h = self.client.get('/').content.decode()
        self.assertIn('Nuevo', h)
        self.assertIn('https://linkedin.com/in/yo', h)

    def test_url_javascript_rechazada(self):
        self.client.force_login(self.admin)
        self.client.post('/perfil/', self._datos_sitio('javascript:alert(1)'))
        self.assertFalse(RedSocial.objects.filter(url__startswith='javascript').exists())
        self.assertEqual(ConfiguracionSitio.actual().nombre, 'MathMaster')

    def test_configuracion_es_unica(self):
        ConfiguracionSitio(nombre='Otro').save()
        self.assertEqual(ConfiguracionSitio.objects.count(), 1)
