# gmx_test_only.py
# 这个文件**完全独立**，不依赖项目代码，也不导入 PyQt6
# 直接测试你的 gmx 是否能运行

import subprocess
import sys

print("=== 纯净 gmx 测试（不加载任何项目代码） ===")

try:
    result = subprocess.run(
        ["gmx", "--version"],
        capture_output=True,
        text=True,
        timeout=15
    )
    print("返回码:", result.returncode)
    print("\n--- gmx 输出 ---")
    print(result.stdout[:1500] if result.stdout else "(无输出)")
    
    if result.returncode == 0:
        print("\n✅✅✅ gmx 命令可以正常执行！")
        print("你的 GROMACS 本身没问题。")
        print("问题只在 PyQt6 的 DLL 加载上。")
    else:
        print("\n❌ gmx 执行失败")
        
except Exception as e:
    print("❌ 执行失败:", e)
