@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==========================================
echo   完全重建 GROMACS-GUI 虚拟环境 (gmx)
echo ==========================================
echo.

echo [1/5] 删除旧的 gmx 虚拟环境...
if exist gmx rmdir /s /q gmx

echo [2/5] 创建新虚拟环境...
python -m venv gmx

call gmx\Scripts\activate.bat
python -m pip install --upgrade pip

echo [3/5] 安装稳定版 PyQt6 (6.6.1) + 依赖...
pip install "PyQt6==6.6.1" "PyQt6-Qt6==6.6.1" matplotlib numpy

echo [4/5] 测试 PyQt6...
python -c "from PyQt6.QtCore import QCoreApplication; print('✅ PyQt6 6.6.1 加载成功！')"

echo [5/5] 完成！
echo.
echo 现在可以运行: python src\main.py
echo 或双击 start_gmx.bat
pause
