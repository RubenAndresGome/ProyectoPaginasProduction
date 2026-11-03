from django.contrib.auth.models import User
from django.test import TestCase

from .models import Article


class SitioTests(TestCase):
    def test_portada_y_paginas_publicas(self):
        for url in ('/', '/contacto/', '/blog/publicaciones/', '/auth/login/', '/auth/registro/', '/hola-mundo/'):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        self.assertContains(self.client.get('/'), 'Empezar a practicar')

    def test_menu_administrar_solo_staff(self):
        self.assertNotContains(self.client.get('/'), 'Administrar')
        self.client.force_login(User.objects.create_superuser('admin', 'a@a.com', '1234'))
        self.assertContains(self.client.get('/'), 'Administrar')


class ArticulosCrudTests(TestCase):
    def setUp(self):
        self.art = Article.objects.create(title='T', content='C')

    def test_crud_protegido(self):
        u = User.objects.create_user('alumno', password='x')
        self.client.force_login(u)
        self.assertEqual(self.client.get('/crear-articulo/').status_code, 302)
        self.assertEqual(self.client.post(f'/borrar-articulo/{self.art.id}/').status_code, 302)
        self.assertTrue(Article.objects.filter(id=self.art.id).exists())

    def test_borrar_exige_post(self):
        self.client.force_login(User.objects.create_superuser('admin', 'a@a.com', '1234'))
        self.assertEqual(self.client.get(f'/borrar-articulo/{self.art.id}/').status_code, 405)
        self.client.post(f'/borrar-articulo/{self.art.id}/')
        self.assertFalse(Article.objects.filter(id=self.art.id).exists())
