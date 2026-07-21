# gmx_pure_test.py
# 完全独立的测试脚本
# 不导入项目任何文件，不导入 PyQt6
# 直接用 subprocess 调用 gmx

import subprocess
import sys

print("=" * 60)
print("纯净 gmx 测试（零依赖）")
print("=" * 60)

try:
    result = subprocess.run(
        ["gmx", "--version"],
        capture_output=True,
        text=True,
        timeout=15,
        encoding="utf-8",
        errors="replace"
    )
    
    print("\n返回码:", result.returncode)
    print("\n--- gmx 输出 ---\n")
    print(result.stdout[:2000] if result.stdout else "(无标准输出)")
    
    if result.returncode == 0:
        print("\n✅✅✅ gmx 命令可以正常运行！")
        print("你的 GROMACS 本身没问题。")
        print("问题只出在 PyQt6 的系统 DLL 加载失败。")
    else:
        print("\n❌ gmx 执行失败")
        
except Exception as e:
    print(f"\n❌ 错误: {e}")
