# PyQt6 修复 + 启动 GROMACS-GUI（最终步骤）

你已经确认：
✅ gmx 本身完全正常（gmx_pure.py 测试通过）
❌ 问题只在 PyQt6 的 DLL 加载失败

---

## 立即执行修复（在当前 (gmx) 窗口）

### 步骤 1: 安装 Microsoft Visual C++ 运行库（最关键！）

1. 下载这个文件（必须是 **x64**）：
   **https://aka.ms/vs/17/release/vc_redist.x64.exe**

2. 双击运行安装（一直点“下一步”）。

3. 安装完成后，**关闭当前 PowerShell 窗口**。

---

### 步骤 2: 重新打开窗口 + 激活环境 + 重装 PyQt6

重新打开 PowerShell，执行下面全部命令：

```powershell
cd E:\1AI\GROMACS-GUI

# 激活虚拟环境
.\gmx\Scripts\Activate.ps1

# 重新安装 PyQt6（干净重装）
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip -y
pip install PyQt6

# 测试是否修复
python -c "from PyQt6.QtCore import QCoreApplication; print('✅ PyQt6 加载成功！')"
```

---

### 步骤 3: 启动 GROMACS-GUI

如果上面显示 `✅ PyQt6 加载成功！`，执行：

```powershell
python src\main.py
```

或者直接双击项目里的：

**start_gmx.bat**

---

## 如果重装后还是报错

尝试这个更激进的命令：

```powershell
.\gmx\Scripts\Activate.ps1
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip -y
pip cache purge
pip install --no-cache-dir PyQt6
```

然后再测试：
```powershell
python -c "from PyQt6.QtCore import QCoreApplication; print('✅ PyQt6 加载成功！')"
python src\main.py
```

---

## 成功后日常使用

```powershell
cd E:\1AI\GROMACS-GUI
.\gmx\Scripts\Activate.ps1
python src\main.py
```

或直接双击 `start_gmx.bat`

---

请按上面步骤操作，完成后把以下两行命令的输出贴给我：

```powershell
python -c "from PyQt6.QtCore import QCoreApplication; print('✅ PyQt6 加载成功！')"
python src\main.py
```

