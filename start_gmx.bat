@echo off
chcp 65001 >nul
echo ==========================================
echo   GROMACS-GUI 启动脚本（虚拟环境: gmx）
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/4] 激活虚拟环境 gmx ...
call gmx\Scripts\activate.bat
if errorlevel 1 (
    echo 错误：找不到 gmx 虚拟环境！
    echo 请先运行以下命令创建：
    echo   python -m venv gmx
    pause
    exit /b
)
echo 虚拟环境已激活: %VIRTUAL_ENV%

echo.
echo [2/4] 检查 gmx 命令...
gmx --version >nul 2>&1
if errorlevel 1 (
    echo 警告：gmx 命令未找到！请确认已加入系统 PATH
) else (
    echo gmx 可用
)

echo.
echo [3/4] 启动 GROMACS-GUI ...
python src\main.py

echo.
echo 程序已退出。
pause
