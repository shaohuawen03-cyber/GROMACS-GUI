# GROMACS-GUI 运行指南（虚拟环境名称固定为 gmx）

**当前状态**：你已经在 `arena/019f84dc-gromacs-gui` 分支

---

## 完整从头开始步骤（PowerShell 复制执行）

### 第 1 步：创建虚拟环境（名字必须是 gmx）

```powershell
cd E:\1AI\GROMACS-GUI

# 创建名为 gmx 的虚拟环境
python -m venv gmx
```

### 第 2 步：激活虚拟环境

```powershell
# 激活 gmx 虚拟环境
.\gmx\Scripts\Activate.ps1
```

激活成功后，命令行前面会出现 `(gmx)` 前缀。

> 如果报错执行策略，运行下面这行后再试：
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 第 3 步：在 gmx 环境中安装依赖

```powershell
# 升级 pip（推荐）
python -m pip install --upgrade pip

# 安装项目所需包
pip install -r requirements.txt
```

### 第 4 步：验证 gmx 命令可用

```powershell
gmx --version
```

必须能正常显示 GROMACS 版本，否则 GUI 无法使用 gmx。

### 第 5 步：测试安装是否成功（强烈推荐）

```powershell
python test_gromacs_gui.py
```

看到大量 ✅ 就说明没问题。

### 第 6 步：启动 GROMACS-GUI

```powershell
python src\main.py
```

---

## 以后每次使用（日常流程）

```powershell
cd E:\1AI\GROMACS-GUI

# 1. 激活虚拟环境
.\gmx\Scripts\Activate.ps1

# 2. 启动程序
python src\main.py
```

---

## 辅助批处理文件（可选，双击更方便）

项目中已提供以下文件：

- `CREATE_GMX_VENV.bat` → 第一次创建虚拟环境 + 安装依赖
- `start_gmx.bat` → 以后直接双击启动

---

## 常见问题

**Q: 提示 No module named 'PyQt6'**  
A: 你没有在 `(gmx)` 虚拟环境中运行。必须先激活虚拟环境。

**Q: Activate.ps1 报错**  
A: 以管理员身份运行 PowerShell，执行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Q: gmx 命令找不到**  
A: 确认你的 GROMACS 安装目录已经加入系统环境变量 PATH。

**退出虚拟环境**：
```powershell
deactivate
```

---

现在请**严格按照上面第 1~6 步**执行。
