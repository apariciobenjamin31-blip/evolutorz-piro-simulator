"""Asistente de IA que explica el escenario con Claude.

Los números los calcula el motor físico; el asistente solo los interpreta y responde
preguntas. Necesita credenciales de Anthropic (variable ANTHROPIC_API_KEY o `ant auth login`).
"""
from __future__ import annotations

import json
from collections.abc import Iterator

import anthropic

MODELO = "claude-opus-5-5"

SISTEMA = """Eres el asistente científico de Evolutorz, un simulador de combustión y explosiones \
en hábitats espaciales inspirado en la NASA.

Recibirás el escenario actual y los resultados del motor físico (Cantera) en JSON. Reglas:
- Responde en español, claro y breve: 2 a 5 frases o una lista corta.
- Usa solo los números del JSON. No inventes valores; si falta un dato, dilo.
- Explica qué significa el resultado y qué variable lo cambiaría más.
- Recuerda que son estimaciones: límites por el método CAFT y presión máxima AICC (sin pérdidas \
de calor), con una mezcla homogénea. No son predicciones validadas ni sustituyen ensayos.
- Ante una pregunta de seguridad real, recomienda consultar a ingeniería de seguridad de la misión."""


def disponible() -> bool:
    """True si hay credenciales de Anthropic (variable de entorno o perfil de `ant auth login`)."""
    import os
    import pathlib
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
                or (pathlib.Path.home() / ".config" / "anthropic").exists())


SISTEMA_SUGERENCIAS = SISTEMA + """

Ahora te piden sugerencias. Responde solo con dos secciones en Markdown, sin introducción:
### ⚠️ Advertencias
(3 o 4 viñetas: los riesgos más importantes del escenario, con sus números)
### ✅ Soluciones
(3 o 4 viñetas: acciones concretas y priorizadas, con el número que las justifica)
Usa como base las sugerencias calculadas que vienen en el JSON; puedes reordenarlas, combinarlas o \
añadir otra si los datos la respaldan."""


def responder(historial: list[dict], contexto: dict) -> Iterator[str]:
    """Genera la respuesta en fragmentos de texto para mostrarla mientras llega."""
    mensajes = list(historial)
    mensajes[-1] = {
        "role": "user",
        "content": "Escenario y resultados actuales:\n```json\n"
                   + json.dumps(contexto, ensure_ascii=False, indent=1)
                   + "\n```\n\nPregunta: " + historial[-1]["content"],
    }
    yield from _transmitir(SISTEMA, mensajes)


def sugerir(contexto: dict) -> Iterator[str]:
    """Advertencias y soluciones para el escenario, redactadas por Claude."""
    mensajes = [{"role": "user", "content": "Escenario, resultados y sugerencias calculadas:\n```json\n"
                 + json.dumps(contexto, ensure_ascii=False, indent=1) + "\n```"}]
    yield from _transmitir(SISTEMA_SUGERENCIAS, mensajes)


def _transmitir(sistema: str, mensajes: list[dict]) -> Iterator[str]:
    try:
        cliente = anthropic.Anthropic()
        with cliente.beta.messages.stream(
            model=MODELO,
            max_tokens=4000,
            system=sistema,
            messages=mensajes,
            output_config={"effort": "low"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        ) as flujo:
            yield from flujo.text_stream
            final = flujo.get_final_message()
        if final.stop_reason == "refusal":
            yield "\n\n_El asistente no pudo responder esta pregunta._"
        elif final.stop_reason == "max_tokens":
            yield "\n\n_La respuesta se cortó por longitud._"
    except anthropic.AuthenticationError:
        yield "No hay una clave válida de Anthropic. Configura `ANTHROPIC_API_KEY` y vuelve a abrir el simulador."
    except anthropic.RateLimitError:
        yield "Se alcanzó el límite de uso de la API. Espera un minuto y vuelve a preguntar."
    except anthropic.APIConnectionError:
        yield "No hay conexión con la API de Anthropic. Revisa tu internet."
    except anthropic.APIStatusError as error:
        yield f"La API devolvió un error ({error.status_code}). Intenta de nuevo más tarde."
    except Exception:
        yield ("No encontré credenciales de Anthropic. Configura la variable `ANTHROPIC_API_KEY` "
               "o ejecuta `ant auth login` y vuelve a abrir el simulador.")


def explicacion_local(resumen: dict) -> str:
    """Explicación breve sin IA, para cuando no hay credenciales."""
    estado = resumen["estado"]
    if estado == "sin_gas":
        return ("El combustible elegido es sólido: no forma una nube de gas explosiva. "
                "El riesgo principal es un incendio con humo y gases tóxicos.")
    if estado == "no_inflamable_atm":
        return ("Con esta atmósfera no se alcanza la temperatura necesaria para que la llama se "
                "propague a ninguna concentración: falta oxígeno o sobra gas inerte.")
    texto = {
        "pobre": "La concentración está por debajo del límite inferior: la mezcla aún no puede arder.",
        "explosiva": "La concentración está dentro de la ventana inflamable: una chispa podría causar una explosión.",
        "rica": "La concentración supera el límite superior: no arde así, pero al mezclarse con aire puede volverse explosiva.",
    }[estado]
    if resumen.get("tiempo_lfl") is not None:
        texto += f" Con esta fuga, el módulo alcanzaría el límite inferior en {resumen['tiempo_lfl']:.0f} min."
    return texto
