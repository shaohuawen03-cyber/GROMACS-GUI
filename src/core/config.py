import os
import shutil

# =============================================
# GROMACS-GUI 配置 - Windows 友好版
# =============================================
# 优先级：
#   1. 环境变量 GMX_PATH
#   2. 系统 PATH 中的 gmx 或 gmx.exe
#   3. 回退到 "gmx"（你已把 gmx 加入 PATH）
#
# 使用方法：
#   - 把 gmx 加入系统 PATH 后直接可用
#   - 或者临时设置： set GMX_PATH=C:\Gromacs\bin\gmx.exe
# =============================================

GMX_PATH = os.environ.get("GMX_PATH", None)

def get_gmx_path():
    if GMX_PATH:
        return GMX_PATH

    # Windows 优先查找 gmx.exe 和 gmx
    for candidate in ["gmx", "gmx.exe"]:
        found = shutil.which(candidate)
        if found:
            return found

    # 最后回退（你确认 gmx 已在 PATH）
    return "gmx"
