#!/usr/bin/env python3
"""
100% 独立测试 gmx 命令
这个脚本**不导入项目任何代码**，不依赖 PyQt6
直接用 subprocess 调用 gmx --version
"""
import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("纯净 gmx 测试（完全不使用项目代码 / PyQt6）")
    print("=" * 60)
    
    gmx_cmd = "gmx"
    
    print(f"\n尝试执行: {gmx_cmd} --version")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            [gmx_cmd, "--version"],
            capture_output=True,
            text=True,
            timeout=20,
            encoding='utf-8',
            errors='replace'
        )
        
        print(f"返回码: {result.returncode}")
        
        if result.stdout:
            print("\n【标准输出】")
            print(result.stdout[:1200])
        
        if result.stderr:
            print("\n【标准错误】")
            print(result.stderr[:600])
        
        if result.returncode == 0:
            print("\n" + "=" * 60)
            print("✅ gmx 命令可以正常运行！")
            print("你的 GROMACS 本身没问题。")
            print("=" * 60)
            return True
        else:
            print("\n❌ gmx 返回了错误")
            return False
            
    except FileNotFoundError:
        print("❌ 错误：找不到 'gmx' 命令")
        print("请确认 gmx 已经加入系统 PATH")
        return False
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
