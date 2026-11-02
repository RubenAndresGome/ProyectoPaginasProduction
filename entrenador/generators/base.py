from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
import random

@dataclass
class PreguntaGenerada:
    """
    Estructura universal que devuelve cualquier generador.
    La vista no necesita saber qué tipo de problema es.
    """
    enunciado_latex: str
    tipo_respuesta: str  # 'numerica', 'opcion_multiple', 'seleccion_multiple'
    respuesta_numerica: Optional[float] = None
    tolerancia: float = 0.01
    opciones: List[dict] = field(default_factory=list)
    # Cada opción: {'texto': str, 'texto_latex': str, 'es_correcta': bool, 'orden': int}
    dificultad: int = 1
    parametros: dict = field(default_factory=dict)
    # Hints/Explicación para el resultado
    explicacion_latex: str = ""

class BaseGenerator(ABC):
    """
    Todos los generadores heredan de esta clase.
    """
    def __init__(self, dificultad: int = 1, max_dificultad: int = 10):
        self.dificultad = min(max(dificultad, 1), max_dificultad)
        self.max_dificultad = max_dificultad

    @abstractmethod
    def generar(self) -> PreguntaGenerada:
        """Genera una pregunta aleatoria para la dificultad actual."""
        pass

    def _rand_int(self, min_val: int, max_val: int) -> int:
        return random.randint(min_val, max_val)

    def _rand_float(self, min_val: float, max_val: float, decimales: int = 2) -> float:
        return round(random.uniform(min_val, max_val), decimales)

    def _elegir(self, opciones: list) -> any:
        return random.choice(opciones)

    def _generar_distractores_numericos(self, correcta: float, cantidad: int = 3) -> List[float]:
        """
        Genera opciones incorrectas creíbles para opción múltiple.
        Estrategia: variar la correcta en ±10-40%
        """
        distractores = set()
        intentos = 0
        while len(distractores) < cantidad and intentos < 100:
            intentos += 1
            if correcta == 0:
                d = self._rand_int(1, 10) * self._elegir([-1, 1])
            else:
                variacion = abs(correcta) * random.uniform(0.1, 0.4) * self._elegir([-1, 1])
                d = round(correcta + variacion, 2)
                # Si es entero el resultado original, preferir distractores enteros
                if isinstance(correcta, int) or (isinstance(correcta, float) and correcta.is_integer()):
                    d = round(d)
            if d != correcta and d not in distractores:
                distractores.add(d)
        return list(distractores)
