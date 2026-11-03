import base64
import json
import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

from . import bloques as reglas
from .markdown import articulo_a_md
from .models import Articulo_Page, Bloque, MeGusta, Plantilla, VistaArticulo

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==')
MEDIA_TMP = tempfile.mkdtemp()


class LimpiezaBloquesTests(TestCase):
    def test_urls_peligrosas(self):
        self.assertEqual(reglas.limpiar('enlace', {'url': 'javascript:alert(1)'})['url'], '')
        self.assertEqual(reglas.limpiar('enlace', {'url': '//evil.com'})['url'], '')
        self.assertEqual(reglas.limpiar('enlace', {'url': '/entrenador/'})['url'], '/entrenador/')
        self.assertEqual(reglas.limpiar('video', {'url': 'https://youtu.be/abcdefghijk'})['url'], 'https://youtu.be/abcdefghijk')

    def test_claves_extra_y_valores_fuera_de_rango(self):
        self.assertEqual(reglas.limpiar('parrafo', {'texto': 'x', 'hack': 1}), {'texto': 'x'})
        self.assertEqual(reglas.limpiar('aviso', {'variante': 'hack'})['variante'], 'info')
        self.assertEqual(reglas.limpiar('titulo', {'nivel': '9'})['nivel'], 2)

    def test_tabla_normalizada(self):
        t = reglas.limpiar('tabla', {'columnas': ['A', 'B'], 'filas': [['1'], ['1', '2', '3'], 'no-lista']})
        self.assertEqual(t['filas'], [['1', ''], ['1', '2'], ['', '']])

    def test_cada_default_es_valido(self):
        for tipo, datos in reglas.DEFAULTS.items():
            self.assertEqual(reglas.limpiar(tipo, datos), reglas.limpiar(tipo, reglas.limpiar(tipo, datos)))


class Base(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'a@a.com', '1234')
        self.alumno = User.objects.create_user('alumno', password='x')
        self.adm = Client(); self.adm.force_login(self.admin)
        self.alu = Client(); self.alu.force_login(self.alumno)
        self.anon = Client()

    def crear(self, plantilla='tema-matematico', titulo='Prueba'):
        p = Plantilla.objects.get(slug=plantilla)
        self.adm.post('/blog/editor/nuevo/', {'titulo': titulo, 'plantilla': p.pk})
        return Articulo_Page.objects.get(title=titulo)

    def api(self, art, ruta, datos, cliente=None):
        return (cliente or self.adm).post(f'/blog/editor/{art.id}/api/{ruta}', json.dumps(datos),
                                          content_type='application/json')


class EditorTests(Base):
    def test_permisos(self):
        for c in (self.anon, self.alu):
            self.assertEqual(c.get('/blog/editor/').status_code, 302)
        self.assertEqual(self.adm.get('/blog/editor/').status_code, 200)

    def test_crear_desde_plantilla_es_borrador(self):
        art = self.crear()
        self.assertFalse(art.publicado)
        self.assertEqual(art.bloques.count(), len(Plantilla.objects.get(slug='tema-matematico').estructura))
        self.assertEqual(self.anon.get(f'/blog/publicacion/{art.id}/').status_code, 404)
        self.assertEqual(self.adm.get(f'/blog/publicacion/{art.id}/').status_code, 200)

    def test_crear_en_blanco(self):
        self.adm.post('/blog/editor/nuevo/', {'titulo': 'Vacío', 'plantilla': ''})
        self.assertEqual(Articulo_Page.objects.get(title='Vacío').bloques.count(), 0)

    def test_guardar_escapa_html(self):
        art = self.crear()
        b = art.bloques.filter(tipo='parrafo').first()
        d = self.api(art, f'bloque/{b.id}/', {'datos': {'texto': '<script>alert(1)</script>'}}).json()
        self.assertIn('&lt;script&gt;', d['preview'])
        self.assertNotIn('<script>alert', d['preview'])

    def test_agregar_insertar_reordenar_borrar(self):
        art = self.crear()
        primero = art.bloques.first()
        self.api(art, 'agregar/', {'tipo': 'cita', 'despues_de': primero.id})
        self.assertEqual(list(art.bloques.values_list('tipo', flat=True))[1], 'cita')
        self.assertEqual(self.api(art, 'agregar/', {'tipo': 'hack'}).status_code, 400)
        ids = list(art.bloques.values_list('id', flat=True))[::-1]
        self.api(art, 'reordenar/', {'ids': ids})
        self.assertEqual(list(art.bloques.values_list('id', flat=True)), ids)
        self.assertEqual(self.api(art, 'reordenar/', {'ids': ids[:-1]}).status_code, 400)
        self.api(art, f'bloque/{ids[0]}/borrar/', {})
        self.assertFalse(Bloque.objects.filter(id=ids[0]).exists())

    def test_no_edita_bloques_de_otro_articulo(self):
        a, b = self.crear(titulo='A'), self.crear(titulo='B')
        ajeno = b.bloques.first()
        self.assertEqual(self.api(a, f'bloque/{ajeno.id}/', {'datos': {}}).status_code, 404)

    def test_alumno_no_usa_api_y_csrf_exigido(self):
        art = self.crear()
        self.assertEqual(self.api(art, 'meta/', {'titulo': 'hack'}, self.alu).status_code, 302)
        c = Client(enforce_csrf_checks=True); c.force_login(self.admin)
        self.assertEqual(self.api(art, 'meta/', {'titulo': 'x'}, c).status_code, 403)

    def test_meta_y_publicar(self):
        art = self.crear()
        self.api(art, 'meta/', {'titulo': 'Nuevo', 'publicado': True, 'categorias': []})
        art.refresh_from_db()
        self.assertEqual((art.title, art.publicado), ('Nuevo', True))
        self.assertEqual(self.api(art, 'meta/', {'titulo': '   '}).status_code, 400)

    @override_settings(MEDIA_ROOT=MEDIA_TMP)
    def test_imagenes(self):
        art = self.crear()
        bid = self.api(art, 'agregar/', {'tipo': 'imagen'}).json()['bloque']['id']
        r = self.adm.post(f'/blog/editor/{art.id}/api/bloque/{bid}/',
                          {'imagen': SimpleUploadedFile('p.png', PNG, 'image/png'), 'datos': '{"pie": "Pie"}'})
        self.assertTrue(r.json()['bloque']['imagen'])
        r = self.adm.post(f'/blog/editor/{art.id}/api/bloque/{bid}/',
                          {'imagen': SimpleUploadedFile('x.exe', b'MZ', 'application/x-msdownload'), 'datos': '{}'})
        self.assertEqual(r.status_code, 400)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_TMP, ignore_errors=True)
        super().tearDownClass()


