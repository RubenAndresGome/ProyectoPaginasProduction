from .base import BaseGenerator, PreguntaGenerada
from .aritmetica import AritmeticaGenerator
from .geometria import GeometriaGenerator
from .trigonometria import TrigonometriaGenerator
from .algebra_basica import AlgebraBasicaGenerator
from .algebra_avanzada import AlgebraAvanzadaGenerator
from .conjuntos import ConjuntosGenerator
from .silogismos import SilogismosGenerator

# Mapeo de categorías del modelo Tema a clases de generadores
GENERADORES_MAP = {
    'aritmetica': AritmeticaGenerator,
    'geometria': GeometriaGenerator,
    'trigonometria': TrigonometriaGenerator,
    'algebra_basica': AlgebraBasicaGenerator,
    'algebra_avanzada': AlgebraAvanzadaGenerator,
    'conjuntos': ConjuntosGenerator,
    'silogismos': SilogismosGenerator,
}
