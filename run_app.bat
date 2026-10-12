@echo off
chcp 65001 >nul
title Pāṇini Vyākaraṇa Sandhi Engine - Web App
echo ========================================================
echo   🕉️  Pāṇini Vyākaraṇa Sandhi Rule Engine
echo       पाणिनीय-व्याकरण-सन्धिनियम-तन्त्रम्
echo ========================================================
echo Starting Streamlit Web Application...
echo.

if not exist ".venv\Scripts\streamlit.exe" (
    echo Error: Virtual environment not found.
    echo Please make sure .venv is created.
    pause
    exit /b 1
)

".venv\Scripts\streamlit.exe" run app.py
pause
