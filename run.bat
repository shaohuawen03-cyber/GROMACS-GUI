@echo off
chcp 65001 >nul
echo ===================================
echo     GROMACS-GUI 启动脚本 (Windows)
echo ===================================
echo.

echo [1/3] 检查 Python...
python --version
if errorlevel 1 (
    echo 错误：未找到 Python，请先安装 Python 3.8+
    pause
    exit /b
)

echo.
echo [2/3] 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 警告：依赖安装可能有问题，继续尝试启动...
)

echo.
echo [3/3] 启动 GROMACS-GUI...
echo.
echo 注意：请确保 gmx 已在系统环境变量 PATH 中！
echo 如果 gmx 不在 PATH，请先运行：
echo    set GMX_PATH=C:\你的\gmx.exe 路径
echo.

python src\main.py

pause
