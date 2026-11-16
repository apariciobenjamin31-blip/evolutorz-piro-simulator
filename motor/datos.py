"""Datos de referencia del simulador.

Valores de literatura a ~20-25 °C y 1 atm en aire. Verificación (14/11/2026):
- Límites de inflamabilidad (lfl/ufl): confirmados para H₂, CH₄, etanol y n-heptano en tablas de
  seguridad basadas en NFPA 325 (Dow, Engineering ToolBox). Para el heptano otras tablas dan 1,0-6,0 %.
- Energía mínima de ignición: H₂ 0,017 mJ (otras fuentes 0,016-0,019), CH₄ 0,28 mJ y n-heptano 0,24 mJ
  confirmados. El valor del etanol (0,23 mJ) NO se pudo confirmar.
- Atmósfera de exploración 56,5 kPa (8,2 psia) con 34 % de O₂: recomendación de la NASA (NTRS 20150021491).
- Traje EVA 29,6 kPa (4,3 psi) de O₂ puro: NASA (NTRS 20150006014).
Detalle y enlaces en 1-contexto/escenarios-explosion-y-llama.md.
"""

# --------------------------------------------------------------------------
# Combustibles
# --------------------------------------------------------------------------
# especie: nombre de la especie en nasa_gas.yaml (Cantera). None = sólido, sin fase gas.
# lfl / ufl: límites inferior y superior de inflamabilidad en aire, % en volumen.
# mie_mj: energía mínima de ignición en aire, mJ (valor típico de tablas de seguridad).
# antoine: constantes (A, B, C) para presión de vapor en mmHg con T en °C.
COMBUSTIBLES = {
    "hidrogeno": {
        "nombre": "Hidrógeno", "detalle": "Gas · propulsante", "estado": "gas",
        "especie": "H2", "lfl": 4.0, "ufl": 75.0, "mie_mj": 0.017,
        "color": "#8fc5ff",
        "espacio": {
            "tierra": "Llama casi invisible y sin hollín; el gas sube y se dispersa rápido.",
            "parcial": "Se dispersa hacia arriba más despacio; la mezcla inflamable dura más cerca de la fuga.",
            "micro": "No escapa hacia arriba y forma bolsas inflamables. Arde en un rango muy amplio y con muy poca energía de ignición.",
        },
        "ensayos": "SOFBALL (bolas de llama en mezclas muy pobres): STS-83 y STS-94 en 1997 y STS-107 en 2003 (Guía de combustión NASA 2015, p. 25).",
        "consulta": "SOFBALL flame balls microgravity hydrogen",
    },
    "metano": {
        "nombre": "Metano", "detalle": "Gas · propulsante", "estado": "gas",
        "especie": "CH4", "lfl": 5.0, "ufl": 15.0, "mie_mj": 0.28,
        "color": "#77d5ff",
        "espacio": {
            "tierra": "Chorro de llama alto y estrecho que sube rápido.",
            "parcial": "La llama del chorro se alarga y ensancha al bajar la flotabilidad.",
            "micro": "Las llamas de chorro de hidrocarburos tienden a ser más anchas, largas y con más hollín en microgravedad; "
                     "eso se estudió con otros hidrocarburos, no con metano, que la NASA usa para llamas casi sin hollín. "
                     "Una fuga sin ventilación forma una nube que no se dispersa sola.",
        },
        "ensayos": "LSP (hollín en llamas de chorro de otros hidrocarburos): STS-83 y STS-94 en 1997, STS-107 en 2003. "
                   "ACME usa metano e hidrógeno para llamas sin hollín (Guía de combustión NASA 2015, p. 13 y 18).",
        "consulta": "laminar soot processes microgravity gas jet diffusion flame",
    },
    "etanol": {
        "nombre": "Etanol", "detalle": "Líquido · vapor", "estado": "liquido",
        "especie": "C2H5OH", "lfl": 3.3, "ufl": 19.0, "mie_mj": 0.23,
        "antoine": (8.20417, 1642.89, 230.3),
        "color": "#ffcb72",
        "espacio": {
            "tierra": "Llama azulada con poco hollín, difícil de ver con luz intensa.",
            "parcial": "Parecida a la de Tierra, con un derrame más lento.",
            "micro": "Forma gotas con llama esférica tenue; absorbe vapor de agua mientras arde.",
        },
        "ensayos": "FLEX quemó gotas de metanol, otro alcohol, en la ISS; no hay ensayo de etanol en las fuentes (Guía de combustión NASA 2015, p. 12).",
        "consulta": "alcohol droplet combustion microgravity water absorption",
    },
    "heptano": {
        "nombre": "n-Heptano", "detalle": "Líquido · vapor", "estado": "liquido",
        "especie": "C7H16,n-heptane", "lfl": 1.05, "ufl": 6.7, "mie_mj": 0.24,
        "antoine": (6.89385, 1264.37, 216.636),
        "color": "#ffd166",
        "espacio": {
            "tierra": "Charco que arde con llama alta, amarilla y con mucho humo.",
            "parcial": "Se derrama y asienta más despacio; llama más baja y ancha.",
            "micro": "No forma charco: flota en gotas. La gota arde con llama esférica y, tras apagarse la llama visible, puede seguir ardiendo como «llama fría» por tiempo prolongado. En FLEX el límite de inflamabilidad resultó más bajo en gravedad reducida.",
        },
        "ensayos": "FLEX y FLEX-2 en la ISS: gotas de 1 a 5 mm, 0 a 3 atm y hasta 40 % de O₂ (Guía de combustión NASA 2015, p. 12-13 y 34).",
        "consulta": "FLEX droplet combustion cool flame heptane",
    },
    "polimero": {
        "nombre": "Polímero de cabina", "detalle": "ABS / PMMA", "estado": "solido",
        "especie": None, "color": "#ff9a68",
        "espacio": {
            "tierra": "Llama alta y luminosa; el plástico fundido gotea.",
            "parcial": "Llama más ancha y lenta; el goteo cae más despacio.",
            "micro": "Llama tenue que avanza contra el flujo; el acrílico burbujea. Con menos O₂ (17 %) la llama se mantiene azul más tiempo. La prueba de NASA-STD-6001 a 1 g podría no ser conservadora en baja gravedad.",
        },
        "ensayos": "BASS (ISS, desde 2012): esfera de acrílico de 2 cm a 17 % de O₂ y 12 cm/s (Guía de combustión NASA 2015, p. 20). SoFIE (página Glenn de la NASA).",
        "consulta": "BASS burning and suppression of solids microgravity PMMA",
    },
    "celulosa": {
        "nombre": "Celulosa", "detalle": "Algodón / papel", "estado": "solido",
        "especie": None, "color": "#ffd36d",
        "espacio": {
            "tierra": "Arde rápido hacia arriba y puede seguir como brasa.",
            "parcial": "Propagación más lenta, dominada por la ventilación.",
            "micro": "Muy sensible al flujo: en BASS la tela ardió 90 s mientras el flujo bajaba de 10 a menos de 1 cm/s. Cerca del límite puede avanzar un frente sin llama en forma de dedos.",
        },
        "ensayos": "BASS: tela de algodón y fibra de vidrio de 2 cm; frente en dedos según Olson et al. 1998 (Guía de combustión NASA 2015, p. 20 y 33).",
        "consulta": "Saffire cotton fiberglass fabric flame spread microgravity",
    },
    "vela": {
        "nombre": "Vela", "detalle": "Cera de parafina", "estado": "solido",
        "especie": None, "color": "#f6e7b0",
        "espacio": {
            "tierra": "Llama en forma de lágrima, amarilla por el hollín; la flotabilidad mueve el gas a ~1 m/s.",
            "parcial": "Llama más corta y ancha, con menos hollín, por una convección más débil.",
            "micro": "Llama casi esférica, tenue y casi invisible. En la estación Mir ardió en algunas pruebas más de 45 min, hasta agotar la cera, y con menos O₂ que en Tierra; cerca del final oscilaba.",
        },
        "ensayos": "Velas en la estación Mir, Dietrich et al. 2000 (Guía de combustión NASA 2015, p. 30-33).",
        "consulta": "candle flames in non-buoyant atmospheres Mir",
    },
    "cables": {
        "nombre": "Aislamiento de cables", "detalle": "ETFE / PTFE", "estado": "solido",
        "especie": None, "color": "#ffad77",
        "espacio": {
            "tierra": "Humea antes de encenderse; la llama sube por el cable si está vertical.",
            "parcial": "Importa más la dirección del cable respecto al flujo.",
            "micro": "La llama envuelve el cable como un manguito y avanza a lo largo.",
        },
        "ensayos": "Lecciones de Apollo 1 (arcos en cables con O₂ puro) y Apollo 13 (calentador a ~1000 °F que degradó el aislamiento de teflón; luego se blindó el cableado con acero inoxidable). Fuente: sma.nasa.gov.",
        "consulta": "wire insulation flame spread microgravity",
    },
}

