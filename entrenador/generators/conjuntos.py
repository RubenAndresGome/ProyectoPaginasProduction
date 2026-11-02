from .base import BaseGenerator, PreguntaGenerada
import random

class ConjuntosGenerator(BaseGenerator):
    """
    Dificultad 1-3: Unión e intersección de 2 conjuntos
    Dificultad 4-6: Complemento, diferencia, diagramas de Venn
    Dificultad 7-8: Operaciones con 3 conjuntos
    Dificultad 9-10: Cardinalidad, principio de inclusión-exclusión
    """
    def generar(self) -> PreguntaGenerada:
        d = self.dificultad
        if d <= 3:
            return self._union_interseccion()
        elif d <= 6:
            return self._complemento_diferencia()
        elif d <= 8:
            return self._tres_conjuntos()
        else:
            return self._cardinalidad()

    def _union_interseccion(self) -> PreguntaGenerada:
        # Conjuntos con elementos numéricos
        universal = list(range(1, 11))
        tam_a = self._rand_int(2, 5)
        tam_b = self._rand_int(2, 5)
        A = sorted(random.sample(universal, tam_a))
        B = sorted(random.sample(universal, tam_b))
        inter = sorted(set(A) & set(B))
        union = sorted(set(A) | set(B))

        A_str = '\\{' + ', '.join(str(x) for x in A) + '\\}'
        B_str = '\\{' + ', '.join(str(x) for x in B) + '\\}'

        if self._elegir([True, False]):
            # Intersección
            correcta_str = '\\{' + ', '.join(str(x) for x in inter) + '\\}'
            if not inter:
                correcta_str = '\\varnothing'

            enunciado = f"\\[ A = {A_str} \\]\n\\[ B = {B_str} \\]\n\\[ A \\cap B = ? \\]"
            expli = f"\\[ A \\cap B = {correcta_str} \\]"
        else:
            # Unión
            correcta_str = '\\{' + ', '.join(str(x) for x in union) + '\\}'
            enunciado = f"\\[ A = {A_str} \\]\n\\[ B = {B_str} \\]\n\\[ A \\cup B = ? \\]"
            expli = f"\\[ A \\cup B = {correcta_str} \\]"

        # Para respuesta de texto: generar opciones
        opciones = self._opciones_conjunto(correcta_str, A, B, inter, union)

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='opcion_multiple',
            opciones=opciones,
            dificultad=self.dificultad,
            parametros={'A': A, 'B': B},
            explicacion_latex=expli
        )

    def _complemento_diferencia(self) -> PreguntaGenerada:
        universal = list(range(1, 13))
        A = sorted(random.sample(universal, self._rand_int(3, 6)))
        U_str = '\\{' + ', '.join(str(x) for x in universal) + '\\}'
        A_str = '\\{' + ', '.join(str(x) for x in A) + '\\}'
        A_comp = sorted(set(universal) - set(A))
        correcta_str = '\\{' + ', '.join(str(x) for x in A_comp) + '\\}'

        enunciado = f"\\[ U = {U_str} \\]\n\\[ A = {A_str} \\]\n\\[ A^c = ? \\]"
        expli = f"\\[ A^c = U \\setminus A = {correcta_str} \\]"

        opciones = self._opciones_conjunto_simple(correcta_str, A_comp, universal)

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='opcion_multiple',
            opciones=opciones,
            dificultad=self.dificultad,
            parametros={'U': universal, 'A': A},
            explicacion_latex=expli
        )

    def _tres_conjuntos(self) -> PreguntaGenerada:
        U = set(range(1, 11))
        A = set(random.sample(list(U), self._rand_int(2, 4)))
        B = set(random.sample(list(U), self._rand_int(2, 4)))
        C = set(random.sample(list(U), self._rand_int(2, 4)))

        # A ∩ B ∩ C
        resultado = sorted(A & B & C)
        if not resultado:
            resultado = sorted(A & B) or sorted(B & C) or sorted(A & C)

        A_str = '\\{' + ', '.join(str(x) for x in sorted(A)) + '\\}'
        B_str = '\\{' + ', '.join(str(x) for x in sorted(B)) + '\\}'
        C_str = '\\{' + ', '.join(str(x) for x in sorted(C)) + '\\}'
        correcta_str = '\\{' + ', '.join(str(x) for x in resultado) + '\\}'
        if not resultado:
            correcta_str = '\\varnothing'

        enunciado = f"\\[ A = {A_str},\\; B = {B_str},\\; C = {C_str} \\]\n\\[ A \\cap B \\cap C = ? \\]"
        expli = f"\\[ A \\cap B \\cap C = {correcta_str} \\]"

        opciones = self._opciones_conjunto_simple(correcta_str, resultado, list(U))

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='opcion_multiple',
            opciones=opciones,
            dificultad=self.dificultad,
            parametros={'A': list(A), 'B': list(B), 'C': list(C)},
            explicacion_latex=expli
        )

    def _cardinalidad(self) -> PreguntaGenerada:
        # |A ∪ B| = |A| + |B| - |A ∩ B|
        nA = self._rand_int(5, 20)
        nB = self._rand_int(5, 20)
        nAB = self._rand_int(1, min(nA, nB, 8))
        correcta = nA + nB - nAB

        enunciado = (
            f"\\[ |A| = {nA},\\; |B| = {nB},\\; |A \\cap B| = {nAB} \\]\n"
            f"\\[ |A \\cup B| = ? \\]"
        )
        expli = f"\\[ |A \\cup B| = {nA} + {nB} - {nAB} = {correcta} \\]"

        return PreguntaGenerada(
            enunciado_latex=enunciado,
            tipo_respuesta='numerica',
            respuesta_numerica=float(correcta),
            tolerancia=0.01,
            dificultad=self.dificultad,
            parametros={'nA': nA, 'nB': nB, 'nAB': nAB},
            explicacion_latex=expli
        )

    def _opciones_conjunto(self, correcta, A, B, inter, union):
        opciones = [{'texto': correcta, 'texto_latex': correcta, 'es_correcta': True, 'orden': 0}]
        distractores_set = set()
        # Generar distractores creíbles
        A_str = '\\{' + ', '.join(str(x) for x in A) + '\\}'
        B_str = '\\{' + ', '.join(str(x) for x in B) + '\\}'
        inter_str = '\\{' + ', '.join(str(x) for x in inter) + '\\}' if inter else '\\varnothing'
        union_str = '\\{' + ', '.join(str(x) for x in union) + '\\}'

        pool = [A_str, B_str, inter_str, union_str]
        for d in pool:
            if d != correcta and d not in distractores_set:
                distractores_set.add(d)
            if len(distractores_set) >= 3:
                break

        for i, d in enumerate(sorted(distractores_set)[:3]):
            opciones.append({'texto': d, 'texto_latex': d, 'es_correcta': False, 'orden': i + 1})

        random.shuffle(opciones)
        for i, o in enumerate(opciones):
            o['orden'] = i
        return opciones

    def _opciones_conjunto_simple(self, correcta, conjunto, universal):
        opciones = [{'texto': correcta, 'texto_latex': correcta, 'es_correcta': True, 'orden': 0}]
        distractores = set()
        while len(distractores) < 3:
            tam = self._rand_int(0, min(6, len(universal)))
            d = sorted(random.sample(universal, tam))
            d_str = '\\{' + ', '.join(str(x) for x in d) + '\\}' if d else '\\varnothing'
            if d_str != correcta:
                distractores.add(d_str)

        for i, d in enumerate(sorted(distractores)[:3]):
            opciones.append({'texto': d, 'texto_latex': d, 'es_correcta': False, 'orden': i + 1})

        random.shuffle(opciones)
        for i, o in enumerate(opciones):
            o['orden'] = i
        return opciones
        
