@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==========================================
echo   创建 GROMACS-GUI 虚拟环境 (名字: gmx)
echo ==========================================
echo.

if exist gmx\Scripts\activate.bat (
    echo 虚拟环境 gmx 已存在！
    echo 如需重新创建，请先删除 gmx 文件夹。
    pause
    exit /b
)

echo [1/2] 创建虚拟环境 gmx ...
python -m venv gmx

if errorlevel 1 (
    echo 创建失败！请确认 Python 已安装。
    pause
    exit /b
)

echo [2/2] 安装依赖...
call gmx\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ==========================================
echo   虚拟环境 gmx 创建完成！
echo.
echo 下次启动请使用：
echo   .\gmx\Scripts\Activate.ps1
echo   python src\main.py
echo ==========================================
pause
