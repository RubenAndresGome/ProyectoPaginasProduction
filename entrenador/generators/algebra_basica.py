from .base import BaseGenerator, PreguntaGenerada
import random
import math

class AlgebraBasicaGenerator(BaseGenerator):
    """
    Dificultad 1-3: Ecuaciones lineales simples (ax + b = c)
    Dificultad 4-6: Ecuaciones con paréntesis, fracciones simples
    Dificultad 7-8: Ecuaciones de 2do grado (factorizables)
    Dificultad 9-10: Ecuaciones de 2do grado con fórmula general
    """
    def generar(self) -> PreguntaGenerada:
        d = self.dificultad
        if d <= 3:
            return self._lineal_simple()
        elif d <= 6:
            return self._lineal_parentesis()
        elif d <= 8:
            return self._cuadratica_factorizable()
        else:
            return self._cuadratica_general()

    def _lineal_simple(self) -> PreguntaGenerada:
        a = self._rand_int(2, 8)
        x = self._rand_int(-10, 10)
        b = self._rand_int(-20, 20)
        while b == 0:
            b = self._rand_int(-20, 20)
        c = a * x + b

        enunciado = f"\\[ {a}x {'+' if b >= 0 else '-'} {abs(b)} = {c} \\]\n\\[ x = ? \\]"
        expli = f"\\[ {a}x = {c} {'-' if b >= 0 else '+'} {abs(b)} = {c - b} \\]\n\\[ x = \\frac{{{c - b}}}{{{a}}} = {x} \\]"

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(x),
            tolerancia=0.01,
            dificultad=self.dificultad,
            parametros={'a': a, 'x': x, 'b': b, 'c': c},
            explicacion_latex=expli
        )

    def _lineal_parentesis(self) -> PreguntaGenerada:
        a = self._rand_int(2, 5)
        x = self._rand_int(-8, 8)
        b = self._rand_int(1, 5)
        c = self._rand_int(-15, 15)
        while c == 0:
            c = self._rand_int(-15, 15)

        # a(x + b) + c = resultado
        resultado = a * (x + b) + c
        enunciado = f"\\[ {a}(x {'+' if b >= 0 else '-'} {abs(b)}) {'+' if c >= 0 else '-'} {abs(c)} = {resultado} \\]\n\\[ x = ? \\]"

        paso1 = a * b
        paso2 = resultado - c
        paso3 = paso2 - paso1
        expli = (
            f"\\[ {a}x {'+' if paso1 >= 0 else '-'} {abs(paso1)} {'+' if c >= 0 else '-'} {abs(c)} = {resultado} \\]\n"
            f"\\[ {a}x = {resultado} {'-' if c >= 0 else '+'} {abs(c)} = {paso2} \\]\n"
            f"\\[ {a}x = {paso2} {'-' if paso1 >= 0 else '+'} {abs(paso1)} = {paso3} \\]\n"
            f"\\[ x = \\frac{{{paso3}}}{{{a}}} = {x} \\]"
        )

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(x),
            tolerancia=0.01,
            dificultad=self.dificultad,
            parametros={'a': a, 'x': x, 'b': b, 'c': c},
            explicacion_latex=expli
        )

    def _cuadratica_factorizable(self) -> PreguntaGenerada:
        # Generar raíces enteras pequeñas
        r1 = self._rand_int(-6, 6)
        r2 = self._rand_int(-6, 6)
        while r2 == r1:
            r2 = self._rand_int(-6, 6)

        # x^2 - (r1+r2)x + r1*r2 = 0
        suma = -(r1 + r2)
        producto = r1 * r2

        enunciado = f"\\[ x^2 {'+' if suma >= 0 else '-'} {abs(suma)}x {'+' if producto >= 0 else '-'} {abs(producto)} = 0 \\]\n\\[ x = ? \\text{{ (escribe la menor raíz)}} \\]"

        menor = min(r1, r2)
        expli = f"\\[ (x {'-' if r1 >= 0 else '+'} {abs(r1)})(x {'-' if r2 >= 0 else '+'} {abs(r2)}) = 0 \\]\n\\[ x_1 = {r1},\\; x_2 = {r2} \\]"

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(menor),
            tolerancia=0.01,
            dificultad=self.dificultad,
            parametros={'r1': r1, 'r2': r2, 'suma': suma, 'producto': producto},
            explicacion_latex=expli
        )

    def _cuadratica_general(self) -> PreguntaGenerada:
        # ax^2 + bx + c = 0 con discriminante positivo
        a = self._rand_int(1, 3)
        r1 = self._rand_int(-8, 8)
        r2 = self._rand_int(-8, 8)
        while r2 == r1:
            r2 = self._rand_int(-8, 8)

        b = -a * (r1 + r2)
        c = a * r1 * r2

        enunciado = (
            f"\\[ {a if a != 1 else ''}x^2 {'+' if b >= 0 else '-'} {abs(b)}x "
            f"{'+' if c >= 0 else '-'} {abs(c)} = 0 \\]\n"
            f"\\[ x = ? \\text{{ (escribe la menor raíz)}} \\]"
        )

        menor = min(r1, r2)
        discrim = b*b - 4*a*c
        expli = (
            f"\\[ x = \\frac{{-b \\pm \\sqrt{{b^2 - 4ac}}}}{{2a}} \\]\n"
            f"\\[ \\Delta = {b}^2 - 4({a})({c}) = {discrim} \\]\n"
            f"\\[ x_1 = {r1},\\; x_2 = {r2} \\]"
        )

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(menor),
            tolerancia=0.01,
            dificultad=self.dificultad,
            parametros={'a': a, 'b': b, 'c': c, 'r1': r1, 'r2': r2},
            explicacion_latex=expli
        )
