@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==========================================
echo   PyQt6 DLL 修复脚本 (针对 gmx 环境)
echo ==========================================
echo.

echo [1/3] 激活 gmx 虚拟环境...
call gmx\Scripts\activate.bat

echo.
echo [2/3] 重新安装 PyQt6...
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip -y
pip install --upgrade PyQt6

echo.
echo [3/3] 测试 PyQt6 是否正常...
python -c "from PyQt6.QtCore import QCoreApplication; print('✅ PyQt6 加载成功！')"

echo.
echo 修复完成！现在可以尝试运行：
echo   python src\main.py
echo.
pause