class LectoresTests(Base):
    def setUp(self):
        super().setUp()
        self.art = self.crear()
        self.art.publicado = True
        self.art.save()
        self.url = f'/blog/publicacion/{self.art.id}/'

    def test_blog_publico_y_busqueda_en_bloques(self):
        self.assertEqual(self.anon.get('/blog/publicaciones/').status_code, 200)
        h = self.anon.get('/blog/publicaciones/', {'q': 'a^2 + b^2'}).content.decode()
        self.assertIn('Prueba', h)

    def test_vistas_unicas_sin_staff(self):
        for _ in range(3):
            self.anon.get(self.url)
        self.alu.get(self.url); self.adm.get(self.url)
        self.assertEqual(VistaArticulo.objects.filter(articulo=self.art).count(), 2)

    def test_me_gusta(self):
        self.assertEqual(self.anon.post(self.url + 'me-gusta/').status_code, 401)
        self.assertTrue(self.alu.post(self.url + 'me-gusta/').json()['me_gusta'])
        self.assertFalse(self.alu.post(self.url + 'me-gusta/').json()['me_gusta'])
        self.assertEqual(MeGusta.objects.count(), 0)

    def test_compartir_una_vez_por_sesion(self):
        self.anon.post(self.url + 'compartir/'); self.anon.post(self.url + 'compartir/'); self.alu.post(self.url + 'compartir/')
        self.art.refresh_from_db()
        self.assertEqual(self.art.veces_compartido, 2)

    def test_markdown(self):
        r = self.anon.get(self.url + 'markdown/')
        self.assertIn('attachment', r['Content-Disposition'])
        md = r.content.decode()
        self.assertTrue(md.startswith('---\ntitle: "Prueba"'))
        self.assertIn('$$\na^2 + b^2 = c^2\n$$', md)
        self.assertIn('http://testserver/entrenador/', md)

    def test_markdown_de_borrador_solo_staff(self):
        self.art.publicado = False; self.art.save()
        self.assertEqual(self.anon.get(self.url + 'markdown/').status_code, 404)
        self.assertEqual(self.adm.get(self.url + 'markdown/').status_code, 200)

    def test_metricas_solo_staff(self):
        self.assertEqual(self.alu.get('/blog/editor/metricas/').status_code, 302)
        self.assertContains(self.adm.get('/blog/editor/metricas/'), 'Vistas totales')

    def test_markdown_tabla_escapa_pipes(self):
        b = Bloque.objects.create(articulo=self.art, tipo='tabla', orden=99,
                                  datos={'columnas': ['a|b'], 'filas': [['x|y']]})
        self.assertIn('a\\|b', articulo_a_md(self.art))
        b.delete()
