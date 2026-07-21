@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo =====================================================
echo   彻底重建干净的 GROMACS-GUI 虚拟环境 (gmx)
echo   使用系统 Python + PyQt6 6.6.1 稳定版
echo =====================================================
echo.

echo [1/6] 删除旧的 gmx 环境...
if exist gmx rmdir /s /q gmx

echo [2/6] 使用系统 Python 创建全新虚拟环境...
python -m venv gmx

if errorlevel 1 (
    echo 创建失败！请确保系统 python 命令可用。
    pause
    exit /b
)

echo [3/6] 激活新环境...
call gmx\Scripts\activate.bat

echo [4/6] 升级 pip...
python -m pip install --upgrade pip

echo [5/6] 安装稳定版依赖 (PyQt6 6.6.1)...
pip install "PyQt6==6.6.1" "PyQt6-Qt6==6.6.1" matplotlib numpy

echo [6/6] 测试 PyQt6...
python -c "from PyQt6.QtCore import QCoreApplication; print('✅ PyQt6 6.6.1 在新环境中加载成功！')"

echo.
echo =====================================================
echo   重建完成！
echo.
echo   现在请运行：
echo     python src\main.py
echo.
echo   或者直接双击：
echo     start_gmx.bat
echo =====================================================
pause