# Para la llama animada (componentes/llama.html): forma de la fuente y paleta.
APARIENCIA = {
    "hidrogeno": {"shape": "nozzle", "palette": "hydrogen", "soot": -1, "microSoot": 0},
    "metano": {"shape": "nozzle", "palette": "normal", "soot": -0.1, "microSoot": 0.45},
    "etanol": {"shape": "pool", "palette": "normal", "soot": -0.35, "microSoot": 0},
    "heptano": {"shape": "pool", "palette": "normal", "soot": 0.15, "microSoot": 0.1},
    "polimero": {"shape": "slab", "palette": "normal", "soot": 0.05, "microSoot": 0},
    "celulosa": {"shape": "sheet", "palette": "normal", "soot": -0.05, "microSoot": 0},
    "vela": {"shape": "wick", "palette": "normal", "soot": 0, "microSoot": 0},
    "cables": {"shape": "wire", "palette": "normal", "soot": 0, "microSoot": 0},
}

GASES_COMBUSTIBLES = [k for k, v in COMBUSTIBLES.items() if v["especie"]]

# --------------------------------------------------------------------------
# Ambientes (gravedad)
# --------------------------------------------------------------------------
AMBIENTES = {
    "orbita": {"nombre": "Órbita", "gravedad": 0.0},
    "luna": {"nombre": "Luna", "gravedad": 1.62},
    "marte": {"nombre": "Marte", "gravedad": 3.71},
    "tierra": {"nombre": "Tierra", "gravedad": 9.81},
}

