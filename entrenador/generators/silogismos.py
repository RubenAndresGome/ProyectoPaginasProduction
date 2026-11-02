from .base import BaseGenerator, PreguntaGenerada
import random

class SilogismosGenerator(BaseGenerator):
    """
    Dificultad 1-4: Silogismos categóricos simples (Modus Ponens, Barbara)
    Dificultad 5-7: Identificar premisas válidas/inválidas (Celarent, Darii)
    Dificultad 8-10: Silogismos con negación y lógica de clases compleja
    """
    
    # Pool de plantillas y estructuras de silogismos (p1, p2, conclusión válida, distractores)
    ESTRUCTURAS = [
        {
            # Modo AAA-1 (Barbara)
            'p1': 'Todos los {M} son {P}.',
            'p2': 'Todos los {S} son {M}.',
            'valida': 'Todos los {S} son {P}.',
            'distractores': [
                'Todos los {P} son {S}.',
                'Ningún {S} es {P}.',
                'Algunos {P} no son {S}.'
            ],
            'explicacion': 'Por transitividad silogística (Modo Barbara): si todo S es M y todo M es P, necesariamente todo S es P.'
        },
        {
            # Modo EAE-1 (Celarent)
            'p1': 'Ningún {M} es {P}.',
            'p2': 'Todos los {S} son {M}.',
            'valida': 'Ningún {S} es {P}.',
            'distractores': [
                'Todos los {S} son {P}.',
                'Algunos {S} son {P}.',
                'Ningún {P} es {M}.'
            ],
            'explicacion': 'Modo Celarent: al estar S contenido en M, y M completamente excluido de P, S queda también completamente excluido de P.'
        },
        {
            # Modo AII-1 (Darii)
            'p1': 'Todos los {M} son {P}.',
            'p2': 'Algunos {S} son {M}.',
            'valida': 'Algunos {S} son {P}.',
            'distractores': [
                'Todos los {S} son {P}.',
                'Ningún {S} es {P}.',
                'Algunos {P} no son {S}.'
            ],
            'explicacion': 'Modo Darii: como algunos miembros de S son M, y todo M es P, esos miembros particulares de S son necesariamente P.'
        },
        {
            # Modo EIO-1 (Ferio)
            'p1': 'Ningún {M} es {P}.',
            'p2': 'Algunos {S} son {M}.',
            'valida': 'Algunos {S} no son {P}.',
            'distractores': [
                'Ningún {S} es {P}.',
                'Todos los {S} son {P}.',
                'Algunos {S} son {P}.'
            ],
            'explicacion': 'Modo Ferio: la parte de S que pertenece a M no puede pertenecer a P, ya que ningún M es P. Por lo tanto, algunos S no son P.'
        },
        {
            # Modo AEE-2 (Camestres)
            'p1': 'Todos los {P} son {M}.',
            'p2': 'Ningún {S} es {M}.',
            'valida': 'Ningún {S} es {P}.',
            'distractores': [
                'Todos los {S} son {P}.',
                'Algunos {S} son {P}.',
                'Ningún {M} es {P}.'
            ],
            'explicacion': 'Modo Camestres: como todo P es M y ningún S es M, S y P no pueden compartir elementos. Por lo tanto, ningún S es P.'
        }
    ]

    TEMAS_VOCABULARIO = [
        {
            'S': 'gatos', 'M': 'felinos', 'P': 'mamíferos'
        },
        {
            'S': 'rectángulos', 'M': 'paralelogramos', 'P': 'cuadriláteros'
        },
        {
            'S': 'serpientes', 'M': 'reptiles', 'P': 'animales de sangre fría'
        },
        {
            'S': 'oxígenos', 'M': 'gases', 'P': 'elementos químicos'
        },
        {
            'S': 'humanos', 'M': 'seres racionales', 'P': 'mortales'
        },
        {
            'S': 'planetas', 'M': 'cuerpos celestes', 'P': 'astros orbitantes'
        },
        {
            'S': 'algoritmos', 'M': 'procesos ordenados', 'P': 'herramientas lógicas'
        }
    ]

    def generar(self) -> PreguntaGenerada:
        # Elegir estructura y vocabulario
        est = self._elegir(self.ESTRUCTURAS)
        vocab = self._elegir(self.TEMAS_VOCABULARIO)

        # Reemplazar placeholders
        p1 = est['p1'].format(**vocab)
        p2 = est['p2'].format(**vocab)
        valida = est['valida'].format(**vocab)
        
        distractores_raw = [d.format(**vocab) for d in est['distractores']]

        enunciado = (
            f"Premisa 1: {p1}\n\n"
            f"Premisa 2: {p2}\n\n"
            f"¿Qué conclusión se deduce lógicamente de estas premisas?"
        )
        
        # Silogismos son texto puro, no necesitan LaTeX.
        # Usamos HTML semántico que se renderiza correctamente en dark mode.
        enunciado_latex = (
            f'<div style="text-align:left;">'
            f'<p style="font-size:0.7rem; font-weight:700; text-transform:uppercase; '
            f'letter-spacing:0.1em; color:#22d3ee; margin-bottom:0.75rem;">Premisas</p>'
            f'<p style="font-size:1.05rem; color:inherit; margin-bottom:0.5rem;">'
            f'<span style="color:#94a3b8; font-weight:600;">1.</span> {p1}</p>'
            f'<p style="font-size:1.05rem; color:inherit; margin-bottom:1.25rem;">'
            f'<span style="color:#94a3b8; font-weight:600;">2.</span> {p2}</p>'
            f'<p style="font-size:0.7rem; font-weight:700; text-transform:uppercase; '
            f'letter-spacing:0.1em; color:#22d3ee;">¿Cuál es la conclusión correcta?</p>'
            f'</div>'
        )

        # Generar las opciones (texto plano, sin LaTeX)
        opciones = []
        opciones.append({
            'texto': valida,
            'texto_latex': '',
            'es_correcta': True,
            'orden': 0
        })

        for i, dist in enumerate(distractores_raw[:3]):
            opciones.append({
                'texto': dist,
                'texto_latex': '',
                'es_correcta': False,
                'orden': i + 1
            })

        random.shuffle(opciones)
        for idx, op in enumerate(opciones):
            op['orden'] = idx

        # Explicación en texto plano (sin delimitadores LaTeX)
        explicacion_texto = est['explicacion'].format(**vocab)
        explicacion_latex = (
            f'<p style="color:inherit; line-height:1.7;">{explicacion_texto}</p>'
        )

        return PreguntaGenerada(
            enunciado_latex=enunciado_latex,
            tipo_respuesta='opcion_multiple',
            opciones=opciones,
            dificultad=self.dificultad,
            parametros={'vocabulario': vocab, 'modo': est.get('explicacion', '')[:10]},
            explicacion_latex=explicacion_latex
        )
