#!/usr/bin/env python3
"""
Minimal test for GROMACS only - does NOT import any PyQt6.
Use this to verify gmx works without the GUI dependency problem.
"""
import subprocess
import sys
import os

def test_gmx_direct():
    print("=== 直接测试 gmx (不经过 GUI 模块) ===")
    
    # 尝试找到 gmx
    gmx_candidates = ["gmx", "gmx.exe"]
    
    gmx_path = None
    for cand in gmx_candidates:
        try:
            result = subprocess.run(
                ["where", cand] if os.name == 'nt' else ["which", cand],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                gmx_path = result.stdout.strip().split('\n')[0]
                break
        except:
            pass
    
    if not gmx_path:
        # fallback to PATH
        gmx_path = "gmx"
    
    print(f"尝试使用: {gmx_path}")
    
    try:
        result = subprocess.run(
            [gmx_path, "--version"],
            capture_output=True,
            text=True,
            timeout=15
        )
        print("返回码:", result.returncode)
        if result.stdout:
            print("标准输出 (前 800 字符):")
            print(result.stdout[:800])
        if result.stderr:
            print("标准错误:")
            print(result.stderr[:500])
        
        if result.returncode == 0:
            print("\n✅ gmx 命令直接调用成功！")
            print("核心功能没问题。")
            return True
        else:
            print("\n❌ gmx 返回非零退出码")
            return False
            
    except FileNotFoundError:
        print("❌ 找不到 gmx 命令。请确认 gmx 已在 PATH 中。")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    success = test_gmx_direct()
    sys.exit(0 if success else 1)
