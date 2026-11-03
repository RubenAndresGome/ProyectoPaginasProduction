from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase

CLAVE_PRUEBA = 'ClaveSegura#2026'  # solo para pruebas · secretos: permitido


class SeguridadAutenticacionTests(TestCase):
    def setUp(self):
        cache.clear()
        User.objects.create_user('ana', password=CLAVE_PRUEBA)

    def test_login_correcto(self):
        r = self.client.post('/auth/login/', {'username': 'ana', 'password': CLAVE_PRUEBA})
        self.assertRedirects(r, '/inicio/', fetch_redirect_response=False)

    def test_bloqueo_tras_5_fallos(self):
        for _ in range(5):
            self.client.post('/auth/login/', {'username': 'ana', 'password': 'mala'})
        r = self.client.post('/auth/login/', {'username': 'ana', 'password': CLAVE_PRUEBA}, follow=True)
        self.assertContains(r, 'Demasiados intentos')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_next_no_permite_redireccion_abierta(self):
        r = self.client.post('/auth/login/?next=https://evil.com/', {'username': 'ana', 'password': CLAVE_PRUEBA,
                                                                    'next': 'https://evil.com/'})
        self.assertFalse(r['Location'].startswith('https://evil.com'))
        self.client.logout()
        r = self.client.post('/auth/login/', {'username': 'ana', 'password': CLAVE_PRUEBA, 'next': '/perfil/'})
        self.assertEqual(r['Location'], '/perfil/')

    def test_logout_solo_post(self):
        self.client.login(username='ana', password=CLAVE_PRUEBA)
        self.assertEqual(self.client.get('/auth/logout/').status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)
        self.client.post('/auth/logout/')
        self.assertNotIn('_auth_user_id', self.client.session)


class CabecerasTests(TestCase):
    def test_cabeceras_de_seguridad(self):
        r = self.client.get('/')
        csp = r.headers.get('Content-Security-Policy', '')
        self.assertIn("object-src 'none'", csp)
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertEqual(r.headers.get('X-Frame-Options'), 'DENY')
        self.assertEqual(r.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(r.headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')
