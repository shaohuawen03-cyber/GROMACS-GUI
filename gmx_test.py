# ============================================================
# gmx_test.py  ——  纯净测试（零项目依赖）
# 直接在 (gmx) 环境里运行：
#   python gmx_test.py
# ============================================================

import subprocess

print("=== 纯净 gmx 测试（不加载任何项目代码） ===\n")

result = subprocess.run(
    ["gmx", "--version"],
    capture_output=True,
    text=True,
    timeout=20,
    encoding="utf-8",
    errors="replace"
)

print(result.stdout)
if result.stderr:
    print("stderr:", result.stderr)

print(f"\n返回码: {result.returncode}")
print("✅ 如果上面显示了 GROMACS 版本，就证明 gmx 本身没问题。")
