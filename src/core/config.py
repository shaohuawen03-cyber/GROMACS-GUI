import os
import shutil
import subprocess

# =============================================
# GROMACS-GUI 配置 - Windows 友好版 (修复版)
# =============================================
# 主要改进：
# - 避免捡到 gmx.EXE / gmx.EXE.exe 这类坏的 launcher
# - 优先返回**真实 gmx.exe** 的完整路径
# - 自动探测用户常见的安装位置（尤其是 E:\gmx2020.6_GPU）
# - 尽量让 GROMACS 能找到 forcefield 数据
# =============================================

def _is_real_gmx_exe(path: str) -> bool:
    """判断是否是一个看起来正常的真实 gmx.exe"""
    if not path or not os.path.isfile(path):
        return False
    name = os.path.basename(path).lower()
    # 排除各种奇怪的包装器
    if ".exe.exe" in name or name == "gmx.exe.exe":
        return False
    if not name.startswith("gmx"):
        return False
    # 优先要 .exe 结尾的真实可执行文件
    if name.endswith(".exe") and "gmx" in name:
        return True
    return False

def _find_real_gmx():
    """智能寻找真正的 gmx 可执行文件"""
    
    # 1. 用户手动设置的环境变量（最高优先级）
    env_path = os.environ.get("GMX_PATH")
    if env_path and _is_real_gmx_exe(env_path):
        return os.path.abspath(env_path)

    # 2. 用户常见的真实安装位置（根据错误日志推断）
    known_good_paths = [
        r"E:\gmx2020.6_GPU\bin\gmx.exe",
        r"E:\gmx2020.6_GPU\bin\gmx.EXE",      # 有些安装是这个名字
        r"C:\gmx2020.6_GPU\bin\gmx.exe",
        r"E:\gmx2020.6_GPU\bin\gmx",
        r"C:\Program Files\GROMACS\bin\gmx.exe",
        r"C:\GROMACS\bin\gmx.exe",
    ]
    
    for p in known_good_paths:
        if _is_real_gmx_exe(p):
            return os.path.abspath(p)

    # 3. 使用 where 命令找（Windows 最可靠的方式）
    for name in ["gmx.exe", "gmx"]:
        try:
            result = subprocess.run(
                ["where", name],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            if result.returncode == 0:
                for line in result.stdout.strip().splitlines():
                    candidate = line.strip()
                    if _is_real_gmx_exe(candidate):
                        return os.path.abspath(candidate)
        except:
            pass

    # 4. shutil.which 兜底
    for name in ["gmx.exe", "gmx"]:
        found = shutil.which(name)
        if _is_real_gmx_exe(found):
            return os.path.abspath(found)

    # 5. 最后实在不行才返回 "gmx"（依赖 PATH）
    return "gmx"

def get_gmx_path():
    """返回最合适的 gmx 可执行文件路径"""
    path = _find_real_gmx()
    return path

# 可选：让程序尝试设置 GMXDATA（帮助找到力场）
def setup_gmx_environment(gmx_path: str):
    """尝试设置 GROMACS 需要的环境变量"""
    if not gmx_path or gmx_path == "gmx":
        return
    
    try:
        bin_dir = os.path.dirname(os.path.abspath(gmx_path))
        # 常见的数据目录位置
        possible_data = [
            os.path.abspath(os.path.join(bin_dir, "..", "share", "gromacs")),
            os.path.abspath(os.path.join(bin_dir, "..")),
            "E:\\gmx2020.6_GPU",
            "C:\\gmx2020.6_GPU",
        ]
        
        for data_root in possible_data:
            top_dir = os.path.join(data_root, "share", "gromacs", "top")
            if os.path.isdir(top_dir):
                os.environ["GMXDATA"] = os.path.abspath(data_root)
                os.environ["GMXLIB"] = top_dir
                break
    except:
        pass