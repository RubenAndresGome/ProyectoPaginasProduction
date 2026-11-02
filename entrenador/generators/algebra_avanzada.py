from .base import BaseGenerator, PreguntaGenerada
import random
import math

class AlgebraAvanzadaGenerator(BaseGenerator):
    """
    Dificultad 1-3: Simplificar expresiones con exponentes
    Dificultad 4-6: Logaritmos básicos
    Dificultad 7-8: Sistema de 2 ecuaciones 2 incógnitas
    Dificultad 9-10: Polinomios (suma, resta, multiplicar)
    """
    def generar(self) -> PreguntaGenerada:
        d = self.dificultad
        if d <= 3:
            return self._exponentes()
        elif d <= 6:
            return self._logaritmos()
        elif d <= 8:
            return self._sistema_2x2()
        else:
            return self._polinomios()

    def _exponentes(self) -> PreguntaGenerada:
        base = self._elegir([2, 3, 5])
        exp1 = self._rand_int(2, 4)
        exp2 = self._rand_int(1, 3)

        # a^m * a^n = a^(m+n)
        if self._elegir([True, False]):
            correcta = exp1 + exp2
            enunciado = f"\\[ {base}^{{{exp1}}} \\cdot {base}^{{{exp2}}} = {base}^{{?}} \\]"
            expli = f"\\[ {base}^{{{exp1}}} \\cdot {base}^{{{exp2}}} = {base}^{{{exp1}+{exp2}}} = {base}^{{{correcta}}} \\]"
        else:
            # a^m / a^n
            correcta = exp1 - exp2
            if correcta < 0:
                correcta = exp2 - exp1
                enunciado = f"\\[ {base}^{{{exp2}}} \\div {base}^{{{exp1}}} = {base}^{{?}} \\]"
                expli = f"\\[ {base}^{{{exp2}}} \\div {base}^{{{exp1}}} = {base}^{{{exp2}-{exp1}}} = {base}^{{{correcta}}} \\]"
            else:
                enunciado = f"\\[ {base}^{{{exp1}}} \\div {base}^{{{exp2}}} = {base}^{{?}} \\]"
                expli = f"\\[ {base}^{{{exp1}}} \\div {base}^{{{exp2}}} = {base}^{{{exp1}-{exp2}}} = {base}^{{{correcta}}} \\]"

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(correcta),
            tolerancia=0.01,
            dificultad=self.dificultad,
            parametros={'base': base, 'exp1': exp1, 'exp2': exp2},
            explicacion_latex=expli
        )

    def _logaritmos(self) -> PreguntaGenerada:
        base = self._elegir([2, 3, 5, 10])
        if base == 2:
            exponente = self._rand_int(1, 8)
        elif base == 3:
            exponente = self._rand_int(1, 5)
        elif base == 5:
            exponente = self._rand_int(1, 4)
        else:
            exponente = self._rand_int(1, 4)

        argumento = base ** exponente

        if self._elegir([True, False]):
            # log_b(arg) = ?
            enunciado = f"\\[ \\log_{{{base}}}({argumento}) = ? \\]"
            expli = f"\\[ \\log_{{{base}}}({argumento}) = {exponente} \\text{{ porque }} {base}^{{{exponente}}} = {argumento} \\]"
            correcta = exponente
        else:
            # log_b(?) = exponente
            enunciado = f"\\[ \\log_{{{base}}}(?) = {exponente} \\]"
            expli = f"\\[ {base}^{{{exponente}}} = {argumento} \\Rightarrow \\log_{{{base}}}({argumento}) = {exponente} \\]"
            correcta = argumento

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(correcta),
            tolerancia=0.01,
            dificultad=self.dificultad,
            parametros={'base': base, 'exponente': exponente, 'argumento': argumento},
            explicacion_latex=expli
        )

    def _sistema_2x2(self) -> PreguntaGenerada:
        # Sistema sencillo con solución entera
        x = self._rand_int(-5, 5)
        y = self._rand_int(-5, 5)

        a1 = self._rand_int(1, 4)
        b1 = self._rand_int(1, 4)
        c1 = a1 * x + b1 * y

        a2 = self._rand_int(1, 4)
        while a2 == a1:
            a2 = self._rand_int(1, 4)
        b2 = self._rand_int(1, 4)
        while b2 == b1:
            b2 = self._rand_int(1, 4)
        c2 = a2 * x + b2 * y

        enunciado = (
            f"\\[ \\begin{{cases}} {a1}x {'+' if b1 >= 0 else '-'} {abs(b1)}y = {c1} \\\\ {a2}x {'+' if b2 >= 0 else '-'} {abs(b2)}y = {c2} \\end{{cases}} \\]\n"
            f"\\[ x = ? \\]"
        )

        expli = f"\\[ x = {x},\\; y = {y} \\]"

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(x),
            tolerancia=0.01,
            dificultad=self.dificultad,
            parametros={'a1': a1, 'b1': b1, 'c1': c1, 'a2': a2, 'b2': b2, 'c2': c2, 'x': x, 'y': y},
            explicacion_latex=expli
        )

    def _polinomios(self) -> PreguntaGenerada:
        # (ax + b)(cx + d) = ? (coeficiente de x^2)
        a = self._rand_int(1, 3)
        b = self._rand_int(-5, 5)
        c = self._rand_int(1, 3)
        d = self._rand_int(-5, 5)

        coef_x2 = a * c
        coef_x = a * d + b * c
        term_indep = b * d

        # Pedir un coeficiente específico
        pedir = self._elegir(['x2', 'x', 'indep'])
        if pedir == 'x2':
            correcta = coef_x2
            enunciado = f"\\[ ({a}x {'+' if b >= 0 else '-'} {abs(b)})({c}x {'+' if d >= 0 else '-'} {abs(d)}) \\]\n\\[ \\text{{Coeficiente de }} x^2 = ? \\]"
            expli = f"\\[ ({a}x {'+' if b >= 0 else '-'} {abs(b)})({c}x {'+' if d >= 0 else '-'} {abs(d)}) = {coef_x2}x^2 {'+' if coef_x >= 0 else '-'} {abs(coef_x)}x {'+' if term_indep >= 0 else '-'} {abs(term_indep)} \\]"
        elif pedir == 'x':
            correcta = coef_x
            enunciado = f"\\[ ({a}x {'+' if b >= 0 else '-'} {abs(b)})({c}x {'+' if d >= 0 else '-'} {abs(d)}) \\]\n\\[ \\text{{Coeficiente de }} x = ? \\]"
            expli = f"\\[ \\text{{Coef. de }} x = {a} \\cdot {d} + {b} \\cdot {c} = {a*d} + {b*c} = {coef_x} \\]"
        else:
            correcta = term_indep
            enunciado = f"\\[ ({a}x {'+' if b >= 0 else '-'} {abs(b)})({c}x {'+' if d >= 0 else '-'} {abs(d)}) \\]\n\\[ \\text{{Término independiente }} = ? \\]"
            expli = f"\\[ \\text{{Término indep.}} = {b} \\cdot {d} = {term_indep} \\]"

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(correcta),
            tolerancia=0.01,
            dificultad=self.dificultad,
            parametros={'a': a, 'b': b, 'c': c, 'd': d},
            explicacion_latex=expli
        )
