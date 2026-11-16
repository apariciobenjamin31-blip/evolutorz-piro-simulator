"""Cálculos de combustión y explosión con Cantera.

Métodos (todos de fase gas, mezcla homogénea):
- Temperatura adiabática de llama: equilibrio químico a entalpía y presión constantes (HP).
- Presión máxima de explosión confinada: equilibrio a energía interna y volumen
  constantes (UV), conocido como AICC. Es un límite superior: ignora pérdidas de calor.
- Límites de inflamabilidad: método CAFT (temperatura adiabática calculada en el límite).
  El umbral de temperatura de cada combustible se calibra para reproducir sus límites
  publicados en aire a 25 °C y 1 atm, y luego se aplica a la atmósfera, presión y
  temperatura del escenario. Es una estimación: los límites reales se miden en ensayos.
"""
from __future__ import annotations

import functools
import math

import cantera as ct
import numpy as np

from .datos import COMBUSTIBLES

T_REF = 298.15
AIRE = {"N2": 78.08, "O2": 20.95, "Ar": 0.93, "CO2": 0.04}
# Especies de la atmósfera y productos de combustión que entran en el equilibrio.
ESPECIES_BASE = ("N2", "O2", "Ar", "He", "CO2", "CO", "H2O", "H2", "OH", "H", "O",
                 "NO", "CH4", "HO2", "H2O2")


@functools.lru_cache(maxsize=1)
def _base_de_especies() -> dict[str, ct.Species]:
    return {s.name: s for s in ct.Species.list_from_file("nasa_gas.yaml")}


@functools.lru_cache(maxsize=None)
def _fase(combustibles: tuple[str, ...]) -> ct.Solution:
    base = _base_de_especies()
    nombres = list(ESPECIES_BASE) + [COMBUSTIBLES[c]["especie"] for c in combustibles]
    especies = [base[n] for n in dict.fromkeys(nombres) if n in base]
    return ct.Solution(thermo="ideal-gas", species=especies)


def composicion(atmosfera: dict[str, float], fracciones: dict[str, float], x_comb: float) -> dict[str, float]:
    """Mezcla molar: x_comb de combustible (repartido según `fracciones`) y el resto atmósfera."""
    total_atm = sum(atmosfera.values()) or 1.0
    total_comb = sum(fracciones.values()) or 1.0
    mezcla = {gas: (1 - x_comb) * v / total_atm for gas, v in atmosfera.items() if v > 0}
    for comb, f in fracciones.items():
        especie = COMBUSTIBLES[comb]["especie"]
        mezcla[especie] = mezcla.get(especie, 0.0) + x_comb * f / total_comb
    return mezcla


def _estado(fracciones, mezcla, T, P_kpa):
    gas = _fase(tuple(sorted(fracciones)))
    gas.TPX = T, P_kpa * 1000.0, mezcla
    return gas


def _o2_por_mol(gas, especie) -> float:
    """Moles de O₂ que consume la combustión completa de 1 mol de la especie."""
    return (gas.n_atoms(especie, "C") + gas.n_atoms(especie, "H") / 4
            - gas.n_atoms(especie, "O") / 2)


def t_adiabatica(fracciones, mezcla, T, P_kpa) -> float:
    """Temperatura adiabática. En mezclas ricas el combustible sobrante se trata como
    inerte (no se descompone), como hace el método CAFT para el límite superior."""
    gas = _estado(fracciones, mezcla, T, P_kpa)
    especies = [COMBUSTIBLES[c]["especie"] for c in fracciones]
    o2_necesario = sum(mezcla.get(e, 0.0) * _o2_por_mol(gas, e) for e in especies)
    o2_disponible = mezcla.get("O2", 0.0)
    if o2_necesario <= o2_disponible or o2_necesario == 0:
        gas.equilibrate("HP")
        return float(gas.T)

    h_inicial = gas.enthalpy_mass
    quemada = o2_disponible / o2_necesario          # fracción del combustible que arde
    parte_quemada = {g: v * (quemada if g in especies else 1.0) for g, v in mezcla.items()}
    sobrante = {e: mezcla.get(e, 0.0) * (1 - quemada) for e in especies}
    gas.TPX = T, P_kpa * 1000.0, parte_quemada
    gas.equilibrate("HP")
    masa_quemada = sum(parte_quemada.values()) * gas.mean_molecular_weight
    y = gas.Y * masa_quemada
    for e, n in sobrante.items():
        y[gas.species_index(e)] += n * gas.molecular_weights[gas.species_index(e)]
    gas.HPY = h_inicial, P_kpa * 1000.0, y / y.sum()
    return float(gas.T)


def explosion_confinada(fracciones, mezcla, T, P_kpa) -> tuple[float, float]:
    """Devuelve (presión máxima en kPa, temperatura en K) de la combustión a volumen constante."""
    gas = _estado(fracciones, mezcla, T, P_kpa)
    gas.equilibrate("UV")
    return float(gas.P / 1000.0), float(gas.T)


@functools.lru_cache(maxsize=None)
def umbrales(comb: str) -> tuple[float, float]:
    """Temperaturas adiabáticas en los límites publicados (aire, 25 °C, 1 atm)."""
    datos = COMBUSTIBLES[comb]
    fr = {comb: 1.0}
    t_inf = t_adiabatica(fr, composicion(AIRE, fr, datos["lfl"] / 100), T_REF, 101.325)
    t_sup = t_adiabatica(fr, composicion(AIRE, fr, datos["ufl"] / 100), T_REF, 101.325)
    return t_inf, t_sup


