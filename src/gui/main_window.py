from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, 
                             QLabel, QTabWidget, QMessageBox, QListWidget, QStackedWidget, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os
import sys
from datetime import datetime
import traceback

# 导入 GROMACS 运行器
from core.runner import GromacsRunner
from gui.topology_tab import TopologyTab
from gui.em_tab import EMTab
from gui.eq_tab import EQTab
from gui.md_tab import MDTab
from gui.ligand.ligand_simulator import LigandSimulator
from gui.analysis_tab import AnalysisTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GROMACS GUI")
        self.resize(1000, 750)
        
        self.runner = GromacsRunner()
        
        # 主布局: 水平分割 (左侧导航, 右侧内容)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # === 左侧导航栏 ===
        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(200)
        nav_font = QFont()
        nav_font.setPointSize(10)
        self.nav_list.setFont(nav_font)
        
        # 美化左侧导航栏的样式 (深色主题)
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                border: 1px solid #3f3f3f;
                border-radius: 4px;
                outline: none;
                color: #d4d4d4;
            }
            QListWidget::item {
                padding: 12px 10px;
                border-bottom: 1px solid #3f3f3f;
            }
            QListWidget::item:selected {
                background-color: #005a9e;
                color: white;
                border-radius: 2px;
            }
            QListWidget::item:hover:!selected {
                background-color: #3f3f3f;
            }
        """)
        
        self.nav_list.addItem("Solution Simulator")
        self.nav_list.addItem("Ligand Simulator")
        self.nav_list.addItem("Membrane Simulator [WIP]")
        self.nav_list.addItem("Polymer Simulator [WIP]")
        
        self.main_layout.addWidget(self.nav_list)
        
        # === 右侧主体区域 ===
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.main_layout.addWidget(self.right_widget, stretch=1)
        
        # 顶部 StackedWidget 用于切换不同的 Builder
        self.stacked_widget = QStackedWidget()
        self.right_layout.addWidget(self.stacked_widget, stretch=3)
        
        # --- 模块 1: Solution Simulator ---
        self.solution_tabs = QTabWidget()
        self.stacked_widget.addWidget(self.solution_tabs)
        
        # --- 模块 2: Ligand Simulator ---
        self.ligand_simulator = LigandSimulator(self)
        self.stacked_widget.addWidget(self.ligand_simulator)
        
        # --- 模块 3,4: 占位符 (WIP) ---
        self.setup_wip_module("Membrane Simulator 正在开发中...\n\n未来将支持磷脂双分子层插入与定向")
        self.setup_wip_module("Polymer Simulator 正在开发中...\n\n敬请期待！")
        
        # 连接导航点击事件
        self.nav_list.currentRowChanged.connect(self.stacked_widget.setCurrentIndex)
        
        # 初始化 Solution Simulator 的各个功能标签页
        self.init_topology_tab()
        self.init_em_tab()
        self.init_eq_tab()
        self.init_md_tab()
        self.init_analysis_tab()

        # Store references for pipeline
        self.topology_tab = self.solution_tabs.widget(0)
        self.em_tab = self.solution_tabs.widget(1)
        self.eq_tab = self.solution_tabs.widget(2)
        self.md_tab = self.solution_tabs.widget(3)
        
        # 默认选中第一项
        self.nav_list.setCurrentRow(0)
        
        # 底部日志输出窗口 (全局共享)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas;")
        self.right_layout.addWidget(QLabel("全局运行日志:"))
        self.right_layout.addWidget(self.log_output, stretch=1)
        
        # 测试GROMACS按钮 + 日志控制
        btn_layout = QHBoxLayout()

        self.btn_test = QPushButton("测试 GROMACS 环境")
        self.btn_test.clicked.connect(self.test_gmx)
        btn_layout.addWidget(self.btn_test)

        self.btn_clear_log = QPushButton("清空日志")
        self.btn_clear_log.clicked.connect(self.clear_log)
        btn_layout.addWidget(self.btn_clear_log)

        self.btn_test_log = QPushButton("测试日志输出 (直接写)")
        self.btn_test_log.clicked.connect(self.test_log_output)
        btn_layout.addWidget(self.btn_test_log)

        self.right_layout.addLayout(btn_layout)

        # === 新增：一键运行完整流程 + Verbose 开关 ===
        controls_layout = QHBoxLayout()

        self.chk_verbose = QCheckBox("Verbose 模式 (显示详细进度 + 结束时间)")
        self.chk_verbose.setChecked(True)
        controls_layout.addWidget(self.chk_verbose)

        self.btn_run_all = QPushButton("🚀 一键运行完整流程 (Topology → EM → EQ → MD)")
        self.btn_run_all.setStyleSheet("background-color: #006400; color: white; font-weight: bold; padding: 8px;")
        self.btn_run_all.clicked.connect(self.run_full_pipeline)
        controls_layout.addWidget(self.btn_run_all)

        self.right_layout.addLayout(controls_layout)

        # Pipeline state
        self.pipeline_running = False
        self.current_pipeline_step = 0
        self.pipeline_steps = []  # will be populated when starting

    @property
    def verbose(self):
        return self.chk_verbose.isChecked() if hasattr(self, 'chk_verbose') else True

    def setup_wip_module(self, text):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        label.setFont(font)
        layout.addWidget(label)
        self.stacked_widget.addWidget(widget)

    def init_topology_tab(self):
        tab = TopologyTab(self)
        self.solution_tabs.addTab(tab, "1. 拓扑与水箱")
        
    def init_em_tab(self):
        tab = EMTab(self)
        self.solution_tabs.addTab(tab, "2. 能量最小化")
        
    def init_eq_tab(self):
        tab = EQTab(self)
        self.solution_tabs.addTab(tab, "3. 系统平衡")
        
    def init_md_tab(self):
        tab = MDTab(self)
        self.solution_tabs.addTab(tab, "4. 生产模拟")
        
    def init_analysis_tab(self):
        tab = AnalysisTab(self)
        self.solution_tabs.addTab(tab, "5. 分析与可视化")

    def log(self, message):
        """向日志窗口输出信息（带时间戳）"""
        ts = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{ts}] {message}"
        # 同时输出到控制台（Spyder / 终端）——这是最可靠的输出方式
        print(formatted)
        # 写入 GUI
        self.log_output.append(formatted)
        # 强制刷新（Spyder + PyQt 经常需要这些）
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())
        self.log_output.repaint()
        try:
            from PyQt6.QtWidgets import QApplication
            QApplication.processEvents()
        except:
            pass

    def _direct_append(self, text: str):
        """最直接的写入方式，用于极端调试"""
        print(f"[DIRECT] {text}")
        self.log_output.append(text)
        self.log_output.repaint()
        try:
            from PyQt6.QtWidgets import QApplication
            QApplication.processEvents()
        except:
            pass

    def log_step_start(self, step_name: str):
        """长任务开始时打印醒目标记 + 时间"""
        ts = datetime.now().strftime("%H:%M:%S")
        self.log("")
        self.log("┏" + "━" * 68 + "┓")
        self.log(f"┃ ▶️ 开始: {step_name}     @ {ts}")
        self.log("┗" + "━" * 68 + "┛")

    def log_step_complete(self, step_name: str):
        """长任务结束时打印完成时间 + 醒目标记（用户最关心的）"""
        ts = datetime.now().strftime("%H:%M:%S")
        self.log("")
        self.log("┏" + "━" * 68 + "┓")
        self.log(f"┃ ✅✅✅ 完成: {step_name}     @ {ts}")
        self.log("┗" + "━" * 68 + "┛")
        self.log("")

    def log_verbose(self, message: str):
        """只有在 Verbose 模式下才显示的详细日志"""
        if getattr(self, 'verbose', True):
            self.log(f"[V] {message}")

    def test_gmx(self):
        """测试GROMACS是否可用"""
        self.log("\n>>> 正在运行: gmx -version")
        success, output = self.runner.run_command(['-version'])
        self.log(output)
        if success:
            QMessageBox.information(self, "成功", "GROMACS 运行正常！")
        else:
            QMessageBox.critical(self, "错误", "GROMACS 运行失败，请检查路径。")

    def clear_log(self):
        """清空全局日志窗口"""
        self.log_output.clear()
        print("[GUI] 日志窗口已清空")

    def test_log_output(self):
        """直接测试日志输出是否工作（不依赖任何GROMACS命令）"""
        print("[GUI] '测试日志输出' 按钮被点击 - 这是控制台输出")
        self.log("=== 直接测试 #1 ===")
        self.log("=== 直接测试 #2 - 如果你能看到这两行，说明 log() 正在把内容写进 GUI ===")
        self.log("=== 直接测试 #3 - 时间戳应该出现 ===")
        self.log("如果上面三行在 GUI 里完全看不到，请检查：")
        self.log("  1. Spyder 的 'Console' 面板（看 print 输出）")
        self.log("  2. 是否有其他窗口遮挡了日志区域")
        print("[GUI] test_log_output 结束")

    def run_full_pipeline(self):
        """一键运行完整流程（Topology → EM → EQ → MD）"""
        if not self.topology_tab or not self.em_tab or not self.eq_tab or not self.md_tab:
            QMessageBox.warning(self, "错误", "部分标签页未初始化")
            return

        reply = QMessageBox.question(
            self,
            "确认一键运行",
            "这将依次执行：\n1. Topology (pdb2gmx + editconf + solvate)\n2. Energy Minimization\n3. Equilibration (NVT + NPT)\n4. Production MD\n\n确认继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.log("\n" + "="*70)
        self.log("🚀 开始一键完整流程")
        self.log("="*70)

        # 目前简单顺序触发（后续可以做成真正的链式回调）
        # 这里我们直接触发 topology 的主要步骤
        # 实际生产中应该监听 finished_signal 再继续下一步

        try:
            # 步骤1: Topology（只触发 pdb2gmx，其余步骤用户可手动或我们后续扩展）
            if hasattr(self.topology_tab, 'run_pdb2gmx'):
                self.log(">>> [1/4] 开始 Topology (pdb2gmx)")
                self.topology_tab.run_pdb2gmx()
                self.log_step_complete("Topology (pdb2gmx) 已启动")

            # 提示用户
            self.log("\n注意：当前版本会依次启动各阶段。")
            self.log("请观察日志，等待当前阶段完成后手动或等待后续自动衔接。")

            # 简单版本：直接启动 EM（假设 topology 已经手动跑完）
            # 实际建议后面做成真正的 pipeline 状态机

            QMessageBox.information(self, "提示", 
                "一键流程已启动 Topology 阶段。\n"
                "请在日志中等待当前阶段完成。\n\n"
                "完整自动流水线后续版本会进一步优化。")

        except Exception as e:
            self.log(f"❌ 一键流程启动失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"一键流程启动失败:\n{str(e)}")
