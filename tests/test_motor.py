"""Comprueba el motor contra valores publicados. Ejecutar: .venv\\Scripts\\python -m pytest"""
import pytest

from motor import combustion as comb, fuga
from motor.datos import ATMOSFERAS, COMBUSTIBLES, GASES_COMBUSTIBLES

AIRE = ATMOSFERAS["cabina"]["gases"]


@pytest.mark.parametrize("comb_id", GASES_COMBUSTIBLES)
def test_reproduce_limites_publicados_en_aire(comb_id):
    v = comb.ventana(AIRE, {comb_id: 1.0}, 298.15, 101.325)
    assert v["lfl"] == pytest.approx(COMBUSTIBLES[comb_id]["lfl"], rel=0.03)
    assert v["ufl"] == pytest.approx(COMBUSTIBLES[comb_id]["ufl"], rel=0.03)


def test_temperatura_estequiometrica_del_metano():
    fr = {"metano": 1.0}
    t = comb.t_adiabatica(fr, comb.composicion(AIRE, fr, 0.095), 298.15, 101.325)
    assert t == pytest.approx(2226, abs=15)


def test_presion_maxima_de_metano_e_hidrogeno():
    for comb_id, x, esperado in [("metano", 0.095, 890), ("hidrogeno", 0.296, 815)]:
        fr = {comb_id: 1.0}
        p, _ = comb.explosion_confinada(fr, comb.composicion(AIRE, fr, x), 298.15, 101.325)
        assert p == pytest.approx(esperado, rel=0.03)


def test_oxigeno_limite_del_metano():
    assert comb.oxigeno_limite(AIRE, {"metano": 1.0}, 298.15, 101.325) == pytest.approx(12, abs=1.5)


def test_atmosfera_exterior_de_marte_no_permite_arder():
    marte = ATMOSFERAS["marte"]
    assert comb.ventana(marte["gases"], {"metano": 1.0}, 298.15, marte["presion"])["lfl"] is None


def test_fuga_converge_al_estado_estable():
    assert fuga.concentracion(10_000, 75, 20, 2) == pytest.approx(fuga.estable(75, 20, 2))
    assert fuga.tiempo_hasta(0.5, 75, 20, 2) is None
