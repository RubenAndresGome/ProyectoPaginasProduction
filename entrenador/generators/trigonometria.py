from .base import BaseGenerator, PreguntaGenerada
import math
import random

class TrigonometriaGenerator(BaseGenerator):
    """
    Dificultad 1-3: Razones trig en triángulos rectángulos (ángulos especiales)
    Dificultad 4-6: Encontrar lados usando razones trig
    Dificultad 7-8: Identidades trigonométricas básicas
    Dificultad 9-10: Ecuaciones trigonométricas simples
    """
    ANGULOS_ESPECIALES = {
        0:   (0, 1, 0),
        30:  (1/2, math.sqrt(3)/2, 1/math.sqrt(3)),
        45:  (math.sqrt(2)/2, math.sqrt(2)/2, 1),
        60:  (math.sqrt(3)/2, 1/2, math.sqrt(3)),
        90:  (1, 0, None),
    }

    def generar(self) -> PreguntaGenerada:
        d = self.dificultad
        if d <= 3:
            return self._razon_directa()
        elif d <= 6:
            return self._encontrar_lado()
        elif d <= 8:
            return self._identidad()
        else:
            return self._ecuacion_simple()

    def _razon_directa(self) -> PreguntaGenerada:
        angulo = self._elegir([30, 45, 60])
        razon = self._elegir(['sin', 'cos', 'tan'])
        sen, cos, tan = self.ANGULOS_ESPECIALES[angulo]

        if razon == 'sin':
            simbolo = '\\sin'
        elif razon == 'cos':
            simbolo = '\\cos'
        else:
            simbolo = '\\tan'

        # Formatear el valor correcto como fracción LaTeX
        correcta_str = self._formatear_especial(angulo, razon)

        # Generar opciones
        opciones = self._opciones_angular(angulo, razon)

        enunciado = f"\\[ {simbolo}({angulo}^\\circ) = ? \\]"

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='opcion_multiple',
            opciones=opciones,
            dificultad=self.dificultad,
            parametros={'angulo': angulo, 'razon': razon},
            explicacion_latex=f"\\[ {simbolo}({angulo}^\\circ) = {correcta_str} \\]"
        )

    def _encontrar_lado(self) -> PreguntaGenerada:
        angulo = self._elegir([30, 45, 60])
        sen, cos, tan = self.ANGULOS_ESPECIALES[angulo]
        razon = self._elegir(['sin', 'cos', 'tan'])

        # Hipotenusa conocida, encontrar cateto
        h = self._rand_int(4, 20)
        if razon == 'sin':
            cateto = round(h * sen, 2)
            enunciado = (
                f"\\[ \\text{{Triángulo rectángulo, hipotenusa }}={h}\\text{{, ángulo }}={angulo}^\\circ \\]\n"
                f"\\[ \\text{{Cateto opuesto }} = ? \\]"
            )
            expli = f"\\[ \\sin({angulo}^\\circ) = \\frac{{\\text{{opuesto}}}}{{{h}}} \\Rightarrow \\text{{opuesto}} = {h} \\times {self._formatear_especial(angulo, 'sin')} = {cateto} \\]"
        elif razon == 'cos':
            cateto = round(h * cos, 2)
            enunciado = (
                f"\\[ \\text{{Triángulo rectángulo, hipotenusa }}={h}\\text{{, ángulo }}={angulo}^\\circ \\]\n"
                f"\\[ \\text{{Cateto adyacente }} = ? \\]"
            )
            expli = f"\\[ \\cos({angulo}^\\circ) = \\frac{{\\text{{ady}}}}{{{h}}} \\Rightarrow \\text{{ady}} = {h} \\times {self._formatear_especial(angulo, 'cos')} = {cateto} \\]"
        else:
            # Cateto adyacente conocido, encontrar opuesto
            ady = self._rand_int(3, 15)
            cateto = round(ady * tan, 2)
            enunciado = (
                f"\\[ \\text{{Triángulo rectángulo, cateto adyacente }}={ady}\\text{{, ángulo }}={angulo}^\\circ \\]\n"
                f"\\[ \\text{{Cateto opuesto }} = ? \\]"
            )
            expli = f"\\[ \\tan({angulo}^\\circ) = \\frac{{\\text{{opuesto}}}}{{{ady}}} \\Rightarrow \\text{{opuesto}} = {ady} \\times {self._formatear_especial(angulo, 'tan')} = {cateto} \\]"

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=cateto,
            tolerancia=0.1,
            dificultad=self.dificultad,
            parametros={'angulo': angulo, 'razon': razon},
            explicacion_latex=expli
        )

    def _identidad(self) -> PreguntaGenerada:
        identidades = [
            {
                'enunciado': r'\[ \sin^2(\theta) + \cos^2(\theta) = ? \]',
                'correcta': '1',
                'opciones': ['0', '1', r'\sin(\theta)', r'\cos(\theta)'],
                'expli': r'\[ \sin^2\theta + \cos^2\theta = 1 \text{ (identidad fundamental)} \]'
            },
            {
                'enunciado': r'\[ \tan(\theta) = \frac{\sin(\theta)}{?} \]',
                'correcta': r'\cos(\theta)',
                'opciones': [r'\cos(\theta)', r'\sin(\theta)', r'\tan(\theta)', '1'],
                'expli': r'\[ \tan\theta = \frac{\sin\theta}{\cos\theta} \]'
            },
            {
                'enunciado': r'\[ 1 + \tan^2(\theta) = ? \]',
                'correcta': r'\sec^2(\theta)',
                'opciones': [r'\csc^2(\theta)', r'\sec^2(\theta)', '1', r'\cot^2(\theta)'],
                'expli': r'\[ 1 + \tan^2\theta = \sec^2\theta \]'
            },
        ]
        iden = self._elegir(identidades)
        opciones = []
        indices = list(range(len(iden['opciones'])))
        random.shuffle(indices)
        for i, idx in enumerate(indices):
            es_correcta = (iden['opciones'][idx] == iden['correcta'])
            opciones.append({
                'texto': iden['opciones'][idx],
                'texto_latex': iden['opciones'][idx],
                'es_correcta': es_correcta,
                'orden': i,
            })

        return PreguntaGenerada(
            enunciado_latex=iden['enunciado'],
            tipo_respuesta='opcion_multiple',
            opciones=opciones,
            dificultad=self.dificultad,
            parametros={'tipo': 'identidad'},
            explicacion_latex=iden['expli']
        )

    def _ecuacion_simple(self) -> PreguntaGenerada:
        # sin(x) = 1/2, x en [0, 360]
        angulo = self._elegir([30, 45, 60])
        razon = self._elegir(['sin', 'cos'])

        if razon == 'sin':
            soluciones = [angulo, 180 - angulo]
            enunciado = f"\\[ \\sin(x) = {self._formatear_especial(angulo, 'sin')}, \\quad x \\in [0^\\circ, 360^\\circ] \\]\n\\[ x = ? \\text{{ (escribe la menor solución en grados)}} \\]"
        else:
            soluciones = [angulo, 360 - angulo]
            enunciado = f"\\[ \\cos(x) = {self._formatear_especial(angulo, 'cos')}, \\quad x \\in [0^\\circ, 360^\\circ] \\]\n\\[ x = ? \\text{{ (escribe la menor solución en grados)}} \\]"

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(soluciones[0]),
            tolerancia=0.5,
            dificultad=self.dificultad,
            parametros={'razon': razon, 'angulo': angulo, 'soluciones': soluciones},
            explicacion_latex=f"\\[ x = {soluciones[0]}^\\circ \\text{{ o }} x = {soluciones[1]}^\\circ \\]"
        )

    def _formatear_especial(self, angulo, razon):
        fracciones = {
            (30, 'sin'): r'\frac{1}{2}',
            (30, 'cos'): r'\frac{\sqrt{3}}{2}',
            (30, 'tan'): r'\frac{\sqrt{3}}{3}',
            (45, 'sin'): r'\frac{\sqrt{2}}{2}',
            (45, 'cos'): r'\frac{\sqrt{2}}{2}',
            (45, 'tan'): '1',
            (60, 'sin'): r'\frac{\sqrt{3}}{2}',
            (60, 'cos'): r'\frac{1}{2}',
            (60, 'tan'): r'\sqrt{3}',
        }
        return fracciones.get((angulo, razon), str(0))

    def _opciones_angular(self, angulo, razon):
        """Genera 4 opciones para razón trig, una correcta."""
        correcta = self._formatear_especial(angulo, razon)

        # Pool de distractores comunes
        todos = {
            'sin': [r'\frac{1}{2}', r'\frac{\sqrt{2}}{2}', r'\frac{\sqrt{3}}{2}', '0', '1'],
            'cos': [r'\frac{1}{2}', r'\frac{\sqrt{2}}{2}', r'\frac{\sqrt{3}}{2}', '0', '1'],
            'tan': [r'\frac{\sqrt{3}}{3}', '1', r'\sqrt{3}', '0'],
        }
        pool = [x for x in todos[razon] if x != correcta]
        distractores = random.sample(pool, min(3, len(pool)))

        opciones_list = [correcta] + distractores
        random.shuffle(opciones_list)

        return [
            {'texto': opt, 'texto_latex': opt, 'es_correcta': opt == correcta, 'orden': i}
            for i, opt in enumerate(opciones_list)
        ]
