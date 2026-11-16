"""Evolutorz · Simulador de fuego y explosiones en hábitats espaciales.

Ejecutar:  .venv\\Scripts\\streamlit run app.py
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from motor import asistente, combustion as comb, fuga, sugerencias
from motor.datos import (AMBIENTES, APARIENCIA, ATMOSFERAS, COMBUSTIBLES, GASES_COMBUSTIBLES,
                         NASA_STD_6001, NOMBRE_GAS, NTRS, O2_LIMITE_REFERENCIA, PO2_REFERENCIAS)

RAIZ = pathlib.Path(__file__).parent
st.set_page_config(page_title="Piro-Simulator · Evolutorz", page_icon="🔥", layout="wide")

st.markdown("""
<style>
[data-testid="stMainBlockContainer"] { padding-top: 1.2rem; padding-right: 11.5rem; max-width: 1500px; }
[data-testid="stSidebarHeader"] { padding: .4rem .8rem 0; height: auto; min-height: 2rem; }
[data-testid="stSidebarUserContent"] { padding-top: 0; }
[data-testid="stSidebarUserContent"] h2 { margin-top: 0; padding-top: 0; }
.st-key-grupo_combustible details { border-left: 4px solid #ff9a68 !important; }
.st-key-grupo_combustible summary p { color: #ff9a68; font-weight: 600; }
.st-key-grupo_combustible details[open] { background: color-mix(in srgb, #ff9a68 9%, transparent); border-color: #ff9a68 !important; }
.st-key-grupo_combustible details[open] summary { background: color-mix(in srgb, #ff9a68 22%, transparent); }
.st-key-grupo_gravedad details { border-left: 4px solid #70d8c4 !important; }
.st-key-grupo_gravedad summary p { color: #70d8c4; font-weight: 600; }
.st-key-grupo_gravedad details[open] { background: color-mix(in srgb, #70d8c4 9%, transparent); border-color: #70d8c4 !important; }
.st-key-grupo_gravedad details[open] summary { background: color-mix(in srgb, #70d8c4 22%, transparent); }
.st-key-grupo_atmosfera details { border-left: 4px solid #8fc5ff !important; }
.st-key-grupo_atmosfera summary p { color: #8fc5ff; font-weight: 600; }
.st-key-grupo_atmosfera details[open] { background: color-mix(in srgb, #8fc5ff 9%, transparent); border-color: #8fc5ff !important; }
.st-key-grupo_atmosfera details[open] summary { background: color-mix(in srgb, #8fc5ff 22%, transparent); }
.st-key-grupo_fuga details { border-left: 4px solid #f0c66e !important; }
.st-key-grupo_fuga summary p { color: #f0c66e; font-weight: 600; }
.st-key-grupo_fuga details[open] { background: color-mix(in srgb, #f0c66e 9%, transparent); border-color: #f0c66e !important; }
.st-key-grupo_fuga details[open] summary { background: color-mix(in srgb, #f0c66e 22%, transparent); }
.st-key-grupo_ignicion details { border-left: 4px solid #b9a4ff !important; }
.st-key-grupo_ignicion summary p { color: #b9a4ff; font-weight: 600; }
.st-key-grupo_ignicion details[open] { background: color-mix(in srgb, #b9a4ff 9%, transparent); border-color: #b9a4ff !important; }
.st-key-grupo_ignicion details[open] summary { background: color-mix(in srgb, #b9a4ff 22%, transparent); }

.ancla { position: relative; top: -70px; height: 0; }
.marca-evolutorz { position: fixed; top: 12px; right: 150px; z-index: 999991; pointer-events: none;
  font: 700 1.35rem system-ui, sans-serif; letter-spacing: .14em; color: #e8eef1; opacity: .18; }
@media (max-width: 900px) {
  [data-testid="stMainBlockContainer"] { padding-right: 9rem; padding-bottom: 2rem; }
}
.veredicto { padding: 14px 18px; border-radius: 12px; border: 1px solid; margin-bottom: 6px; }
.veredicto b { font-size: 1.25rem; display: block; margin-bottom: 2px; }
.veredicto span { color: #bccad1; }
.v-verde { background: rgba(80,200,140,.08); border-color: rgba(80,200,140,.45); }
.v-verde b { color: #6fdca6; }
.v-amarillo { background: rgba(240,198,110,.08); border-color: rgba(240,198,110,.45); }
.v-amarillo b { color: #f0c66e; }
.v-naranja { background: rgba(255,146,92,.08); border-color: rgba(255,146,92,.5); }
.v-naranja b { color: #ff9a68; }
.v-rojo { background: rgba(255,90,80,.1); border-color: rgba(255,100,90,.6); }
.v-rojo b { color: #ff7a6e; }
.regimen-actual { border: 1px solid #70d8c4; border-radius: 10px; padding: 10px 12px; background: rgba(112,216,196,.07); }
.regimen { border: 1px solid #1d2f3d; border-radius: 10px; padding: 10px 12px; }
.regimen h4, .regimen-actual h4 { margin: 0 0 4px; font-size: .8rem; letter-spacing: .06em; text-transform: uppercase; color: #93a5ae; }
.regimen-actual h4 { color: #70d8c4; }

/* Animación de burbuja: se infla con rebote al pasar el cursor, suelta una onda y hace «pop» al hacer clic. */
.stButton button, [data-testid="stExpander"] summary, [data-testid="stPills"] button {
  position: relative; overflow: hidden; transition: box-shadow .25s ease; }
.stButton button::after, [data-testid="stExpander"] summary::after, [data-testid="stPills"] button::after {
  content: ""; position: absolute; left: 50%; top: 50%; width: 12px; height: 12px; border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,.45), rgba(255,255,255,0) 70%);
  transform: translate(-50%, -50%) scale(0); opacity: 0; pointer-events: none; }
.stButton button:hover, [data-testid="stPills"] button:hover {
  animation: burbuja .5s cubic-bezier(.3, 1.6, .5, 1) forwards; box-shadow: 0 0 14px rgba(255,146,92,.35); }
[data-testid="stExpander"] summary:hover { animation: burbuja-suave .5s cubic-bezier(.3, 1.6, .5, 1) forwards; }
.stButton button:hover::after, [data-testid="stExpander"] summary:hover::after,
[data-testid="stPills"] button:hover::after { animation: onda .65s ease-out; }
.stButton button:active, [data-testid="stExpander"] summary:active,
[data-testid="stPills"] button:active { animation: pop .28s ease-out; }
@keyframes burbuja { 0% { transform: scale(1); } 45% { transform: scale(1.09); } 75% { transform: scale(.98); } 100% { transform: scale(1.04); } }
@keyframes burbuja-suave { 0% { transform: scale(1); } 45% { transform: scale(1.03); } 75% { transform: scale(.995); } 100% { transform: scale(1.015); } }
@keyframes onda { 0% { transform: translate(-50%, -50%) scale(0); opacity: .7; } 100% { transform: translate(-50%, -50%) scale(22); opacity: 0; } }
@keyframes pop { 0% { transform: scale(.9); } 60% { transform: scale(1.07); } 100% { transform: scale(1); } }
@media (prefers-reduced-motion: reduce) {
  .stButton button, [data-testid="stExpander"] summary, [data-testid="stPills"] button { animation: none !important; }
  .stButton button::after, [data-testid="stExpander"] summary::after, [data-testid="stPills"] button::after { display: none; }
}
/* Entrada al cargar o recargar: cada bloque aparece uno tras otro. */
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > * {
  animation: entrada .65s cubic-bezier(.2, .9, .3, 1.15) both; }
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > * {
  animation: entrada-lateral .55s cubic-bezier(.2, .9, .3, 1.15) both; }
@keyframes entrada { from { opacity: 0; transform: translateY(22px) scale(.97); filter: blur(4px); }
  to { opacity: 1; transform: none; filter: none; } }
@keyframes entrada-lateral { from { opacity: 0; transform: translateX(-26px); } to { opacity: 1; transform: none; } }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(1) { animation-delay: 70ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(2) { animation-delay: 140ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(3) { animation-delay: 210ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(4) { animation-delay: 280ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(5) { animation-delay: 350ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(6) { animation-delay: 420ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(7) { animation-delay: 490ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(8) { animation-delay: 560ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(9) { animation-delay: 630ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(10) { animation-delay: 700ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(11) { animation-delay: 770ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(12) { animation-delay: 840ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(13) { animation-delay: 910ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(14) { animation-delay: 980ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(15) { animation-delay: 1050ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(16) { animation-delay: 1120ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(17) { animation-delay: 1190ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(18) { animation-delay: 1260ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(19) { animation-delay: 1330ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(20) { animation-delay: 1400ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(21) { animation-delay: 1470ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(22) { animation-delay: 1540ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(23) { animation-delay: 1610ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(24) { animation-delay: 1680ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(25) { animation-delay: 1680ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(26) { animation-delay: 1680ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(27) { animation-delay: 1680ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(28) { animation-delay: 1680ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(29) { animation-delay: 1680ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(30) { animation-delay: 1680ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(31) { animation-delay: 1680ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(32) { animation-delay: 1680ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(33) { animation-delay: 1680ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(34) { animation-delay: 1680ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(35) { animation-delay: 1680ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(36) { animation-delay: 1680ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(37) { animation-delay: 1680ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(38) { animation-delay: 1680ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(39) { animation-delay: 1680ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(40) { animation-delay: 1680ms; }
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > :nth-child(1) { animation-delay: 230ms; }
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > :nth-child(2) { animation-delay: 310ms; }
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > :nth-child(3) { animation-delay: 390ms; }
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > :nth-child(4) { animation-delay: 470ms; }
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > :nth-child(5) { animation-delay: 550ms; }
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > :nth-child(6) { animation-delay: 630ms; }
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > :nth-child(7) { animation-delay: 710ms; }
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > :nth-child(8) { animation-delay: 790ms; }
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > :nth-child(9) { animation-delay: 870ms; }
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > :nth-child(10) { animation-delay: 950ms; }
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > :nth-child(11) { animation-delay: 1030ms; }
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > :nth-child(12) { animation-delay: 1110ms; }
/* Pasada la carga inicial, los cambios de parámetros no repiten la entrada. */
html.ya-cargado [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > *,
html.ya-cargado [data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > * { animation: none !important; }
@media (prefers-reduced-motion: reduce) {
  [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > *,
  [data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > * { animation: none !important; }
}
</style>
""", unsafe_allow_html=True)

def cargar_arco():
    """Inserta la barra de atajos en semicírculo en la página principal (una sola vez).

    Streamlit no ejecuta <script> dentro de st.html, así que un iframe mínimo copia el
    estilo y el script de componentes/arco.html al documento principal.
    """
    fuente = (RAIZ / "componentes" / "arco.html").read_text(encoding="utf-8")
    css = fuente.split("<style>", 1)[1].split("</style>", 1)[0]
    js = fuente.split("<script>", 1)[1].split("</script>", 1)[0]
    cargador = ("<script>const D = window.parent.document;"
                "if (!D.getElementById('arco-estilos')) {"
                "const s = D.createElement('style'); s.id = 'arco-estilos'; s.textContent = " + json.dumps(css) + ";"
                "D.head.appendChild(s);"
                "const j = D.createElement('script'); j.textContent = " + json.dumps(js) + ";"
                "D.body.appendChild(j); }</script>")
    st.iframe(cargador, height=1, alt="Cargador del menú de atajos")


cargar_arco()


def ancla(id_):
    st.markdown(f'<div class="ancla" id="{id_}"></div>', unsafe_allow_html=True)


def nombre(clave):
    return COMBUSTIBLES[clave]["nombre"]


def fmt(valor, dec=1):
    return f"{valor:,.{dec}f}".replace(",", " ").replace(".", ",")


# --------------------------------------------------------------------------
# Cálculos con caché (Streamlit vuelve a ejecutar el script en cada cambio)
# --------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def calc_ventana(atm, fr, T, P):
    return comb.ventana(dict(atm), dict(fr), T, P)


@st.cache_data(show_spinner=False)
def calc_aicc(atm, fr, x, T, P):
    fr = dict(fr)
    return comb.explosion_confinada(fr, comb.composicion(dict(atm), fr, x), T, P)


@st.cache_data(show_spinner=False)
def calc_loc(atm, fr, T, P):
    return comb.oxigeno_limite(dict(atm), dict(fr), T, P)


@st.cache_data(show_spinner=False)
def calc_velocidad(atm, fr, x, T, P):
    return comb.velocidad_llama(dict(atm), dict(fr), x, T, P)


# --------------------------------------------------------------------------
# Parámetros (barra lateral)
# --------------------------------------------------------------------------
# Valores iniciales de cada control. Los escenarios los reemplazan con un clic.
INICIALES = {
    "mezcla": False, "comb": "hidrogeno", "amb": "orbita", "grav": 1.0, "viento": 0.2,
    "atm": "cabina", "temp": 22.0, "origen": "Fuga en el tiempo", "vol": 75.0, "caudal": 20.0,
    "renov": 2.0, "dur": 180, "inst": 180, "x_fijo": 8.0, "energia": 1.0, "resist": 0.0,
}

ESCENARIOS = {
    "explosion": {
        "boton": "💥 Explosión",
        "titulo": "Escenario: fuga de hidrógeno que termina en mezcla explosiva",
        "texto": "Módulo de 75 m³ en órbita con aire de cabina (101,3 kPa, 21 % de O₂). Fuga de 100 L/min de H₂ "
                 "y ventilación degradada a 0,5 renovaciones por hora durante 120 min, con una chispa de 1 mJ. "
                 "Volumen, caudal y ventilación son valores supuestos para ilustrar el caso.",
        "valores": {"mezcla": False, "comb": "hidrogeno", "amb": "orbita", "viento": 0.2, "atm": "cabina",
                    "o2_cabina": 20.95, "p_cabina": 101.3, "temp": 22.0, "origen": "Fuga en el tiempo",
                    "vol": 75.0, "caudal": 100.0, "renov": 0.5, "dur": 120, "inst": 120,
                    "energia": 1.0, "resist": 0.0},
    },
    "llama": {
        "boton": "🕯️ Llama",
        "titulo": "Escenario: vela en microgravedad con llama estable",
        "texto": "Vela en órbita con aire de cabina (101,3 kPa, 21 % de O₂) y aire quieto, como en los ensayos de "
                 "la estación Mir: la llama es casi esférica, tenue y en algunas pruebas duró más de 45 min "
                 "(Guía de combustión NASA 2015, p. 30-33).",
        "valores": {"mezcla": False, "comb": "vela", "amb": "orbita", "viento": 0.0, "atm": "cabina",
                    "o2_cabina": 20.95, "p_cabina": 101.3, "temp": 22.0},
    },
}

for clave, valor in INICIALES.items():
    st.session_state.setdefault(clave, valor)



GRUPOS = [('combustible', '#ff9a68'), ('gravedad', '#70d8c4'), ('atmosfera', '#8fc5ff'), ('fuga', '#f0c66e'), ('ignicion', '#b9a4ff')]
for clave_grupo, _ in GRUPOS:
    st.session_state.setdefault(f"grupo_{clave_grupo}", clave_grupo == "combustible")


def abrir_solo(grupo):
    """Al abrir un grupo de parámetros, cierra los demás."""
    if st.session_state.get(f"grupo_{grupo}"):
        for otro, _ in GRUPOS:
            if otro != grupo:
                st.session_state[f"grupo_{otro}"] = False


def restablecer():
    st.session_state.clear()


def cargar_escenario(nombre_escenario):
    st.session_state.update(ESCENARIOS[nombre_escenario]["valores"])
    st.session_state.escenario = nombre_escenario
    st.session_state.auto_explosion = nombre_escenario == "explosion"


with st.sidebar:
    st.markdown(f"## ⚙️ {'Parámetros'}")
    st.caption("Escenarios de ejemplo")
    b1, b2 = st.columns(2)
    for col, (clave, esc) in zip((b1, b2), ESCENARIOS.items()):
        col.button(esc["boton"], on_click=cargar_escenario, args=(clave,), width="stretch")

    with st.expander("🔥 Combustible", key="grupo_combustible", on_change=abrir_solo, args=("combustible",)):
        mezcla = st.toggle("Mezcla de gases", key="mezcla", help="Combina hidrógeno, metano y vapores en proporciones.")
        if mezcla:
            elegidos = st.multiselect("Componentes", GASES_COMBUSTIBLES, default=["hidrogeno", "metano"],
                                      format_func=nombre) or ["metano"]
            partes = {c: st.slider(f"{nombre(c)} (partes)", 0, 100, 50, key=f"mezcla_{c}") for c in elegidos}
            fracciones = {c: p / 100 for c, p in partes.items() if p > 0} or {"metano": 1.0}
            combustible = max(fracciones, key=fracciones.get)
        else:
            combustible = st.selectbox("Material o gas", list(COMBUSTIBLES), format_func=nombre, key="comb")
            fracciones = {combustible: 1.0} if COMBUSTIBLES[combustible]["especie"] else {}
        st.caption(COMBUSTIBLES[combustible]["detalle"])

    with st.expander("🪐 Gravedad y aire", key="grupo_gravedad", on_change=abrir_solo, args=("gravedad",)):
        ambiente = st.radio("Ambiente", [*AMBIENTES, "otro"], horizontal=True, key="amb",
                            format_func=lambda a: AMBIENTES[a]["nombre"] if a in AMBIENTES else "Otro")
        gravedad = (AMBIENTES[ambiente]["gravedad"] if ambiente in AMBIENTES
                    else st.slider("Gravedad (m/s²)", 0.0, 30.0, step=0.1, key="grav"))
        viento = st.slider("Velocidad del aire (m/s)", 0.0, 2.0, step=0.05, key="viento",
                           help="Orienta la llama y arrastra el humo.")

    with st.expander("🫧 Atmósfera", key="grupo_atmosfera", on_change=abrir_solo, args=("atmosfera",)):
        atm_id = st.selectbox("Atmósfera", [*ATMOSFERAS, "propia"], key="atm",
                              format_func=lambda a: ATMOSFERAS[a]["nombre"] if a in ATMOSFERAS else "Composición propia")
        if atm_id == "propia":
            tabla = st.data_editor(
                {"Gas": ["N2", "O2", "Ar", "CO2", "He"], "%": [78.0, 21.0, 1.0, 0.0, 0.0]},
                column_config={"Gas": st.column_config.SelectboxColumn(options=list(NOMBRE_GAS), required=True)},
                num_rows="dynamic", hide_index=True, key="tabla_gases")
            atmosfera = {}
            for gas, pct in zip(tabla["Gas"], tabla["%"]):
                if gas and pct and pct > 0:
                    atmosfera[gas] = atmosfera.get(gas, 0) + float(pct)
            atmosfera = atmosfera or {"N2": 100.0}
            st.session_state.setdefault("p_propia", 101.3)
            presion = st.number_input("Presión total (kPa)", 0.1, 10000.0, key="p_propia")
        else:
            base = ATMOSFERAS[atm_id]
            st.session_state.setdefault(f"o2_{atm_id}", float(base["gases"].get("O2", 0.0)))
            st.session_state.setdefault(f"p_{atm_id}", float(base["presion"]))
            o2 = st.slider("O₂ (%)", 0.0, 100.0, step=0.5, key=f"o2_{atm_id}")
            otros = {g: v for g, v in base["gases"].items() if g != "O2"}
            total_otros = sum(otros.values())
            atmosfera = {g: (100 - o2) * v / total_otros for g, v in otros.items()} if total_otros else {}
            if o2 > 0:
                atmosfera["O2"] = o2
            presion = st.number_input("Presión total (kPa)", 0.1, 10000.0, key=f"p_{atm_id}")
        temperatura = st.number_input("Temperatura (°C)", -100.0, 400.0, step=1.0, key="temp")

    with st.expander("⏱ Fuga y módulo", key="grupo_fuga", on_change=abrir_solo, args=("fuga",)):
        origen = st.radio("Concentración del gas", ["Fuga en el tiempo", "Valor fijo"], horizontal=True, key="origen")
        volumen = st.number_input("Volumen del módulo (m³)", 1.0, 5000.0, key="vol", help="Ejemplo: 75 m³.")
        caudal = st.number_input("Caudal de la fuga (L/min)", 0.0, 10000.0, key="caudal")
        renovaciones = st.number_input("Renovaciones de aire por hora", 0.0, 60.0, step=0.5, key="renov",
                                       help="Cuántas veces por hora la ventilación reemplaza el aire del módulo.")
        duracion = st.slider("Tiempo simulado (min)", 5, 720, step=5, key="dur")
        if origen == "Valor fijo":
            x_fijo = st.slider("Combustible en la mezcla (%)", 0.0, 100.0, step=0.1, key="x_fijo")
        else:
            st.session_state.inst = min(st.session_state.inst, duracion)
            instante = st.slider("Evaluar en el minuto", 0, duracion, key="inst")

    with st.expander("⚡ Ignición y estructura", key="grupo_ignicion", on_change=abrir_solo, args=("ignicion",)):
        energia = st.number_input("Energía de la chispa (mJ)", 0.0, 10000.0, step=0.1, key="energia",
                                  help="Una descarga electrostática humana ronda 1 a 30 mJ.")
        resistencia = st.number_input("Sobrepresión que resiste el módulo (kPa)", 0.0, 5000.0, key="resist",
                                      help="0 = sin dato. Se compara con la presión de explosión.")

    st.button("↺ Restablecer", on_click=restablecer, width="stretch")

# --------------------------------------------------------------------------
# Estado del escenario
# --------------------------------------------------------------------------
T = temperatura + 273.15
es_gas = bool(fracciones)
atm_t = tuple(sorted(atmosfera.items()))
fr_t = tuple(sorted(fracciones.items()))
o2_atm = atmosfera.get("O2", 0.0) / (sum(atmosfera.values()) or 1)

x_max = 1.0
if es_gas and all(COMBUSTIBLES[c]["estado"] == "liquido" for c in fracciones):
    psat = sum(comb.presion_vapor_kpa(c, T) * f for c, f in fracciones.items()) / sum(fracciones.values())
    x_max = min(1.0, psat / presion)

if origen == "Valor fijo":
    x = min(x_fijo / 100, x_max)
    t_eval = None
else:
    t_eval = instante
    x = float(fuga.concentracion(instante, volumen, caudal, renovaciones, x_max))

r = {"estado": "sin_gas", "x": x, "tiempo_lfl": None}
ventana = None
if es_gas:
    ventana = calc_ventana(atm_t, fr_t, T, presion)
    lfl, ufl = ventana["lfl"], ventana["ufl"]
    if lfl is None:
        r["estado"] = "no_inflamable_atm"
    else:
        r["lfl"], r["ufl"] = lfl, ufl
        r["pct_lfl"] = x * 100 / lfl * 100
        r["estado"] = "pobre" if x * 100 < lfl else ("rica" if ufl is not None and x * 100 > ufl else "explosiva")
        if origen == "Fuga en el tiempo":
            r["tiempo_lfl"] = fuga.tiempo_hasta(lfl / 100, volumen, caudal, renovaciones, x_max)
        x_eval = x if r["estado"] == "explosiva" else ventana["x_pico"] / 100
        r["pmax"], r["tmax"] = calc_aicc(atm_t, fr_t, x_eval, T, presion)
        r["pmax_es_actual"] = r["estado"] == "explosiva"
        r["mie"] = min(COMBUSTIBLES[c]["mie_mj"] for c in fracciones)

po2 = presion * o2_atm * (1 - x if es_gas else 1)

# --------------------------------------------------------------------------
# Encabezado y resumen
# --------------------------------------------------------------------------
st.markdown('<div class="marca-evolutorz">Piro-Simulator · Evolutorz</div>', unsafe_allow_html=True)
# --------------------------------------------------------------------------
# Llama y ventana de inflamabilidad
# --------------------------------------------------------------------------
ancla("llama")
st.subheader("🔥 Llama y ventana de inflamabilidad")
# Contenedor que el botón «Ampliar» lleva casi a pantalla completa (componentes/arco.html).
bloque_simulacion = st.container(key="bloque_simulacion")
col_llama, col_ventana = bloque_simulacion.columns([1, 1.25], gap="medium")
with col_llama:
    intensidad = 0.0 if o2_atm <= 0 else min(2.5, po2 / 21.2)
    if gravedad < 0.1:
        intensidad *= 0.55 + 0.45 * min(1.0, viento / 0.1)
    if intensidad > 0:
        intensidad = max(0.6, intensidad)
    vacio = None
    if o2_atm <= 0:
        vacio = ["Sin O₂", "No se dibuja una llama convencional"]
    elif r["estado"] == "no_inflamable_atm":
        vacio = ["No arde", "Esta atmósfera no sostiene la llama"]
    explosion = None
    if "pmax" in r:
        rgb = [int(COMBUSTIBLES[combustible]["color"][i:i + 2], 16) for i in (1, 3, 5)]
        explosion = {"pmax": r["pmax"], "p0": presion, "color": rgb, "gravity": gravedad,
                     "label": "💥 Ver explosión" if r["pmax_es_actual"] else "💥 Ver peor caso",
                     "auto": st.session_state.pop("auto_explosion", False)}
    # Punto de la gráfica (fracción del barrido) donde está tu mezcla: ahí late la llama.
    marca = None
    if ventana is not None and 0 < x < 1:
        fraccion = (np.log10(max(x * 100, 0.2)) - np.log10(0.2)) / (2 - np.log10(0.2))
        marca = 0.8 * min(1.0, max(0.0, float(fraccion)))
    parametros = {
        "sync": {"periodo": 6000, "marca": marca},
        "gravity": gravedad, "airflow": viento, "intensity": intensidad,
        "look": APARIENCIA[combustible], "empty": vacio, "explosion": explosion,
        "hud": [nombre(combustible) if not mezcla else "Mezcla", AMBIENTES.get(ambiente, {"nombre": "Otro"})["nombre"],
                f"g {fmt(gravedad, 2)} m/s²", f"pO₂ {fmt(po2)} kPa"],
    }
    plantilla = (RAIZ / "componentes" / "llama.html").read_text(encoding="utf-8")
    st.iframe(plantilla.replace("__PARAMS__", json.dumps(parametros)), height=300,
              alt="Esquema animado de la llama")
    st.caption("Esquema cualitativo: forma y color según gravedad, aire y pO₂.")

with col_ventana:
    if ventana is None:
        st.info("La ventana de inflamabilidad se calcula para gases y vapores. Elige hidrógeno, metano, etanol o n-heptano.")
    else:
        fig = go.Figure()
        if ventana["lfl"] is not None:
            fig.add_vrect(x0=ventana["lfl"], x1=ventana["ufl"] or ventana["x"][-1], fillcolor="#ff5a50",
                          opacity=0.13, line_width=0, annotation_text="zona explosiva", annotation_position="bottom left")
        fig.add_trace(go.Scatter(x=ventana["x"], y=ventana["t_ad"], mode="lines", name="Temperatura de llama",
                                 line=dict(color="#ff9a68", width=3)))
        fig.add_hline(y=ventana["t_umbral_inf"], line_dash="dot", line_color="#93a5ae",
                      annotation_text="umbral para arder", annotation_position="bottom right")
        if 0 < x < 1:
            fig.add_vline(x=x * 100, line_color="#70d8c4", line_width=2,
                          annotation_text="tu mezcla", annotation_position="top right")
        fig.update_layout(template="plotly_dark", height=300, margin=dict(l=10, r=10, t=30, b=10),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
                          xaxis=dict(title="Combustible en la mezcla (%)", type="log", range=[np.log10(0.2), 2]),
                          yaxis=dict(title="Temperatura adiabática (K)"))
        st.plotly_chart(fig, width="stretch")
        if ventana["lfl"] is not None:
            st.caption(f"Límites estimados: {fmt(ventana['lfl'], 2)} % a "
                       f"{fmt(ventana['ufl'], 1) + ' %' if ventana['ufl'] else 'sin límite superior'} "
                       f"(método CAFT calibrado con datos en aire).")

# --------------------------------------------------------------------------
# Resumen
# --------------------------------------------------------------------------
if st.session_state.get("escenario") in ESCENARIOS and st.session_state.get("comb") == ESCENARIOS[st.session_state.escenario]["valores"]["comb"]:
    esc = ESCENARIOS[st.session_state.escenario]
    st.info(f"**{esc['titulo']}.** {esc['texto']} Puedes cambiar cualquier parámetro.", icon="📌")

ancla("resumen")
if r["estado"] == "sin_gas" and st.session_state.get("escenario") == "llama" and combustible == "vela":
    clase, titulo, texto = ("v-verde", "🕯️ Llama estable",
                            "Llama de vela casi esférica y tenue, sostenida por difusión de oxígeno. "
                            "Aunque se vea débil, puede encender materiales cercanos.")
elif r["estado"] == "sin_gas":
    clase, titulo, texto = "v-naranja", "🔥 Riesgo de incendio", "Material sólido: no forma una nube explosiva, pero puede arder y producir humo tóxico."
elif r["estado"] == "no_inflamable_atm":
    clase, titulo, texto = "v-verde", "🟢 Esta atmósfera no deja arder la mezcla", "Falta oxígeno o sobra gas inerte para que la llama se propague a cualquier concentración."
elif r["estado"] == "explosiva":
    enciende = energia >= r["mie"]
    clase, titulo = "v-rojo", "💥 Mezcla explosiva"
    texto = ("La chispa configurada basta para encenderla." if enciende
             else "La chispa configurada no alcanza la energía mínima típica, pero otra fuente podría encenderla.")
elif r["estado"] == "rica":
    clase, titulo, texto = "v-naranja", "⚠️ Demasiado rica", "No arde así, pero al mezclarse con aire pasará por la zona explosiva."
elif r["pct_lfl"] >= 25:
    clase, titulo, texto = "v-naranja", "⚠️ Cerca del límite", "Supera el 25 % del límite inferior: nivel de alarma alta en detectores industriales."
elif r["pct_lfl"] >= 10:
    clase, titulo, texto = "v-amarillo", "🟡 Alarma temprana", "Supera el 10 % del límite inferior: nivel de primera alarma habitual."
else:
    clase, titulo, texto = "v-verde", "🟢 Por debajo de la alarma", "La concentración está lejos del límite inferior de inflamabilidad."
st.markdown(f'<div class="veredicto {clase}"><b>{titulo}</b><span>{texto}</span></div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Gas en el aire", f"{fmt(x * 100, 2)} %" if es_gas else "—",
          help="Fracción molar del gas o vapor en el módulo.")
c2.metric("% del límite inferior", f"{fmt(r['pct_lfl'], 0)} %" if "pct_lfl" in r else "—",
          help="100 % = límite inferior de inflamabilidad (LFL).")
if "pmax" in r:
    c3.metric("Explosión" if r["pmax_es_actual"] else "Peor explosión",
              f"{fmt(r['pmax'], 0)} kPa", f"+{fmt(r['pmax'] - presion, 0)} kPa", delta_color="inverse",
              help="Combustión a volumen constante (AICC), sin pérdidas de calor: es un límite superior.")
else:
    c3.metric("Explosión", "—")
if origen == "Fuga en el tiempo" and es_gas and "lfl" in r:
    c4.metric("Hasta zona explosiva",
              f"{fmt(r['tiempo_lfl'], 0)} min" if r["tiempo_lfl"] is not None else "No llega")
else:
    c4.metric("pO₂", f"{fmt(po2)} kPa", help="Presión parcial de oxígeno.")

def dato_combustible(clave):
    """Un dato concreto del combustible, con los valores calculados para este escenario."""
    if mezcla:
        return (f"La mezcla arde entre {fmt(r['lfl'], 1)} % y {fmt(r['ufl'] or 100, 1)} % en esta atmósfera. "
                f"Encendida en un módulo cerrado, la presión podría multiplicarse por {fmt(r['pmax'] / presion, 1)}.")
    if clave == "hidrogeno":
        return (f"El hidrógeno arde entre {fmt(r['lfl'], 0)} % y {fmt(r['ufl'] or 100, 0)} % en esta atmósfera y se "
                "enciende con solo 0,017 mJ, unas 16 veces menos energía que el metano: casi cualquier chispa basta. "
                "Además, su llama es casi invisible.")
    if clave == "metano":
        return (f"El metano arde entre {fmt(r['lfl'], 1)} % y {fmt(r['ufl'] or 100, 1)} % en esta atmósfera. "
                f"Encendido en un módulo cerrado, la presión podría multiplicarse por {fmt(r['pmax'] / presion, 1)}.")
    if clave == "etanol":
        vapor = comb.presion_vapor_kpa("etanol", T) / presion * 100
        return (f"A {fmt(temperatura, 0)} °C el vapor de etanol puede llegar a {fmt(vapor, 1)} % en un espacio cerrado, "
                f"y su límite inferior es {fmt(r['lfl'], 1)} %: un derrame basta para formar una mezcla explosiva.")
    return (f"Su límite inferior es solo {fmt(r['lfl'], 2)} %: muy poco vapor ya forma una mezcla explosiva. "
            "En los ensayos FLEX de la NASA el heptano siguió reaccionando como «llama fría», sin llama visible.")


if es_gas and "lfl" in r:
    nombre_alerta = "Mezcla de gases" if mezcla else nombre(combustible)
    dato = dato_combustible(combustible)
    sobrepresion = r["pmax"] - presion
    if resistencia > 0 and sobrepresion > resistencia:
        dato += f" La sobrepresión ({fmt(sobrepresion, 0)} kPa) superaría lo que resiste el módulo ({fmt(resistencia, 0)} kPa)."
    if r["estado"] == "explosiva":
        st.error(f"**Alerta de explosión · {nombre_alerta}.** {dato}", icon="💥")
    elif r["estado"] == "rica":
        st.warning(f"**Mezcla demasiado rica · {nombre_alerta}.** Al mezclarse con aire pasará por la zona explosiva. {dato}", icon="⚠️")
    elif r["pct_lfl"] >= 25:
        st.warning(f"**Acercándose al límite · {nombre_alerta}.** {dato}", icon="⚠️")

# --------------------------------------------------------------------------
# Explosión
# --------------------------------------------------------------------------
ancla("explosion")
st.subheader("💥 Explosión")
if not es_gas:
    st.info("Los sólidos no forman una nube de gas explosiva. Revisa la sección «Espacio» para su comportamiento al arder.")
elif r["estado"] == "no_inflamable_atm":
    st.success("Con esta atmósfera la mezcla no puede arder a ninguna concentración.")
else:
    e1, e2, e3 = st.columns(3)
    e1.metric("Temperatura de llama", f"{fmt(r['tmax'], 0)} K",
              help="A volumen constante, en la concentración evaluada o en la más energética.")
    e2.metric("Aumento de presión", f"{fmt(r['pmax'] / presion, 1)} ×", help="Presión máxima / presión inicial.")
    if resistencia > 0:
        margen = resistencia - (r["pmax"] - presion)
        e3.metric("Margen estructural", f"{fmt(margen)} kPa", delta="resiste" if margen >= 0 else "falla",
                  delta_color="normal" if margen >= 0 else "inverse")
    else:
        e3.metric("Energía mínima de ignición", f"{fmt(r['mie'], 3)} mJ", help="Valor típico en aire; baja con más O₂.")

    with st.expander("Más resultados: oxígeno límite y velocidad de la explosión", expanded=True):
        loc = calc_loc(atm_t, fr_t, T, presion)
        ref = [O2_LIMITE_REFERENCIA[c] for c in fracciones if c in O2_LIMITE_REFERENCIA]
        st.markdown(f"**O₂ mínimo para que arda:** {fmt(loc) + ' %' if loc else 'no arde ni con O₂ puro'} (modelo)"
                    + (f" · {fmt(min(ref))} % publicado con N₂" if ref else ""))
        if set(fracciones) <= {"hidrogeno", "metano"}:
            if st.button("Calcular velocidad de llama (tarda unos segundos)"):
                x_vel = x if r["estado"] == "explosiva" else ventana["x_pico"] / 100
                with st.spinner("Resolviendo la llama con GRI-Mech 3.0…"):
                    su = calc_velocidad(atm_t, fr_t, x_vel, T, presion)
                if su is None:
                    st.warning("No se pudo resolver la llama con esta atmósfera.")
                else:
                    kg = comb.indice_deflagracion(presion, r["pmax"], su)
                    tiempo = (r["pmax"] - presion) / 100 / (kg / volumen ** (1 / 3)) * 1000
                    st.markdown(f"**Velocidad de llama:** {fmt(su, 2)} m/s · **K_G:** {fmt(kg, 0)} bar·m/s · "
                                f"**subida de presión en el módulo:** ~{fmt(tiempo, 0)} ms")
        else:
            st.caption("La velocidad de llama detallada está disponible para hidrógeno y metano.")
        st.caption("Supuestos: mezcla homogénea, presión máxima sin pérdidas de calor (AICC), límites por "
                   "método CAFT. Para hidrógeno el modelo subestima el O₂ mínimo; usa el valor publicado.")

# --------------------------------------------------------------------------
# Fuga en el tiempo
# --------------------------------------------------------------------------
ancla("fuga")
st.subheader("⏱ Evolución de la fuga")
if not es_gas:
    st.info("La simulación de fuga aplica a gases y vapores.")
else:
    t = np.linspace(0, duracion, 240)
    xs = fuga.concentracion(t, volumen, caudal, renovaciones, x_max) * 100
    fig = go.Figure()
    if "lfl" in r:
        fig.add_hrect(y0=r["lfl"], y1=r["ufl"] or 100, fillcolor="#ff5a50", opacity=0.13, line_width=0,
                      annotation_text="zona explosiva", annotation_position="top left")
        for frac, etiqueta in [(0.10, "alarma 10 %"), (0.25, "alarma 25 %")]:
            fig.add_hline(y=r["lfl"] * frac, line_dash="dot", line_color="#f0c66e",
                          annotation_text=etiqueta, annotation_position="bottom right")
    fig.add_trace(go.Scatter(x=t, y=xs, mode="lines", line=dict(color="#70d8c4", width=3), name="Concentración"))
    if t_eval is not None:
        fig.add_vline(x=t_eval, line_color="#e8eef1", line_dash="dash")
    tope = max(xs.max() * 1.25, (r.get("lfl") or 0) * 1.4, 0.5)
    fig.update_layout(template="plotly_dark", height=320, margin=dict(l=10, r=10, t=20, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
                      xaxis_title="Tiempo (min)", yaxis=dict(title="Combustible en el aire (%)", range=[0, tope]))
    st.plotly_chart(fig, width="stretch")
    nota = f"Estado estable: {fmt(fuga.estable(volumen, caudal, renovaciones, x_max) * 100, 2)} %."
    if x_max < 1:
        nota += f" El vapor se satura en {fmt(x_max * 100, 1)} % a esta temperatura y presión."
    if gravedad < 0.1:
        nota += " En microgravedad sin ventilación, cerca de la fuga la concentración es mayor que este promedio."
    st.caption(nota)

# --------------------------------------------------------------------------
# Asistente
# --------------------------------------------------------------------------
ancla("sugerencias")
st.subheader("💡 Sugerencias")
contexto = {
    "combustible": {nombre(c): round(f / sum(fracciones.values()) * 100, 1) for c, f in fracciones.items()} or nombre(combustible),
    "gravedad_m_s2": gravedad, "aire_m_s": viento, "presion_kPa": presion, "temperatura_C": temperatura,
    "atmosfera_pct": {NOMBRE_GAS.get(g, g): round(v, 2) for g, v in atmosfera.items()},
    "pO2_kPa": round(po2, 2), "estado": r["estado"], "combustible_en_aire_pct": round(x * 100, 3),
    "LFL_pct": r.get("lfl") and round(r["lfl"], 2), "UFL_pct": r.get("ufl") and round(r["ufl"], 2),
    "presion_explosion_kPa": r.get("pmax") and round(r["pmax"], 1),
    "minutos_hasta_LFL": r["tiempo_lfl"] and round(r["tiempo_lfl"], 1),
    "volumen_m3": volumen, "fuga_L_min": caudal, "renovaciones_h": renovaciones,
}

# Sugerencias: advertencias y soluciones. Con clave de API las redacta Claude a partir del cálculo físico.
o2_limite = None
if es_gas and "lfl" in r:
    referencias = [O2_LIMITE_REFERENCIA[c] for c in fracciones if c in O2_LIMITE_REFERENCIA]
    o2_limite = min(referencias) if referencias else calc_loc(atm_t, fr_t, T, presion)
avisos, soluciones = sugerencias.generar(r, {
    "es_gas": es_gas, "nombre": "La mezcla" if mezcla else nombre(combustible), "volumen": volumen,
    "caudal": caudal, "renovaciones": renovaciones, "gravedad": gravedad, "o2_pct": o2_atm * 100,
    "energia": energia, "presion": presion, "resistencia": resistencia, "o2_limite": o2_limite, "origen": origen})
clave_escenario = json.dumps(contexto, sort_keys=True, default=str)
# Advertencias y soluciones siempre visibles (modelo físico). Con clave de API, Claude puede redactarlas.
guardada = st.session_state.get("sugerencias_ia")
if asistente.disponible() and st.button("✦ Redactar con IA", key="btn_sugerencias"):
    with st.container(border=True):
        texto = st.write_stream(asistente.sugerir(
            {**contexto, "advertencias_calculadas": avisos, "soluciones_calculadas": soluciones}))
    st.session_state.sugerencias_ia = guardada = {"clave": clave_escenario, "texto": texto}
elif guardada and guardada["clave"] == clave_escenario:
    with st.container(border=True):
        st.markdown(guardada["texto"])
col_a, col_s = st.columns(2, gap="medium")
salto = chr(10)
with col_a.container(border=True):
    st.markdown("#### " + "⚠️ Advertencias" + salto + (salto.join(f"- {t}" for t in avisos) or "- Sin advertencias."))
with col_s.container(border=True):
    st.markdown("#### " + "✅ Soluciones" + salto + salto.join(f"- {t}" for t in soluciones))

# El asistente vive en un panel inferior que se abre desde el centro de la rueda de atajos.
with st.container(key="panel_asistente"):
    ancla("asistente")
    st.subheader("✦ Asistente IA")
    st.caption(asistente.explicacion_local(r))
    historial = st.session_state.setdefault("chat", [])
    for m in historial:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    def elegir_sugerencia():
        st.session_state.pendiente = st.session_state.sugerencia
        st.session_state.sugerencia = None


    st.pills("Preguntas rápidas", [q for q in ("¿Por qué da este resultado?", "¿Qué cambio lo haría más seguro?",
                                                   "¿Cómo cambia en microgravedad?")], key="sugerencia",
             on_change=elegir_sugerencia, label_visibility="collapsed")
    with st.container():
        pregunta = st.chat_input("Pregunta sobre este escenario…") or st.session_state.pop("pendiente", None)
    if pregunta:
        historial.append({"role": "user", "content": pregunta})
        with st.chat_message("user"):
            st.markdown(pregunta)
        with st.chat_message("assistant"):
            respuesta = st.write_stream(asistente.responder(historial, contexto))
        historial.append({"role": "assistant", "content": respuesta})


# --------------------------------------------------------------------------
# Cómo arde en el espacio
# --------------------------------------------------------------------------
ancla("espacio")
st.subheader("🪐 Cómo arde en el espacio")
regimen = "micro" if gravedad < 0.1 else ("parcial" if gravedad < 9 else "tierra")
info = COMBUSTIBLES[combustible]
cols = st.columns(3)
for col, (clave, titulo) in zip(cols, [("tierra", "Tierra · 1 g"), ("parcial", "Luna y Marte"), ("micro", "Órbita")]):
    css = "regimen-actual" if clave == regimen else "regimen"
    extra = " · " + "tu escenario" if clave == regimen else ""
    col.markdown(f'<div class="{css}"><h4>{titulo}{extra}</h4>{info["espacio"][clave]}</div>', unsafe_allow_html=True)
st.caption(f"Ensayos de referencia: {info['ensayos']}")
with st.expander("Comparar todos en microgravedad"):
    st.dataframe({"Combustible": [v["nombre"] for v in COMBUSTIBLES.values()],
                  "En órbita": [v["espacio"]["micro"] for v in COMBUSTIBLES.values()],
                  "Ensayos": [v["ensayos"] for v in COMBUSTIBLES.values()]},
                 hide_index=True, width="stretch")

# --------------------------------------------------------------------------
# Fuentes
# --------------------------------------------------------------------------
ancla("fuentes")
st.subheader("📚 Fuentes para verificar")
st.markdown(
    f"- [Ensayos de {info['nombre'].lower()} en vuelo (NASA NTRS)]({NTRS}{info['consulta'].replace(' ', '+')})\n"
    f"- [NASA-STD-6001: inflamabilidad de materiales]({NASA_STD_6001})\n"
    f"- [Oxígeno y seguridad de cabina (NASA NTRS)]({NTRS}spacecraft+fire+oxygen+partial+pressure)\n"
    "- [Cantera: equilibrio químico y llamas](https://cantera.org)\n"
    "- Atmósferas de referencia (pO₂): " + ", ".join(f"{n} {fmt(v)} kPa" for n, v in PO2_REFERENCIAS)
)
st.caption("Los límites de inflamabilidad, la energía de ignición y el O₂ límite publicados están en "
           "motor/datos.py. Verifícalos antes de usar el simulador en un trabajo formal.")
