@echo off
chcp 65001 >nul
title 🔧 币安交易机器人 - 安装程序
color 0B

echo.
echo ========================================
echo   🔧 币安交易机器人 - 安装程序
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未检测到 Python
    echo.
    echo 请先安装 Python 3.8+:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python 已安装
python --version
echo.

REM 创建虚拟环境
if exist ".venv" (
    echo ⚠️  虚拟环境已存在，是否重新创建? (Y/N)
    set /p RECREATE=
    if /i "%RECREATE%"=="Y" (
        echo 删除旧虚拟环境...
        rmdir /s /q .venv
    ) else (
        echo 使用现有虚拟环境
        goto :install_deps
    )
)

echo 📦 创建虚拟环境...
python -m venv .venv
if errorlevel 1 (
    echo ❌ 虚拟环境创建失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境创建成功
echo.

:install_deps
REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 升级 pip
echo 🔄 升级 pip...
python -m pip install --upgrade pip
echo.

REM 安装依赖
echo 📥 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ❌ 依赖安装失败
    echo.
    echo 尝试使用国内镜像源...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo ❌ 安装仍然失败，请检查网络连接
        pause
        exit /b 1
    )
)

echo.
echo ✅ 所有依赖安装成功!
echo.

REM 创建 .env 文件
if not exist ".env" (
    if exist ".env.example" (
        echo 📝 创建配置文件...
        copy .env.example .env >nul
        echo ✅ 已创建 .env 文件
        echo.
        echo ⚠️  重要: 请编辑 .env 文件，填入你的币安 API 密钥
        echo.
    )
)

echo ========================================
echo   🎉 安装完成!
echo ========================================
echo.
echo 下一步:
echo   1. 编辑 .env 文件，配置 API 密钥
echo   2. 双击 start.bat 启动程序
echo   3. 浏览器访问 http://localhost:8501
echo.
echo 文档:
echo   - README.md: 完整使用说明
echo   - QUICKSTART.md: 快速开始指南
echo.
pause
