# GROMACS-GUI Windows 完整运行指南（虚拟环境名：gmx）

**前提**：
- 你已经在 `arena/019f84dc-gromacs-gui` 分支
- gmx 已经在系统 PATH 中
- 当前目录是 E:\1AI\GROMACS-GUI

---

## 从头开始完整步骤（复制粘贴执行）

### 步骤 1: 创建并激活虚拟环境（名字固定为 gmx）

在 PowerShell 中执行：

```powershell
# 确保在正确目录
cd E:\1AI\GROMACS-GUI

# 创建虚拟环境，名字叫 gmx
python -m venv gmx

# 激活虚拟环境
.\gmx\Scripts\Activate.ps1
```

激活后，命令行前面应该出现 `(gmx)` 前缀。

---

### 步骤 2: 在虚拟环境中安装依赖

激活 gmx 环境后执行：

```powershell
# 升级 pip（可选但推荐）
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

---

### 步骤 3: 验证 gmx 是否可用（非常重要）

```powershell
gmx --version
```

应该能看到 GROMACS 版本信息。如果报错，请先修复 gmx 的 PATH。

---

### 步骤 4: 验证安装（推荐先跑测试）

```powershell
python test_gromacs_gui.py
```

如果看到很多 ✅ ，说明安装成功。

---

### 步骤 5: 启动 GROMACS-GUI

```powershell
python src\main.py
```

---

## 日常使用流程（以后每次打开）

```powershell
cd E:\1AI\GROMACS-GUI

# 激活虚拟环境
.\gmx\Scripts\Activate.ps1

# 启动程序
python src\main.py
```

---

## 额外说明

- 虚拟环境位置：`E:\1AI\GROMACS-GUI\gmx`
- 以后安装新包都要在激活 `(gmx)` 环境下用 `pip install`
- 如果想退出虚拟环境：`deactivate`
- 如果 `Activate.ps1` 报错执行策略问题，运行一次：
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

---

现在直接从 **步骤 1** 开始执行即可。
