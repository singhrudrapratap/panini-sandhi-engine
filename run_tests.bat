@echo off
chcp 65001 >nul
title Pāṇini Vyākaraṇa Sandhi Engine - Test Suite
echo ========================================================
echo   🕉️  Running Sandhi Engine Automated Test Suite
echo       पाणिनीय-सन्धिनियम-परीक्षण-सञ्चयः
echo ========================================================
echo.

if not exist ".venv\Scripts\pytest.exe" (
    echo Error: Virtual environment not found.
    echo Please make sure .venv is created.
    pause
    exit /b 1
)

".venv\Scripts\pytest.exe" tests\test_sandhi.py -v
echo.
pause
