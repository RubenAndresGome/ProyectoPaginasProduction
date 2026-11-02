from .base import BaseGenerator, PreguntaGenerada
import math
import random

class GeometriaGenerator(BaseGenerator):
    """
    Dificultad 1-2: Perímetro de figuras simples
    Dificultad 3-4: Área de figuras simples
    Dificultad 5-6: Área/perímetro compuestos
    Dificultad 7-8: Teorema de Pitágoras
    Dificultad 9-10: Círculos, volumen de prismas
    """
    def generar(self) -> PreguntaGenerada:
        d = self.dificultad
        if d <= 2:
            return self._perimetro()
        elif d <= 4:
            return self._area()
        elif d <= 6:
            return self._compuesto()
        elif d <= 8:
            return self._pitagoras()
        else:
            return self._circulos_volumenes()

    def _perimetro(self) -> PreguntaGenerada:
        fig = self._elegir(['triangulo', 'rectangulo'])
        if fig == 'rectangulo':
            a, b = self._rand_int(3, 15), self._rand_int(3, 15)
            correcta = 2 * (a + b)
            enunciado = (
                f"\\[ \\text{{Perímetro del rectángulo de lados }} {a} \\text{{ cm y }} {b} \\text{{ cm}} \\]\n"
                f"\\[ P = ? \\text{{ cm}} \\]"
            )
            params = {'figura': 'rectangulo', 'a': a, 'b': b}
            expli = f"\\[ P = 2({a}+{b}) = {correcta} \\text{{ cm}} \\]"
        else:
            lados = [self._rand_int(3, 12) for _ in range(3)]
            correcta = sum(lados)
            enunciado = (
                f"\\[ \\text{{Perímetro del triángulo de lados }} {lados[0]},\\; {lados[1]},\\; {lados[2]} \\text{{ cm}} \\]\n"
                f"\\[ P = ? \\text{{ cm}} \\]"
            )
            params = {'figura': 'triangulo', 'lados': lados}
            expli = f"\\[ P = {'+'.join(str(l) for l in lados)} = {correcta} \\text{{ cm}} \\]"

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(correcta),
            tolerancia=0.01,
            dificultad=self.dificultad,
            parametros=params,
            explicacion_latex=expli
        )

    def _area(self) -> PreguntaGenerada:
        fig = self._elegir(['rectangulo', 'triangulo', 'paralelogramo'])
        if fig == 'rectangulo':
            a, b = self._rand_int(3, 20), self._rand_int(3, 20)
            correcta = a * b
            enunciado = f"\\[ \\text{{Área del rectángulo }} {a} \\times {b} \\text{{ cm}}^2 = ? \\]"
            expli = f"\\[ A = {a} \\times {b} = {correcta} \\text{{ cm}}^2 \\]"
            params = {'figura': 'rectangulo', 'a': a, 'b': b}
        elif fig == 'triangulo':
            base = self._rand_int(4, 20)
            altura = self._rand_int(3, 15)
            correcta = (base * altura) / 2
            enunciado = (
                f"\\[ \\text{{Área del triángulo: }} b={base}\\text{{ cm}},\\; h={altura}\\text{{ cm}} \\]\n"
                f"\\[ A = ? \\text{{ cm}}^2 \\]"
            )
            expli = f"\\[ A = \\frac{{{base} \\times {altura}}}{{2}} = {correcta} \\text{{ cm}}^2 \\]"
            params = {'figura': 'triangulo', 'base': base, 'altura': altura}
        else:
            base = self._rand_int(4, 18)
            altura = self._rand_int(3, 12)
            correcta = base * altura
            enunciado = f"\\[ \\text{{Área del paralelogramo: }} b={base},\\; h={altura} \\]\n\\[ A = ? \\]"
            expli = f"\\[ A = {base} \\times {altura} = {correcta} \\]"
            params = {'figura': 'paralelogramo', 'base': base, 'altura': altura}

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(correcta),
            tolerancia=0.01,
            dificultad=self.dificultad,
            parametros=params,
            explicacion_latex=expli
        )

    def _pitagoras(self) -> PreguntaGenerada:
        # Generar triángulo pitagórico
        catetos = [
            (3,4,5), (5,12,13), (6,8,10), (7,24,25),
            (8,15,17), (9,12,15), (9,40,41), (10,24,26),
            (12,16,20), (12,35,37), (15,20,25), (15,36,39),
        ]
        triple = self._elegir(catetos)
        a, b, c = triple
        k = self._rand_int(1, 3)  # Escalar
        a, b, c = a*k, b*k, c*k

        # Pedir la hipotenusa o un cateto
        if self._elegir([True, False]):
            enunciado = (
                f"\\[ \\text{{Triángulo rectángulo: catetos }} {a} \\text{{ y }} {b} \\]\n"
                f"\\[ \\text{{Hipotenusa }} c = ? \\]"
            )
            correcta = c
            expli = f"\\[ c = \\sqrt{{{a}^2 + {b}^2}} = \\sqrt{{{a*a}+{b*b}}} = {c} \\]"
        else:
            enunciado = (
                f"\\[ \\text{{Triángulo rectángulo: hipotenusa }} {c} \\text{{, un cateto }} {a} \\]\n"
                f"\\[ \\text{{Otro cateto }} = ? \\]"
            )
            correcta = b
            expli = f"\\[ b = \\sqrt{{{c}^2 - {a}^2}} = \\sqrt{{{c*c}-{a*a}}} = {b} \\]"

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(correcta),
            tolerancia=0.01,
            dificultad=self.dificultad,
            parametros={'tipo': 'pitagoras', 'a': a, 'b': b, 'c': c},
            explicacion_latex=expli
        )

    def _circulos_volumenes(self) -> PreguntaGenerada:
        if self._elegir([True, False]):
            # Círculo: área o perímetro
            r = self._rand_int(2, 10)
            if self._elegir([True, False]):
                correcta = round(3.14 * r * r, 2)
                enunciado = (
                    f"\\[ \\text{{Área del círculo de radio }} r={r} \\text{{ cm}} \\]\n"
                    f"\\[ A = ? \\text{{ cm}}^2 \\text{{ (usa }} \\pi \\approx 3.14\\text{{)}} \\]"
                )
                expli = f"\\[ A = \\pi r^2 \\approx 3.14 \\cdot {r}^2 = {correcta} \\text{{ cm}}^2 \\]"
            else:
                correcta = round(2 * 3.14 * r, 2)
                enunciado = (
                    f"\\[ \\text{{Perímetro del círculo de radio }} r={r} \\text{{ cm}} \\]\n"
                    f"\\[ P = ? \\text{{ cm}} \\text{{ (usa }} \\pi \\approx 3.14\\text{{)}} \\]"
                )
                expli = f"\\[ P = 2\\pi r \\approx 2 \\cdot 3.14 \\cdot {r} = {correcta} \\text{{ cm}} \\]"
            tolerancia = 0.2
        else:
            # Volumen de prisma rectangular
            l, a, h = self._rand_int(2, 8), self._rand_int(2, 8), self._rand_int(2, 8)
            correcta = l * a * h
            enunciado = (
                f"\\[ \\text{{Volumen del prisma: }} {l} \\times {a} \\times {h} \\text{{ cm}} \\]\n"
                f"\\[ V = ? \\text{{ cm}}^3 \\]"
            )
            expli = f"\\[ V = {l} \\times {a} \\times {h} = {correcta} \\text{{ cm}}^3 \\]"
            tolerancia = 0.01

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(correcta),
            tolerancia=tolerancia,
            dificultad=self.dificultad,
            parametros={},
            explicacion_latex=expli
        )

    def _compuesto(self) -> PreguntaGenerada:
        # Rectángulo con un triángulo en un lado
        ancho = self._rand_int(4, 12)
        alto_rect = self._rand_int(3, 10)
        alto_tri = self._rand_int(2, 6)
        area_rect = ancho * alto_rect
        area_tri = (ancho * alto_tri) / 2
        correcta = area_rect + area_tri
        enunciado = (
            f"\\[ \\text{{Figura compuesta: rectángulo }} {ancho}\\times{alto_rect} "
            f"\\text{{ + triángulo de base }} {ancho} \\text{{ y altura }} {alto_tri} \\]\n"
            f"\\[ \\text{{Área total }} = ? \\]"
        )
        expli = (
            f"\\[ A_{{rect}} = {ancho}\\times{alto_rect}={area_rect} \\]\n"
            f"\\[ A_{{tri}} = \\frac{{{ancho}\\times{alto_tri}}}{{2}}={area_tri} \\]\n"
            f"\\[ A_{{total}} = {area_rect}+{area_tri}={correcta} \\]"
        )
        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(correcta),
            tolerancia=0.01,
            dificultad=self.dificultad,
            parametros={'ancho': ancho, 'alto_rect': alto_rect, 'alto_tri': alto_tri},
            explicacion_latex=expli
        )
