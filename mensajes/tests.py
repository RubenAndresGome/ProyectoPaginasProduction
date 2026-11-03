import json

from django.contrib.auth.models import User
from django.test import Client, TestCase

from entrenador.models import Tema, TemaProgreso

from .models import Mensaje

FORM = {'nombre': 'Ana', 'email': 'ana@x.com', 'asunto': 'Hola', 'cuerpo': 'Prueba'}


class ContactoTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'a@a.com', '1234')
        self.alumno = User.objects.create_user('alumno', password='x', first_name='Luis')

    def test_envio_y_honeypot(self):
        self.client.post('/mensajes/enviar/', FORM)
        self.client.post('/mensajes/enviar/', {**FORM, 'asunto': 'spam', 'sitio_web': 'http://spam'})
        self.assertEqual(list(Mensaje.objects.values_list('asunto', flat=True)), ['Hola'])

    def test_limite_por_hora(self):
        for i in range(5):
            self.client.post('/mensajes/enviar/', {**FORM, 'asunto': f'm{i}'})
        self.assertEqual(Mensaje.objects.count(), 3)

    def test_flujo_bandeja_y_respuesta(self):
        alu = Client(); alu.force_login(self.alumno)
        alu.post('/mensajes/enviar/', FORM)
        m = Mensaje.objects.get()
        self.assertEqual(m.usuario, self.alumno)
        self.assertEqual(alu.get('/mensajes/bandeja/').status_code, 302)
        self.client.force_login(self.admin)
        self.client.get(f'/mensajes/bandeja/{m.id}/')
        self.client.post(f'/mensajes/bandeja/{m.id}/', {'respuesta': 'Respuesta'})
        m.refresh_from_db()
        self.assertTrue(m.leido and m.respondido)
        self.assertContains(alu.get('/mensajes/mis-mensajes/'), 'Respuesta')


class TutorTests(TestCase):
    def preguntar(self, texto, cliente=None):
        return (cliente or self.client).post('/mensajes/tutor/', json.dumps({'texto': texto}),
                                             content_type='application/json').json()

    def test_recomienda_el_tema_mas_debil(self):
        u = User.objects.create_user('alumno', password='x')
        TemaProgreso.objects.create(usuario=u, tema=Tema.objects.get(slug='trigonometria'), total_intentos=10, total_aciertos=3)
        TemaProgreso.objects.create(usuario=u, tema=Tema.objects.get(slug='aritmetica'), total_intentos=10, total_aciertos=9)
        c = Client(); c.force_login(u)
        d = self.preguntar('¿Qué me recomiendas?', c)
        self.assertIn('Trigonometría', d['texto'])
        self.assertIn('/practicar/trigonometria/', d['enlaces'][0]['url'])

    def test_detecta_temas_sin_acentos_ni_mayusculas(self):
        self.assertIn('Álgebra Avanzada', self.preguntar('LOGARITMOS')['texto'])
        self.assertIn('Geometría', self.preguntar('explícame pitagoras')['texto'])

    def test_respuesta_por_defecto_y_solo_post(self):
        self.assertIn('No estoy seguro', self.preguntar('asdfgh')['texto'])
        self.assertEqual(self.client.get('/mensajes/tutor/').status_code, 405)
