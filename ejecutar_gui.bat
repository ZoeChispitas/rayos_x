@echo off
REM Activa el entorno virtual y ejecuta la interfaz grafica
cd /d "%~dp0"
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    python rayosx_gui.py
) else (
    echo No se encontro venv. Crealo con: python -m venv venv
    pause
)
