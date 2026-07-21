#!/usr/bin/env python3
"""
100% 独立的 gmx 测试脚本
这个脚本**不使用项目里的任何代码**，也不导入 PyQt6
直接用 subprocess 调用你系统里的 gmx
"""
import subprocess
import sys

print("=" * 70)
print("GROMACS 独立测试（完全不加载项目代码 / PyQt6）")
print("=" * 70)

gmx = "gmx"

print(f"\n正在执行: {gmx} --version\n")
print("-" * 70)

try:
    result = subprocess.run(
        [gmx, "--version"],
        capture_output=True,
        text=True,
        timeout=20,
        encoding="utf-8",
        errors="replace"
    )
    
    print(f"返回码: {result.returncode}")
    
    if result.stdout:
        print("\n【gmx 输出】")
        print(result.stdout[:1500])
    
    if result.stderr:
        print("\n【错误输出】")
        print(result.stderr[:800])
    
    print("-" * 70)
    
    if result.returncode == 0:
        print("\n✅✅✅  gmx 可以正常运行！")
        print("你的 GROMACS 本身没问题。")
        print("问题只出在 PyQt6 的系统 DLL 上。\n")
        sys.exit(0)
    else:
        print("\n❌ gmx 命令执行失败")
        sys.exit(1)

except FileNotFoundError:
    print("❌ 找不到 gmx 命令")
    print("请确认 gmx 已经加到系统环境变量 PATH 里")
    sys.exit(1)
except Exception as e:
    print(f"❌ 发生错误: {e}")
    sys.exit(1)
