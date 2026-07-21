import os
import shutil
import subprocess

# ============================================================
# 最终强力版 - 专门为你的 GROMACS 安装优化
# ============================================================
# 你的真实路径：
#   可执行文件: E:\gmx2020.6_GPU\bin\gmx.exe
#   数据目录:   E:\gmx2020.6_GPU\share\gromacs\top
#
# 这个版本会：
#   1. 强制使用正确的 gmx.exe
#   2. 强制设置 GMXDATA / GMXLIB
# ============================================================

def get_gmx_path():
    """强制返回正确的 gmx.exe"""
    
    # 最高优先级：你真实的安装路径
    for p in [
        r"E:\gmx2020.6_GPU\bin\gmx.exe",
        r"E:\gmx2020.6_GPU\bin\gmx.EXE",
    ]:
        if os.path.isfile(p):
            return os.path.abspath(p)

    # 环境变量
    env = os.environ.get("GMX_PATH")
    if env and os.path.isfile(env):
        bn = os.path.basename(env).lower()
        if "gmx" in bn and not bn.endswith(".exe.exe"):
            return os.path.abspath(env)

    # where 命令找干净的
    for name in ["gmx.exe", "gmx"]:
        try:
            res = subprocess.run(["where", name], capture_output=True, text=True, timeout=4, shell=True)
            if res.returncode == 0:
                for line in res.stdout.strip().splitlines():
                    p = line.strip()
                    if p and os.path.isfile(p):
                        bn = os.path.basename(p).lower()
                        if "gmx" in bn and not bn.endswith(".exe.exe"):
                            return os.path.abspath(p)
        except:
            pass

    # 兜底
    for name in ["gmx.exe", "gmx"]:
        p = shutil.which(name)
        if p and os.path.isfile(p):
            bn = os.path.basename(p).lower()
            if "gmx" in bn and not bn.endswith(".exe.exe"):
                return os.path.abspath(p)

    return "gmx"

def setup_gmx_environment(gmx_path: str = None):
    """强制设置数据目录，让 pdb2gmx 能找到力场"""
    if gmx_path is None:
        gmx_path = get_gmx_path()

    if not gmx_path or gmx_path == "gmx":
        return

    # 直接硬编码你正确的安装路径（最可靠）
    correct_root = r"E:\gmx2020.6_GPU"
    top_dir = os.path.join(correct_root, "share", "gromacs", "top")

    if os.path.isdir(top_dir):
        os.environ["GMXDATA"] = correct_root
        os.environ["GMXLIB"] = top_dir
        return

    # 动态推断（备用）
    try:
        exe_dir = os.path.dirname(os.path.abspath(gmx_path))
        for root in [
            os.path.abspath(os.path.join(exe_dir, "..")),
            r"E:\gmx2020.6_GPU",
            r"C:\gmx2020.6_GPU",
        ]:
            top = os.path.join(root, "share", "gromacs", "top")
            if os.path.isdir(top):
                os.environ["GMXDATA"] = root
                os.environ["GMXLIB"] = top
                return
    except:
        pass
