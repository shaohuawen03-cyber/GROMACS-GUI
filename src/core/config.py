import os
import shutil
import subprocess

# ============================================================
# 最终强力修复版 - 专门解决你的 "No force fields found" 问题
# ============================================================

def get_gmx_path():
    """
    强制返回正确的 gmx.exe
    优先级：
      1. E:\gmx2020.6_GPU\bin\gmx.exe （你真正的可执行文件）
      2. 其他已知好路径
      3. where 找到的干净 gmx.exe
    """
    # 最高优先：你真实的安装路径
    for p in [
        r"E:\gmx2020.6_GPU\bin\gmx.exe",
        r"E:\gmx2020.6_GPU\bin\gmx.EXE",
        r"C:\gmx2020.6_GPU\bin\gmx.exe",
    ]:
        if os.path.isfile(p):
            return os.path.abspath(p)

    # 环境变量
    env = os.environ.get("GMX_PATH")
    if env and os.path.isfile(env):
        bn = os.path.basename(env).lower()
        if "gmx" in bn and not bn.endswith(".exe.exe"):
            return os.path.abspath(env)

    # where 命令（过滤坏 launcher）
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
    """强制设置 GMXDATA，让 GROMACS 能找到力场"""
    if gmx_path is None:
        gmx_path = get_gmx_path()

    if not gmx_path or gmx_path == "gmx":
        return

    # 根据真实 gmx.exe 位置推断数据目录
    exe_dir = os.path.dirname(os.path.abspath(gmx_path))

    candidates = [
        os.path.abspath(os.path.join(exe_dir, "..")),                      # bin 的上一级
        os.path.abspath(os.path.join(exe_dir, "..", "share", "gromacs")),
        r"E:\gmx2020.6_GPU",
        r"C:\gmx2020.6_GPU",
    ]

    for root in candidates:
        top = os.path.join(root, "share", "gromacs", "top")
        if os.path.isdir(top):
            try:
                if any(d.endswith(".ff") for d in os.listdir(top)):
                    os.environ["GMXDATA"] = root
                    os.environ["GMXLIB"] = top
                    return
            except:
                pass

    # 硬编码兜底（最有效）
    for guess in [r"E:\gmx2020.6_GPU", r"C:\gmx2020.6_GPU"]:
        top = os.path.join(guess, "share", "gromacs", "top")
        if os.path.isdir(top):
            os.environ["GMXDATA"] = guess
            os.environ["GMXLIB"] = top
            return
