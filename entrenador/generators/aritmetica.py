from .base import BaseGenerator, PreguntaGenerada
import random

class AritmeticaGenerator(BaseGenerator):
    """
    Dificultad 1-3: Suma y resta
    Dificultad 4-6: Multiplicación y división exacta
    Dificultad 7-8: Operaciones combinadas
    Dificultad 9-10: Potencias, raíces, operaciones con decimales
    """
    def generar(self) -> PreguntaGenerada:
        d = self.dificultad

        if d <= 3:
            return self._suma_resta()
        elif d <= 6:
            return self._multiplicacion_division()
        elif d <= 8:
            return self._combinadas()
        else:
            return self._potencias_raices()

    def _suma_resta(self) -> PreguntaGenerada:
        d = self.dificultad
        if d == 1:
            a, b = self._rand_int(1, 10), self._rand_int(1, 10)
        elif d == 2:
            a, b = self._rand_int(10, 99), self._rand_int(1, 50)
        else:
            a, b = self._rand_int(100, 999), self._rand_int(10, 999)

        op = self._elegir(['+', '-'])
        if op == '-' and b > a:
            a, b = b, a  # Evitar negativos en dificultad baja

        correcta = a + b if op == '+' else a - b
        enunciado = f"\\[ {a} {op} {b} = ? \\]"

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(correcta),
            tolerancia=0.01,
            dificultad=self.dificultad,
            parametros={'a': a, 'b': b, 'op': op},
            explicacion_latex=f"\\[ {a} {op} {b} = {correcta} \\]"
        )

    def _multiplicacion_division(self) -> PreguntaGenerada:
        d = self.dificultad
        if d <= 5:
            a = self._rand_int(2, 12)
            b = self._rand_int(2, 12)
            correcta = a * b
            enunciado = f"\\[ {a} \\times {b} = ? \\]"
            parametros = {'a': a, 'b': b, 'op': '*'}
        else:
            # División exacta: generar resultado y divisor, calcular dividendo
            b = self._rand_int(2, 12)
            resultado = self._rand_int(2, 15)
            a = b * resultado
            correcta = resultado
            enunciado = f"\\[ {a} \\div {b} = ? \\]"
            parametros = {'a': a, 'b': b, 'op': '/'}

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(correcta),
            tolerancia=0.01,
            dificultad=self.dificultad,
            parametros=parametros,
            explicacion_latex=f"\\[ \\text{{Resultado}} = {correcta} \\]"
        )

    def _combinadas(self) -> PreguntaGenerada:
        # Ej: (3 + 4) × 2 - 1
        a = self._rand_int(2, 10)
        b = self._rand_int(2, 10)
        c = self._rand_int(2, 5)
        d = self._rand_int(1, 10)
        correcta = (a + b) * c - d
        enunciado = f"\\[ ({a} + {b}) \\times {c} - {d} = ? \\]"
        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(correcta),
            dificultad=self.dificultad,
            parametros={'a': a, 'b': b, 'c': c, 'd': d},
            explicacion_latex=f"\\[ ({a}+{b})={a+b},\\; {a+b}\\times{c}={(a+b)*c},\\; {(a+b)*c}-{d}={correcta} \\]"
        )

    def _potencias_raices(self) -> PreguntaGenerada:
        base = self._rand_int(2, 9)
        exp = self._rand_int(2, 4)
        correcta = base ** exp

        if self._elegir([True, False]):
            enunciado = f"\\[ {base}^{{{exp}}} = ? \\]"
            parametros = {'tipo': 'potencia', 'base': base, 'exp': exp}
            explicacion = f"\\[ {base}^{{{exp}}} = {correcta} \\]"
        else:
            # Raíz cuadrada de un cuadrado perfecto
            base = self._rand_int(2, 15)
            correcta = base
            radicando = base * base
            enunciado = f"\\[ \\sqrt{{{radicando}}} = ? \\]"
            parametros = {'tipo': 'raiz', 'radicando': radicando}
            explicacion = f"\\[ \\sqrt{{{radicando}}} = {correcta} \\]"

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(correcta),
            dificultad=self.dificultad,
            parametros=parametros,
            explicacion_latex=explicacion
        )
