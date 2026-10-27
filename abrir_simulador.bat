@echo off
cd /d "%~dp0"
echo Abriendo el simulador... (no cierres esta ventana mientras lo usas)
python -m streamlit run streamlit_app.py
pause
