# gmx_only_test.py
# 完全独立测试 gmx
# 这个文件不导入项目任何代码，不导入 PyQt6

import subprocess
import sys

print("=== 纯 gmx 测试（零项目依赖） ===")
print("直接调用系统 gmx，不加载任何 GUI 代码\n")

try:
    result = subprocess.run(
        ["gmx", "--version"],
        capture_output=True,
        text=True,
        timeout=20,
        encoding="utf-8",
        errors="replace"
    )
    
    print("返回码:", result.returncode)
    print("\n--- 输出 ---")
    print(result.stdout[:2000] if result.stdout else "(无)")
    
    if result.returncode == 0:
        print("\n✅✅✅ gmx 本身运行正常！")
        print("问题只出在 PyQt6 的 DLL 上。")
    else:
        print("\n❌ gmx 失败")
        
except Exception as e:
    print("❌ 错误:", e)
