"""Advertencias y soluciones calculadas con el modelo físico (sin IA).

Sirven como respuesta cuando no hay credenciales de Anthropic y como base de datos
para que el asistente IA proponga sus propias sugerencias sin inventar números.
"""
from __future__ import annotations


def _f(valor, dec=1):
    return f"{valor:,.{dec}f}".replace(",", " ").replace(".", ",")


def generar(r: dict, e: dict) -> tuple[list[str], list[str]]:
    """Devuelve (advertencias, soluciones) para el escenario.

    r: resultados del motor (estado, x, lfl, ufl, pmax, tiempo_lfl, mie...).
    e: escenario (es_gas, nombre, volumen, caudal, renovaciones, gravedad, o2_pct,
       energia, presion, resistencia, o2_limite, origen).
    """
    avisos, soluciones = [], []
    micro = e["gravedad"] < 0.1

    if not e["es_gas"]:
        avisos.append(f"{e['nombre']} es un material sólido: no forma una nube explosiva, pero el humo y el monóxido "
                      "de carbono pueden afectar a la tripulación antes de que el fuego crezca.")
        if micro:
            avisos.append("En microgravedad el humo no sube hacia los detectores: se queda donde lo lleve la ventilación.")
        soluciones.append("Ante un incendio en la cabina, la respuesta habitual es cortar la ventilación y la energía "
                          "del equipo afectado para quitarle oxígeno y fuente de calor, y luego usar el extintor.")
        soluciones.append("Elegir materiales ensayados con NASA-STD-6001 en las condiciones de uso reduce la carga combustible.")
        if e["o2_pct"] > 21:
            avisos.append(f"La atmósfera tiene {_f(e['o2_pct'])} % de O₂: los sólidos arden con más facilidad que en aire.")
            soluciones.append("Volver a una atmósfera con 21 % de O₂ o menos reduce la inflamabilidad de los materiales.")
        return avisos, soluciones

    if r["estado"] == "no_inflamable_atm":
        avisos.append("Con esta atmósfera la mezcla no arde, pero si entra aire u oxígeno el riesgo vuelve.")
        soluciones.append("Mantener la atmósfera actual y vigilar la entrada de oxígeno.")
        return avisos, soluciones

    lfl, ufl, x = r["lfl"], r.get("ufl"), r["x"] * 100
    if r["estado"] == "explosiva":
        avisos.append(f"La mezcla está en la zona explosiva: {_f(x, 2)} % de {e['nombre'].lower()}, "
                      f"entre {_f(lfl, 1)} % y {_f(ufl or 100, 1)} %.")
    elif r["estado"] == "rica":
        avisos.append(f"Hay {_f(x, 1)} % de combustible, más que el límite superior ({_f(ufl, 1)} %). "
                      "Al ventilar pasará por la zona explosiva.")
    elif r["pct_lfl"] >= 10:
        avisos.append(f"La concentración ya es el {_f(r['pct_lfl'], 0)} % del límite inferior; "
                      "los detectores industriales alarman al 10 % y al 25 %.")

    if r.get("tiempo_lfl") is not None and r["estado"] == "pobre":
        avisos.append(f"Con esta fuga el módulo alcanzaría la mezcla explosiva en {_f(r['tiempo_lfl'], 0)} min.")
    if "pmax" in r:
        inicio = ("Si se enciende" if r["estado"] == "explosiva"
                  else "En el peor caso, si la mezcla llegara a la zona explosiva")
        texto = (f"{inicio}, la presión llegaría a ~{_f(r['pmax'], 0)} kPa "
                 f"({_f(r['pmax'] / e['presion'], 1)} veces la actual)")
        sobre = r["pmax"] - e["presion"]
        if e["resistencia"] > 0 and sobre > e["resistencia"]:
            texto += f", más de lo que resiste el módulo ({_f(e['resistencia'], 0)} kPa de sobrepresión)"
        avisos.append(texto + ".")
    if e["energia"] >= r["mie"]:
        avisos.append(f"La chispa configurada ({_f(e['energia'], 2)} mJ) supera la energía mínima de ignición "
                      f"({_f(r['mie'], 3)} mJ).")

    # Soluciones con números del modelo.
    if e["origen"] == "Fuga en el tiempo" and e["caudal"] > 0:
        q = e["caudal"] / 1000
        objetivo = 0.25 * lfl / 100
        renov = q * (1 / objetivo - 1) * 60 / e["volumen"]
        if renov > e["renovaciones"]:
            soluciones.append(f"Subir la ventilación a {_f(renov, 1)} renovaciones por hora mantiene el gas bajo el "
                              f"25 % del límite inferior (ahora hay {_f(e['renovaciones'], 1)}).")
        mitad = q / 2 / (q / 2 + e["renovaciones"] * e["volumen"] / 60) * 100
        soluciones.append(f"Reducir la fuga a la mitad bajaría la concentración estable a {_f(mitad, 2)} %.")
    elif r["estado"] in ("explosiva", "rica"):
        soluciones.append("Ventilar con aire limpio o con gas inerte hasta bajar del 25 % del límite inferior.")
    if e.get("o2_limite"):
        soluciones.append(f"Inertizar con nitrógeno hasta dejar el O₂ por debajo de {_f(e['o2_limite'], 1)} % impide que la mezcla "
                          f"arda (ahora hay {_f(e['o2_pct'], 1)} %).")
    soluciones.append(f"Eliminar fuentes de ignición: con {_f(r['mie'], 3)} mJ basta una pequeña descarga "
                      "electrostática. Apagar equipos eléctricos cercanos y no accionar interruptores.")
    if micro:
        soluciones.append("En microgravedad, poner detectores cerca de la posible fuga: el gas no sube y "
                          "cerca de la fuente la concentración es mayor que el promedio.")
    return avisos, soluciones