# --------------------------------------------------------------------------
# Atmósferas: composición en % molar y presión total típica en kPa.
# Las de otros planetas son composiciones aproximadas; dentro de un hábitat
# importa la atmósfera de cabina, no la exterior.
# --------------------------------------------------------------------------
ATMOSFERAS = {
    "cabina": {"nombre": "Cabina estándar (aire)", "presion": 101.3,
               "gases": {"N2": 78.08, "O2": 20.95, "Ar": 0.93, "CO2": 0.04}},
    "exploracion": {"nombre": "Atmósfera de exploración", "presion": 56.5,
                    "gases": {"N2": 66.0, "O2": 34.0}},
    "eva": {"nombre": "Traje EVA (O₂ puro)", "presion": 29.6,
            "gases": {"O2": 100.0}},
    "marte": {"nombre": "Atmósfera de Marte (exterior)", "presion": 0.6,
              "gases": {"CO2": 95.1, "N2": 2.7, "Ar": 1.6, "O2": 0.13, "CO": 0.47}},
    "venus": {"nombre": "Atmósfera de Venus (exterior)", "presion": 9200.0,
              "gases": {"CO2": 96.5, "N2": 3.5}},
    "titan": {"nombre": "Atmósfera de Titán (exterior)", "presion": 146.7,
              "gases": {"N2": 98.4, "CH4": 1.5, "H2": 0.1}},
    "nitrogeno": {"nombre": "Nitrógeno inerte", "presion": 101.3, "gases": {"N2": 100.0}},
    "argon": {"nombre": "Argón inerte", "presion": 101.3, "gases": {"Ar": 100.0}},
    "helio": {"nombre": "Helio inerte", "presion": 101.3, "gases": {"He": 100.0}},
}

# Nombre legible de cada especie de la atmósfera.
NOMBRE_GAS = {"N2": "N₂", "O2": "O₂", "Ar": "Ar", "CO2": "CO₂", "He": "He",
              "CH4": "CH₄", "H2": "H₂", "CO": "CO", "H2O": "H₂O"}

# Atmósferas de referencia para comparar la pO₂ (kPa).
PO2_REFERENCIAS = [("Exploración", 19.2), ("Cabina estándar", 21.3), ("Traje EVA", 29.6)]

NTRS = "https://ntrs.nasa.gov/search?q="
NASA_STD_6001 = "https://standards.nasa.gov/standard/NASA/NASA-STD-6001"

# O₂ límite publicado (% en volumen, diluyente N₂, NFPA 69). Referencia para contrastar
# con la estimación del modelo, que subestima el valor del hidrógeno.
# Confirmados H₂ 5, CH₄ 12 y n-heptano 11,5 (tabla Dow basada en NFPA 69). El del etanol (10,5)
# NO se pudo confirmar: la misma tabla da 10 para el metanol. Revisar la edición vigente de NFPA 69.
O2_LIMITE_REFERENCIA = {"hidrogeno": 5.0, "metano": 12.0, "etanol": 10.5, "heptano": 11.5}

# Fuentes verificadas el 14/11/2026 (ver 1-contexto/escenarios-explosion-y-llama.md).
GUIA_NASA = "https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/"
GLENN_COMBUSTION = "https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/"
APOLLO_1 = "https://sma.nasa.gov/sma-disciplines/accllp/apollo-1"
APOLLO_13 = "https://sma.nasa.gov/sma-disciplines/accllp/apollo-13"
