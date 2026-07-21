# GROMACS-GUI Windows 安装运行指南

你的环境：gmx 已加入系统环境变量 PATH

## 快速开始（复制粘贴执行）

### 1. 克隆仓库

```powershell
cd E:\1AI
git clone https://github.com/shaohuawen03-cyber/GROMACS-GUI.git
cd GROMACS-GUI
```

### 2. 安装依赖（推荐用虚拟环境）

```powershell
# 创建虚拟环境（可选但推荐）
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 【必须】替换配置文件（原版写死了别人的路径）

**把下面整个代码块复制，覆盖文件：** `src\core\config.py`

```python
import os
import shutil

# =============================================
# GROMACS-GUI 配置 - Windows 友好版
# =============================================
# 优先级：
#   1. 环境变量 GMX_PATH
#   2. 系统 PATH 中的 gmx 或 gmx.exe
#   3. 回退到 "gmx"（你已把 gmx 加入 PATH）
#
# 使用方法：
#   - 把 gmx 加入系统 PATH 后直接可用
#   - 或者临时设置： set GMX_PATH=C:\Gromacs\bin\gmx.exe
# =============================================

GMX_PATH = os.environ.get("GMX_PATH", None)

def get_gmx_path():
    if GMX_PATH:
        return GMX_PATH

    # Windows 优先查找 gmx.exe 和 gmx
    for candidate in ["gmx", "gmx.exe"]:
        found = shutil.which(candidate)
        if found:
            return found

    # 最后回退（你确认 gmx 已在 PATH）
    return "gmx"
```

**保存文件后继续。**

### 4. 验证 gmx 是否可用（非常重要）

```powershell
gmx --version
```

如果能正常显示版本信息，说明没问题。

### 5. 启动程序

```powershell
# 方法一：直接启动（推荐）
python src\main.py

# 方法二：使用批处理脚本
run.bat
```

### 6. （强烈推荐）运行测试验证安装

```powershell
python test_gromacs_gui.py
```

---

## 额外提示

- 如果想用环境变量指定 gmx 路径：
  ```powershell
  $env:GMX_PATH = "C:\your\path\to\gmx.exe"
  python src\main.py
  ```

- 测试 gmx 命令是否真的在 PATH：
  ```powershell
  where gmx
  gmx --version
  ```

- 常见问题：
  - 报错找不到 gmx → 检查 PATH
  - PyQt6 安装失败 → 尝试 `pip install PyQt6 --upgrade`
  - 图形界面卡死 → 确保 Windows 有正常显示驱动

---

完成以上步骤后，程序应该可以正常运行了！

如有问题，把报错信息贴出来。
