from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QPlainTextEdit, 
                             QLabel, QTabWidget, QMessageBox, QListWidget, QStackedWidget, QCheckBox)
from PyQt6.QtCore import Qt, QTimer
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
        
        # 底部日志输出窗口 (全局共享) —— 使用 QPlainTextEdit 性能更好 + 限制历史
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas; font-size: 12px;")
        self.log_output.setMaximumBlockCount(8000)   # 防止日志无限增长导致卡死
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

        # === Verbose + 手动测试确认（用户要求：测试完后才能一键） ===
        self.chk_verbose = QCheckBox("Verbose 模式 (显示详细进度 + 结束时间)")
        self.chk_verbose.setChecked(True)
        self.right_layout.addWidget(self.chk_verbose)

        # 手动测试确认区（非常醒目）
        manual_layout = QHBoxLayout()

        self.chk_manual_test_passed = QCheckBox("✅ 我已手动测试通过 pdb2gmx（溶液或复合物）")
        self.chk_manual_test_passed.setChecked(False)
        self.chk_manual_test_passed.setStyleSheet("font-weight: bold; color: #006400; font-size: 13px;")
        self.chk_manual_test_passed.stateChanged.connect(self._update_run_all_button)
        manual_layout.addWidget(self.chk_manual_test_passed)

        btn_mark_tested = QPushButton("我已手动测试成功 → 勾选")
        btn_mark_tested.setStyleSheet("background-color: #228B22; color: white; font-weight: bold; padding: 4px 10px;")
        btn_mark_tested.clicked.connect(lambda: self.chk_manual_test_passed.setChecked(True))
        manual_layout.addWidget(btn_mark_tested)

        self.right_layout.addLayout(manual_layout)

        # 一键按钮
        self.btn_run_all = QPushButton("🚀 一键运行完整流程 (Topology → EM → EQ → MD)")
        self.btn_run_all.setStyleSheet("background-color: #555; color: #ccc; padding: 10px; font-weight: bold;")
        self.btn_run_all.clicked.connect(self.run_full_pipeline)
        self.right_layout.addWidget(self.btn_run_all)

        tip = QLabel("使用方法：1. 手动跑通 pdb2gmx（看控制台 [GMX] 输出）  2. 点击「我已手动测试成功」  3. 再点一键流程")
        tip.setStyleSheet("color: #666; font-size: 11px;")
        self.right_layout.addWidget(tip)

        self._update_run_all_button()

    def _update_run_all_button(self):
        """动态更新一键按钮样式和文字"""
        try:
            if hasattr(self, 'btn_run_all') and hasattr(self, 'chk_manual_test_passed'):
                checked = self.chk_manual_test_passed.isChecked()
                if checked:
                    self.btn_run_all.setStyleSheet("background-color: #006400; color: white; font-weight: bold; padding: 8px;")
                    self.btn_run_all.setText("🚀 一键运行完整流程 (已确认手动测试通过)")
                else:
                    self.btn_run_all.setStyleSheet("background-color: #555; color: #ccc; font-weight: normal; padding: 8px;")
                    self.btn_run_all.setText("🚀 一键运行完整流程 (请先勾选手动测试通过)")
        except Exception:
            pass

        # Pipeline state
        self.pipeline_running = False
        self.current_pipeline_step = 0
        self.pipeline_steps = []  # will be populated when starting

        # === 异步日志缓冲（防止高频输出导致 GUI 卡死）===
        self._log_buffer = []
        self._log_timer = QTimer(self)
        self._log_timer.timeout.connect(self._flush_log_buffer)
        self._log_timer.start(1200)   # 每 1.2 秒批量刷新一次 GUI（非常保守）

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
        # 控制台永远实时打印（最可靠的输出）
        print(formatted)
        # 放入缓冲，定时批量写入 GUI（防止高频输出卡死）
        self._log_buffer.append(formatted)

    def _flush_log_buffer(self):
        if not self._log_buffer:
            return
        try:
            # 一次性大块写入
            text_to_add = "\n".join(self._log_buffer) + "\n"
            self.log_output.moveCursor(self.log_output.textCursor().End)
            self.log_output.insertPlainText(text_to_add)
            self.log_output.moveCursor(self.log_output.textCursor().End)
        except Exception:
            pass
        self._log_buffer.clear()

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
        """一键运行完整流程（仅在用户确认手动测试通过后才推荐使用）"""
        if not self.topology_tab or not self.em_tab or not self.eq_tab or not self.md_tab:
            QMessageBox.warning(self, "错误", "部分标签页未初始化")
            return

        # 新增保护：必须勾选“已手动测试通过”
        if not getattr(self, 'chk_manual_test_passed', None) or not self.chk_manual_test_passed.isChecked():
            QMessageBox.warning(
                self,
                "请先手动测试",
                "强烈建议：\n"
                "1. 先手动跑通 pdb2gmx（溶液或复合物）\n"
                "2. 确认生成 processed.gro / topol.top\n"
                "3. 勾选上方「已手动测试通过」复选框\n\n"
                "再点击一键流程。\n\n"
                "当前版本的一键流程主要是方便后续阶段，完整自动链式仍在完善中。"
            )
            return

        reply = QMessageBox.question(
            self,
            "确认一键运行完整流程",
            "这将尝试启动 Topology 阶段。\n"
            "后续 EM / EQ / MD 需要你观察日志后手动或等待后续自动衔接。\n\n"
            "确认继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.log("\n" + "="*70)
        self.log("🚀 开始一键完整流程（用户已确认手动测试通过）")
        self.log("="*70)

        try:
            # 目前主要触发 solution 的 pdb2gmx（复合物用户可手动在 Ligand Simulator 里跑）
            if hasattr(self.topology_tab, 'run_pdb2gmx'):
                self.log(">>> [1/4] 启动 Topology (pdb2gmx) ...")
                self.topology_tab.run_pdb2gmx()

            self.log("\n注意：")
            self.log("• 控制台会显示大量 [GMX] 输出（正常）")
            self.log("• GUI 日志在重度阶段会比较安静（我们故意设计的，防止卡死）")
            self.log("• pdb2gmx 成功后请手动继续 editconf / solvate / EM 等，或等待后续改进的自动链式。")

            QMessageBox.information(
                self, "已启动",
                "已触发 Topology (pdb2gmx)。\n"
                "请在控制台观察输出，等待它自然结束。\n\n"
                "后续阶段请根据日志手动执行或等待我们后续版本完善全自动流水线。"
            )

        except Exception as e:
            self.log(f"❌ 一键流程启动失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"一键流程启动失败:\n{str(e)}")
