import os
import shutil
import subprocess

# =============================================
# GROMACS-GUI 配置 - Windows 专用修复版
# =============================================
# 针对用户错误日志专门优化：
# - 强制优先使用 E:\gmx2020.6_GPU\bin\gmx.exe （真实可执行文件）
# - 自动设置 GMXDATA / GMXLIB 让 GROMACS 能找到 forcefield
# - 避免捡到 gmx.EXE.exe / gmx.EXE 这类坏 launcher
# =============================================

def get_gmx_path():
    """
    返回一个能正常工作的 gmx 路径。
    优先级：
      1. 用户环境变量 GMX_PATH
      2. 用户真实安装路径 E:\gmx2020.6_GPU\bin\gmx.exe
      3. 其他常见位置
      4. where / shutil 找到的干净 gmx.exe
    """
    # 1. 环境变量最高优先
    env = os.environ.get("GMX_PATH")
    if env and os.path.isfile(env) and "gmx" in os.path.basename(env).lower():
        # 排除明显坏的 launcher
        if not os.path.basename(env).lower().endswith(".exe.exe"):
            return os.path.abspath(env)

    # 2. 用户实际安装位置（根据错误日志）
    preferred = [
        r"E:\gmx2020.6_GPU\bin\gmx.exe",
        r"E:\gmx2020.6_GPU\bin\gmx.EXE",   # 有些安装是这个
        r"C:\gmx2020.6_GPU\bin\gmx.exe",
    ]
    for p in preferred:
        if os.path.isfile(p):
            return os.path.abspath(p)

    # 3. 用 where 命令找（优先完整路径）
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

    # 4. shutil 兜底
    for name in ["gmx.exe", "gmx"]:
        p = shutil.which(name)
        if p and os.path.isfile(p):
            bn = os.path.basename(p).lower()
            if "gmx" in bn and not bn.endswith(".exe.exe"):
                return os.path.abspath(p)

    # 最后回退（依赖 PATH）
    return "gmx"

def setup_gmx_environment(gmx_path: str = None):
    """
    根据 gmx.exe 的实际位置，设置 GMXDATA / GMXLIB
    这样 pdb2gmx 才能找到 forcefield.itp
    """
    if gmx_path is None:
        gmx_path = get_gmx_path()

    if not gmx_path or gmx_path == "gmx":
        return

    try:
        exe_dir = os.path.dirname(os.path.abspath(gmx_path))

        # 常见布局：
        # bin/gmx.exe  →  share/gromacs/top
        candidates = [
            os.path.abspath(os.path.join(exe_dir, "..", "share", "gromacs")),
            os.path.abspath(os.path.join(exe_dir, "..")),
            r"E:\gmx2020.6_GPU",
            r"C:\gmx2020.6_GPU",
        ]

        for root in candidates:
            top_dir = os.path.join(root, "share", "gromacs", "top")
            if os.path.isdir(top_dir):
                # 确认里面有 .ff 目录
                try:
                    if any(d.endswith(".ff") for d in os.listdir(top_dir)):
                        os.environ["GMXDATA"] = root
                        os.environ["GMXLIB"] = top_dir
                        return
                except:
                    pass

        # 兜底：直接硬编码用户常见位置
        for guess in [r"E:\gmx2020.6_GPU", r"C:\gmx2020.6_GPU"]:
            top = os.path.join(guess, "share", "gromacs", "top")
            if os.path.isdir(top):
                os.environ["GMXDATA"] = guess
                os.environ["GMXLIB"] = top
                return
    except:
        pass