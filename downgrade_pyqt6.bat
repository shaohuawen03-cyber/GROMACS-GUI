@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==========================================
echo   降级 PyQt6 到稳定版本 6.6.1
echo ==========================================
echo.

call gmx\Scripts\activate.bat

echo [1/3] 卸载当前 PyQt6...
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip -y

echo.
echo [2/3] 安装稳定版 PyQt6 6.6.1...
pip install "PyQt6==6.6.1" "PyQt6-Qt6==6.6.1"

echo.
echo [3/3] 测试加载...
python -c "from PyQt6.QtCore import QCoreApplication; print('✅ PyQt6 6.6.1 加载成功！')"

echo.
echo ==========================================
echo   完成！如果上面显示 ✅，请运行：
echo   python src\main.py
echo ==========================================
pause
