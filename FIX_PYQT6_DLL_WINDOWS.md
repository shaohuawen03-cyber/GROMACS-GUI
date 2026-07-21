# PyQt6 DLL 加载失败修复指南（Windows + gmx 虚拟环境）

你当前错误：
```
DLL load failed while importing QtCore: 找不到指定的程序。
```

这是 **PyQt6 在 Windows 上最常见的安装问题**，通常是因为缺少 **Microsoft Visual C++ 运行时库**。

---

## 推荐修复步骤（按顺序执行）

### 步骤 1: 安装 Microsoft Visual C++ Redistributable（最重要！）

1. 下载并安装这个（必须是 x64）：
   - **链接**：https://aka.ms/vs/17/release/vc_redist.x64.exe

2. 下载后**双击运行**安装（一直点 Next 即可）。

3. 安装完成后**重启 PowerShell**（很重要）。

---

### 步骤 2: 在 (gmx) 环境中重新安装 PyQt6

激活虚拟环境后执行：

```powershell
cd E:\1AI\GROMACS-GUI

# 确保在 (gmx) 环境
.\gmx\Scripts\Activate.ps1

# 完全卸载再重装
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip -y

# 重新安装
pip install PyQt6
```

---

### 步骤 3: 验证修复

```powershell
# 确认在 (gmx) 环境
python -c "from PyQt6.QtCore import QCoreApplication; print('✅ PyQt6 加载成功！')"

# 再运行测试
python test_gromacs_gui.py
```

---

### 步骤 4: 启动 GUI

```powershell
python src\main.py
```

---

## 如果还是失败，尝试以下备用方法

### 方法 A: 强制重新安装（带缓存清理）

```powershell
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip -y
pip cache purge
pip install --no-cache-dir PyQt6
```

### 方法 B: 安装特定兼容版本（2020.6 GROMACS 用户常用）

```powershell
pip install "PyQt6>=6.5.0,<6.7"
```

### 方法 C: 检查是否用了正确的 Python

```powershell
where python
python -c "import sys; print(sys.executable)"
```

确保输出路径包含 `\gmx\` 文件夹。

---

## 额外：只测试核心功能（绕过 GUI）

如果你想先确认代码逻辑是否正常（不启动界面）：

```powershell
# 在 (gmx) 环境中执行
python -c "
import sys
sys.path.insert(0, 'src')
from core.config import get_gmx_path
from core.runner import GromacsRunner

print('gmx path:', get_gmx_path())
r = GromacsRunner()
ok, out = r.run_command(['-version'])
print('gmx 版本测试成功:', ok)
print('前几行:', out[:300] if out else '无输出')
print('✅ 核心功能正常！')
"
```

---

## 完成后告诉我结果

请按顺序执行 **步骤 1 → 步骤 2 → 步骤 3**，然后把下面命令的输出贴给我：

```powershell
python -c "from PyQt6.QtCore import QCoreApplication; print('PyQt6 OK')"
python test_gromacs_gui.py
```

