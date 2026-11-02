"""Definición de las plantillas base. La usan la migración 0007 y el comando blog_demo."""

def T(texto, nivel=2): return {"tipo": "titulo", "datos": {"texto": texto, "nivel": nivel}}
def P(texto): return {"tipo": "parrafo", "datos": {"texto": texto}}
def L(items, ordenada=False): return {"tipo": "lista", "datos": {"items": items, "ordenada": ordenada}}
def I(pie): return {"tipo": "imagen", "datos": {"pie": pie, "alt": pie}}
def A(texto, variante="info"): return {"tipo": "aviso", "datos": {"texto": texto, "variante": variante}}
def F(latex): return {"tipo": "formula", "datos": {"latex": latex}}
def E(url, texto, descripcion=""): return {"tipo": "enlace", "datos": {"url": url, "texto": texto, "descripcion": descripcion}}
def C(texto, autor=""): return {"tipo": "cita", "datos": {"texto": texto, "autor": autor}}
def TB(columnas, filas): return {"tipo": "tabla", "datos": {"columnas": columnas, "filas": filas}}

PLANTILLAS = [
    {"nombre": "Tutorial paso a paso", "slug": "tutorial", "tipo": "tutorial", "icono": "list-check",
     "descripcion": "Enseña a lograr un resultado concreto en pasos ordenados.",
     "estructura": [P("Qué vas a lograr y por qué es útil."),
                    T("Lo que necesitas"), L(["Requisito 1", "Requisito 2"]),
                    T("Pasos"), L(["Primer paso", "Segundo paso", "Tercer paso"], ordenada=True),
                    I("Captura del resultado"),
                    A("Error común y cómo evitarlo.", "alerta"),
                    T("Resultado"), P("Resumen de lo logrado y siguiente paso sugerido.")]},
    {"nombre": "Lista (listicle)", "slug": "lista", "tipo": "lista", "icono": "list-ol",
     "descripcion": "N elementos fáciles de escanear: consejos, herramientas, ejemplos.",
     "estructura": [P("Introducción: qué contiene la lista y para quién es."),
                    T("1. Primer elemento"), P("Por qué importa."),
                    T("2. Segundo elemento"), P("Por qué importa."),
                    T("3. Tercer elemento"), P("Por qué importa."),
                    T("Conclusión"), P("Cuál elegir según tu caso.")]},
    {"nombre": "Caso de estudio", "slug": "caso-de-estudio", "tipo": "caso", "icono": "magnifying-glass-chart",
     "descripcion": "Problema → solución → resultados con datos reales.",
     "estructura": [T("Contexto"), P("Quién, dónde y cuándo."),
                    T("El problema"), P("Qué no funcionaba y cómo se medía."),
                    T("La solución"), P("Qué se hizo y por qué."), I("Diagrama o evidencia"),
                    T("Resultados"), TB(["Métrica", "Antes", "Después"], [["", "", ""]]),
                    T("Aprendizajes"), L(["Lección 1", "Lección 2"])]},
    {"nombre": "Comparativa A vs B", "slug": "comparativa", "tipo": "comparativa", "icono": "scale-balanced",
     "descripcion": "Compara dos opciones con criterios y da un veredicto.",
     "estructura": [P("Qué se compara y con qué criterios."),
                    TB(["Criterio", "Opción A", "Opción B"], [["", "", ""], ["", "", ""]]),
                    T("Ventajas de A"), L(["..."]), T("Ventajas de B"), L(["..."]),
                    T("Veredicto"), A("Cuándo conviene cada una.", "exito")]},
    {"nombre": "Guía para principiantes", "slug": "principiantes", "tipo": "principiante", "icono": "seedling",
     "descripcion": "Introduce un tema desde cero, sin asumir conocimientos previos.",
     "estructura": [P("Bienvenida y qué aprenderás."),
                    T("¿Qué es?"), P("Definición en palabras simples."),
                    T("Conceptos clave"), L(["Concepto 1", "Concepto 2", "Concepto 3"]),
                    T("Tu primer ejercicio"), P("Un ejemplo guiado."),
                    E("https://example.com", "Para seguir aprendiendo", "Recurso recomendado")]},
    {"nombre": "Tema matemático", "slug": "tema-matematico", "tipo": "matematico", "icono": "square-root-variable",
     "descripcion": "Teoría, fórmula, ejemplo resuelto y práctica en el entrenador.",
     "estructura": [T("Teoría"), P("Explicación del concepto."),
                    T("Fórmula"), F("a^2 + b^2 = c^2"),
                    T("Ejemplo resuelto"), P("Planteamiento y desarrollo paso a paso."),
                    A("Tip: verifica tu resultado sustituyendo en la fórmula.", "info"),
                    E("/entrenador/", "Practica este tema en el entrenador", "Ejercicios adaptativos generados al azar")]},
]
