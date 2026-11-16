@echo off
rem Abre el simulador Evolutorz en el navegador (http://localhost:8501).
rem El entorno de Python vive fuera de OneDrive, en %USERPROFILE%\.venvs\evolutorz.
cd /d "%~dp0"
set "VENV=%USERPROFILE%\.venvs\evolutorz"
if not exist "%VENV%\Scripts\streamlit.exe" (
  echo Creando el entorno de Python por primera vez...
  python -m venv "%VENV%"
  "%VENV%\Scripts\python.exe" -m pip install -r requirements.txt
)
"%VENV%\Scripts\streamlit.exe" run app.py --server.port 8501