def _umbral_mezcla(fracciones) -> tuple[float, float]:
    total = sum(fracciones.values()) or 1.0
    inf = sum(umbrales(c)[0] * f / total for c, f in fracciones.items())
    sup = sum(umbrales(c)[1] * f / total for c, f in fracciones.items())
    return inf, sup


def _cruce(f, x_a, x_b, objetivo, pasos=18):
    """Bisección del punto donde f(x) cruza `objetivo` entre x_a y x_b."""
    f_a = f(x_a) - objetivo
    for _ in range(pasos):
        x_m = 0.5 * (x_a + x_b)
        f_m = f(x_m) - objetivo
        if (f_m > 0) == (f_a > 0):
            x_a, f_a = x_m, f_m
        else:
            x_b = x_m
    return 0.5 * (x_a + x_b)


def ventana(atmosfera, fracciones, T, P_kpa, puntos=48) -> dict:
    """Curva de temperatura adiabática y límites estimados para la atmósfera del escenario."""
    def tad(x):
        return t_adiabatica(fracciones, composicion(atmosfera, fracciones, x), T, P_kpa)

    xs = np.unique(np.concatenate([np.geomspace(0.002, 0.2, puntos // 2), np.linspace(0.2, 0.96, puntos // 2)]))
    ts = np.array([tad(x) for x in xs])
    t_inf, t_sup = _umbral_mezcla(fracciones)
    i_pico = int(np.argmax(ts))
    lfl = ufl = None
    if ts[i_pico] >= t_inf:
        pobres = np.nonzero(ts[: i_pico + 1] >= t_inf)[0]
        i = int(pobres[0])
        lfl = xs[0] if i == 0 else _cruce(tad, xs[i - 1], xs[i], t_inf)
    if ts[i_pico] >= t_sup:
        ricas = np.nonzero(ts[i_pico:] >= t_sup)[0]
        j = i_pico + int(ricas[-1])
        ufl = xs[-1] if j == len(xs) - 1 else _cruce(tad, xs[j], xs[j + 1], t_sup)
        if lfl is None or ufl < lfl:
            ufl = None
    return {
        "x": xs * 100, "t_ad": ts, "t_umbral_inf": t_inf, "t_umbral_sup": t_sup,
        "lfl": None if lfl is None else lfl * 100,
        "ufl": None if ufl is None else ufl * 100,
        "x_pico": float(xs[i_pico] * 100), "t_pico": float(ts[i_pico]),
    }


def oxigeno_limite(atmosfera, fracciones, T, P_kpa) -> float | None:
    """Concentración mínima de O₂ (% molar) con la que la mezcla aún puede arder.

    Se reemplaza O₂ por los demás gases de la atmósfera (o N₂ si no hay otros).
    """
    diluyente = {g: v for g, v in atmosfera.items() if g != "O2"} or {"N2": 100.0}
    total = sum(diluyente.values())

    def arde(o2):
        atm = {g: (100 - o2) * v / total for g, v in diluyente.items()}
        atm["O2"] = o2
        return ventana(atm, fracciones, T, P_kpa, puntos=28)["lfl"] is not None

    if not arde(100.0):
        return None
    bajo, alto = 0.0, 100.0
    for _ in range(10):
        medio = 0.5 * (bajo + alto)
        if arde(medio):
            alto = medio
        else:
            bajo = medio
    return alto


def presion_vapor_kpa(comb: str, T: float) -> float | None:
    """Presión de vapor (ecuación de Antoine) de un combustible líquido, en kPa."""
    antoine = COMBUSTIBLES[comb].get("antoine")
    if not antoine:
        return None
    a, b, c = antoine
    return 10 ** (a - b / (T - 273.15 + c)) * 0.133322


def velocidad_llama(atmosfera, fracciones, x_comb, T, P_kpa) -> float | None:
    """Velocidad de llama laminar en m/s con cinética GRI-Mech 3.0 (solo H₂ y CH₄).

    Tarda unos segundos. Devuelve None si el combustible o la atmósfera no están en GRI-Mech.
    """
    if not set(fracciones) <= {"hidrogeno", "metano"}:
        return None
    gas = ct.Solution("gri30.yaml")
    mezcla = composicion(atmosfera, fracciones, x_comb)
    if any(especie not in gas.species_names for especie in mezcla):
        return None
    gas.TPX = T, P_kpa * 1000.0, mezcla
    llama = ct.FreeFlame(gas, width=0.03)
    llama.set_refine_criteria(ratio=3, slope=0.1, curve=0.2)
    try:
        llama.solve(loglevel=0, auto=True)
    except ct.CanteraError:
        return None
    return float(llama.velocity[0])


def indice_deflagracion(p0_kpa, pmax_kpa, su, gamma=1.35) -> float:
    """Índice K_G (bar·m/s) del modelo de llama delgada de Dahoe et al. (2001)."""
    p0, pmax = p0_kpa / 100, pmax_kpa / 100
    return (36 * math.pi) ** (1 / 3) * p0 * su * (pmax / p0) ** (1 / gamma) * (pmax / p0 - 1)
