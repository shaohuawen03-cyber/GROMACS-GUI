import os
import shutil
import subprocess

# ============================================================
# 强力修复版 GROMACS 路径检测
# 专门解决 "No force fields found" 问题
# ============================================================

def get_gmx_path():
    """
    强制返回正确的 gmx 可执行文件。
    优先使用用户真实的安装路径 E:\gmx2020.6_GPU\bin\gmx.exe
    这样才能正确找到 forcefield 数据。
    """
    # 1. 用户明确设置的环境变量
    env = os.environ.get("GMX_PATH")
    if env and os.path.isfile(env):
        bn = os.path.basename(env).lower()
        if "gmx" in bn and not bn.endswith(".exe.exe"):
            return os.path.abspath(env)

    # 2. 硬编码用户真实安装路径（根据错误日志，这是正确的）
    #    优先使用干净的 gmx.exe
    real_paths = [
        r"E:\gmx2020.6_GPU\bin\gmx.exe",      # 最推荐
        r"E:\gmx2020.6_GPU\bin\gmx.EXE",
        r"C:\gmx2020.6_GPU\bin\gmx.exe",
    ]
    for p in real_paths:
        if os.path.isfile(p):
            return os.path.abspath(p)

    # 3. 用 where 命令找，严格过滤坏的 launcher
    for name in ["gmx.exe", "gmx"]:
        try:
            result = subprocess.run(
                ["where", name],
                capture_output=True, text=True, timeout=5, shell=True
            )
            if result.returncode == 0:
                for line in result.stdout.strip().splitlines():
                    p = line.strip()
                    if p and os.path.isfile(p):
                        bn = os.path.basename(p).lower()
                        if "gmx" in bn and not bn.endswith(".exe.exe"):
                            return os.path.abspath(p)
        except:
            pass

    # 4. shutil.which 兜底
    for name in ["gmx.exe", "gmx"]:
        p = shutil.which(name)
        if p and os.path.isfile(p):
            bn = os.path.basename(p).lower()
            if "gmx" in bn and not bn.endswith(".exe.exe"):
                return os.path.abspath(p)

    # 5. 最后回退
    return "gmx"

def setup_gmx_environment(gmx_path: str = None):
    """
    根据 gmx.exe 的真实位置，设置 GMXDATA / GMXLIB
    让 pdb2gmx 能找到 amber03.ff / oplsaa.ff 等力场
    """
    if gmx_path is None:
        gmx_path = get_gmx_path()

    if not gmx_path or gmx_path == "gmx":
        return

    try:
        exe_dir = os.path.dirname(os.path.abspath(gmx_path))

        # 典型安装结构：
        # E:\gmx2020.6_GPU\bin\gmx.exe
        # E:\gmx2020.6_GPU\share\gromacs\top\oplsaa.ff\forcefield.itp
        candidates = [
            os.path.abspath(os.path.join(exe_dir, "..")),                    # bin 的上一级
            os.path.abspath(os.path.join(exe_dir, "..", "share", "gromacs")),
            r"E:\gmx2020.6_GPU",
            r"C:\gmx2020.6_GPU",
        ]

        for root in candidates:
            top_dir = os.path.join(root, "share", "gromacs", "top")
            if os.path.isdir(top_dir):
                # 确认里面真的有 .ff 目录
                try:
                    if any(d.endswith(".ff") for d in os.listdir(top_dir)):
                        os.environ["GMXDATA"] = root
                        os.environ["GMXLIB"] = top_dir
                        return
                except:
                    pass

        # 最后硬编码兜底（用户常见位置）
        for guess in [r"E:\gmx2020.6_GPU", r"C:\gmx2020.6_GPU"]:
            top = os.path.join(guess, "share", "gromacs", "top")
            if os.path.isdir(top):
                os.environ["GMXDATA"] = guess
                os.environ["GMXLIB"] = top
                return
    except:
        pass
