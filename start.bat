@echo off
title 币安交易机器人
echo ========================================
echo   币安自动交易机器人
echo ========================================
echo.

REM 检查虚拟环境
if not exist ".venv" (
    echo 创建虚拟环境...
    python -m venv .venv
)
if not exist ".venv\Scripts\activate.bat" (
    echo ❌ 未找到虚拟环境，请先运行 install.bat
    pause
    exit /b 1
)

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 检查依赖
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ❌ 依赖缺失，正在安装...
    pip install -r requirements.txt
)

REM 启动 Streamlit
echo ✅ 启动中...
echo.
streamlit run app.py

pause
