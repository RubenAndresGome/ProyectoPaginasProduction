import random

from django.contrib.auth.models import User
from django.test import TestCase

from .generators import GENERADORES_MAP
from .models import Tema


class GeneradoresTests(TestCase):
    """Cada generador debe producir preguntas válidas en todos los niveles."""

    def test_todos_los_generadores_y_niveles(self):
        random.seed(2026)
        for categoria, clase in GENERADORES_MAP.items():
            for nivel in range(1, 11):
                for _ in range(15):
                    with self.subTest(categoria=categoria, nivel=nivel):
                        p = clase(dificultad=nivel, max_dificultad=10).generar()
                        self.assertTrue(p.enunciado_latex.strip())
                        self.assertIn(p.tipo_respuesta, {'numerica', 'opcion_multiple', 'seleccion_multiple', 'texto_libre'})
                        if p.tipo_respuesta == 'numerica':
                            self.assertIsNotNone(p.respuesta_numerica)
                        if p.opciones:
                            correctas = [o for o in p.opciones if o['es_correcta']]
                            self.assertGreaterEqual(len(correctas), 1, 'debe haber al menos una opción correcta')
                            textos = [o['texto'] for o in p.opciones]
                            self.assertEqual(len(textos), len(set(textos)), f'opciones repetidas: {textos}')

    def test_cada_tema_sembrado_tiene_generador(self):
        temas = Tema.objects.filter(activo=True)
        self.assertEqual(temas.count(), 7)
        for t in temas:
            self.assertIn(t.categoria, GENERADORES_MAP)


class PracticarTests(TestCase):
    def test_practicar_tema_genera_pregunta(self):
        u = User.objects.create_user('alumno', password='x')
        self.client.force_login(u)
        r = self.client.get('/entrenador/practicar/aritmetica/')
        self.assertEqual(r.status_code, 200)
