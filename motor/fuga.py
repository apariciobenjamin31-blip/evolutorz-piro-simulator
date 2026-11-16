"""Evolución de una fuga de gas o vapor dentro de un módulo cerrado.

Modelo de mezcla perfecta (todo el volumen con la misma concentración):
    dx/dt = (q - (q + Q)·x) / V
con q = caudal de la fuga y Q = renovación de aire con atmósfera limpia. Solución:
    x(t) = q / (q + Q) · (1 - exp(-(q + Q)·t / V))
Cerca de la fuga la concentración real es mayor, sobre todo en microgravedad sin
ventilación, donde el gas no sube ni se dispersa por flotabilidad.
"""
from __future__ import annotations

import math

import numpy as np


def concentracion(t_min, volumen_m3, fuga_l_min, renovaciones_h, x_max=1.0):
    """Fracción molar del combustible en el tiempo (t en minutos)."""
    q = fuga_l_min / 1000.0            # m³/min
    Q = renovaciones_h * volumen_m3 / 60.0
    if q <= 0:
        return np.zeros_like(np.asarray(t_min, dtype=float))
    k = (q + Q) / volumen_m3
    x = q / (q + Q) * (1 - np.exp(-k * np.asarray(t_min, dtype=float)))
    return np.minimum(x, x_max)


def tiempo_hasta(fraccion, volumen_m3, fuga_l_min, renovaciones_h, x_max=1.0):
    """Minutos hasta alcanzar `fraccion`; None si nunca se alcanza."""
    q = fuga_l_min / 1000.0
    Q = renovaciones_h * volumen_m3 / 60.0
    if q <= 0:
        return None
    x_estable = min(q / (q + Q), x_max)
    if fraccion >= x_estable:
        return None
    k = (q + Q) / volumen_m3
    return -math.log(1 - fraccion * (q + Q) / q) / k


def estable(volumen_m3, fuga_l_min, renovaciones_h, x_max=1.0):
    q = fuga_l_min / 1000.0
    Q = renovaciones_h * volumen_m3 / 60.0
    return 0.0 if q <= 0 else min(q / (q + Q), x_max)
