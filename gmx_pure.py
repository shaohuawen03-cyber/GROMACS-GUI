import subprocess
print("="*70)
print("纯净 gmx 测试（完全不使用项目代码，不加载 PyQt6）")
print("="*70)
r = subprocess.run(["gmx", "--version"], capture_output=True, text=True, timeout=15, encoding="utf-8", errors="replace")
print("\n返回码:", r.returncode)
print("\n--- gmx 输出 ---")
print((r.stdout or r.stderr)[:2200])
if r.returncode == 0:
    print("\n✅✅✅ gmx 本身运行完全正常！")
    print("问题只出在 PyQt6 的 DLL 加载上。")
