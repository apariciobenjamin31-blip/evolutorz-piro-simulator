# Piro-Simulator · equipo Evolutorz

Simulador de fuego y explosiones en hábitats espaciales (NASA Space Apps), en Python con Cantera y Streamlit.

- **App publicada:** https://piro-simulator.streamlit.app (Streamlit Community Cloud, Python 3.12). Cada push a `main` la vuelve a desplegar: no subas nada que no funcione.
- **Repositorio:** https://github.com/apariciobenjamin31-blip/evolutorz-piro-simulator (público).
- **Idioma de trabajo e interfaz:** español. Ahorra tokens y adapta el esfuerzo a la tarea. En tareas grandes, pregunta antes de empezar.

## Ejecutar y probar

```bash
pip install -r requirements.txt
streamlit run app.py
python -m pytest
```

En el equipo del autor (Windows) el entorno está en `%USERPROFILE%\.venvs\evolutorz` (fuera de OneDrive); `iniciar.bat` lo usa.

## Estructura

- `app.py`: interfaz completa (barra lateral por grupos, llama, resumen, explosión, fuga, sugerencias, asistente, espacio, fuentes).
- `motor/combustion.py`: Cantera (equilibrio HP, AICC, límites por CAFT, O₂ límite por bisección, FreeFlame con GRI-Mech 3.0).
- `motor/datos.py`: combustibles, atmósferas y valores publicados con sus fuentes.
- `motor/fuga.py`, `motor/sugerencias.py`, `motor/asistente.py` (Claude; necesita `ANTHROPIC_API_KEY`).
- `componentes/llama.html` (llama, brasas, explosión) y `componentes/arco.html` (rueda de atajos, se inyecta con un iframe porque `st.html` quita los scripts).
- `tests/test_motor.py`: 9 pruebas contra valores publicados.

## Reglas

- **Nunca** subas claves ni secretos. La clave de Anthropic va en *Settings → Secrets* de Streamlit Cloud o en una variable de entorno.
- Commits con el correo privado de GitHub `246191846+apariciobenjamin31-blip@users.noreply.github.com`, nunca el correo personal. Terminan con `Co-Authored-By: Claude …`.
- Esta es la versión pública de la expo: **sin modo maya**. La versión con maya y la variante con la sección NASA/PSI viven en otras carpetas del autor y no se publican aquí sin que lo pida.
- Valores físicos: usa solo datos con fuente; si falta un dato, dilo en vez de inventarlo. Limitación conocida: el modelo subestima el O₂ límite del hidrógeno (≈2 % frente a 5 % publicado).
- Tras cambiar módulos de `motor/` hay que reiniciar Streamlit.
