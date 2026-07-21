# ============================================================
# 纯净 gmx 测试（零依赖）
# 这个文件可以直接运行，不导入项目任何代码
# 不管 PyQt6 能不能加载，都能测试 gmx
# ============================================================

import subprocess
import sys

print("=" * 65)
print("纯净测试 gmx（不加载 runner.py / worker.py / PyQt6）")
print("=" * 65)

gmx = "gmx"

print(f"\n执行命令: {gmx} --version\n")

try:
    result = subprocess.run(
        [gmx, "--version"],
        capture_output=True,
        text=True,
        timeout=15,
        encoding="utf-8",
        errors="replace"
    )
    
    print(f"返回码: {result.returncode}")
    print("\n--- 输出内容 ---")
    output = result.stdout or result.stderr or "(无输出)"
    print(output[:1500])
    
    if result.returncode == 0:
        print("\n" + "=" * 65)
        print("✅✅✅  gmx 可以正常运行！")
        print("你的 GROMACS 本身没问题。")
        print("GUI 启动失败只因为 PyQt6 缺少系统 DLL。")
        print("=" * 65)
    else:
        print("\n❌ gmx 返回非零退出码")
        
except Exception as e:
    print(f"\n❌ 执行出错: {e}")

input("\n按回车键退出...")
