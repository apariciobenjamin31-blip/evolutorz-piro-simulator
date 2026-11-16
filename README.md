# 🔥 Piro-Simulator · Equipo Evolutorz

**Simulador de fuego y explosiones en hábitats espaciales** · *Fire and explosion simulator for space habitats*

🌐 **Pruébalo / Try it:** https://piro-simulator.streamlit.app

> ¿Qué pasaría si pudiéramos predecir una explosión antes de que ocurra?
> *What if we could predict an explosion before it happens?*

---

## English

Piro-Simulator predicts when a scenario inside a spacecraft, space station, lunar or Martian base is approaching a fire or explosion, before it is ever reproduced in the real world. It combines a physical combustion model (Cantera, NASA thermodynamic data) with an AI assistant.

**What it does**

- Flammability window of hydrogen, methane, ethanol, n-heptane and gas mixtures in any atmosphere, pressure and temperature (calibrated CAFT method).
- Maximum explosion pressure in a closed module (AICC), limiting oxygen concentration and minimum ignition energy.
- Leak in a module over time: gas concentration, early (10 % LFL) and high (25 % LFL) alarms, and time until the mixture becomes explosive.
- Gravity (orbit, Moon, Mars, Earth), airflow and atmosphere (cabin air, NASA exploration atmosphere, EVA suit, Mars, Venus, Titan, inert gases or a custom mix).
- Animated flame that changes shape with gravity and airflow (teardrop on Earth, blue sphere in microgravity), and an explosion animation.
- Warnings and solutions computed by the model, plus an AI assistant (Claude) when an API key is configured.

**Limits:** estimates for exploring scenarios, not validated predictions; they do not replace testing. The model underestimates the limiting oxygen of hydrogen (≈2 % vs 5 % published).

## Español

Piro-Simulator predice cuándo un escenario dentro de una nave, una estación espacial o una base en la Luna o Marte se acerca a un incendio o una explosión, antes de reproducirlo en el mundo real. Combina un modelo físico de combustión (Cantera, datos termodinámicos de la NASA) con un asistente IA.

**Qué hace**

- Ventana de inflamabilidad de hidrógeno, metano, etanol, n-heptano y mezclas en cualquier atmósfera, presión y temperatura (método CAFT calibrado).
- Presión máxima de explosión en un módulo cerrado (AICC), O₂ mínimo para arder y energía mínima de ignición.
- Fuga en un módulo en el tiempo: concentración, alarmas temprana (10 % del LFL) y alta (25 % del LFL) y tiempo hasta la mezcla explosiva.
- Gravedad (órbita, Luna, Marte, Tierra), flujo de aire y atmósfera (cabina, exploración NASA, traje EVA, Marte, Venus, Titán, gases inertes o composición propia).
- Llama animada que cambia de forma con la gravedad y el aire (lágrima en la Tierra, esfera azul en microgravedad) y animación de explosión.
- Advertencias y soluciones calculadas por el modelo, y asistente IA (Claude) si hay clave de API.

**Límites:** son estimaciones para explorar escenarios, no predicciones validadas; no sustituyen ensayos. El modelo subestima el O₂ límite del hidrógeno (≈2 % frente a 5 % publicado).

---

## Ejecutar en tu equipo / Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

En Windows también puedes hacer doble clic en `iniciar.bat`. / On Windows you can also double-click `iniciar.bat`.

Pruebas / Tests: `python -m pytest`

**Asistente IA / AI assistant (opcional):** define `ANTHROPIC_API_KEY` como variable de entorno o, en Streamlit Cloud, en *Settings → Secrets*. Nunca la subas al repositorio. / Set `ANTHROPIC_API_KEY` as an environment variable or in Streamlit Cloud *Settings → Secrets*. Never commit it.

## Archivos / Files

| Archivo | Contenido / Contents |
|---|---|
| `app.py` | Interfaz (Streamlit) / User interface |
| `motor/combustion.py` | Cálculos con Cantera / Cantera calculations |
| `motor/datos.py` | Combustibles, atmósferas y valores publicados con fuentes / Fuels, atmospheres and published values with sources |
| `motor/fuga.py` | Modelo de fuga / Leak model |
| `motor/sugerencias.py` | Advertencias y soluciones / Warnings and solutions |
| `motor/asistente.py` | Asistente con Claude / Claude assistant |
| `componentes/` | Llama animada y menú de atajos / Animated flame and shortcut wheel |
| `tests/test_motor.py` | Validación contra valores publicados / Validation against published values |

Hecho para NASA Space Apps Challenge · Built for the NASA Space Apps Challenge.
