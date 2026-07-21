import subprocess
import os
from PyQt6.QtCore import QObject, pyqtSignal, QThread

class GromacsWorker(QThread):
    # 信号定义
    output_signal = pyqtSignal(str)     # 实时输出信号
    finished_signal = pyqtSignal(bool, str)  # 完成信号 (success, final_message)
    
    def __init__(self, gmx_path, args, cwd=None, input_text=None):
        super().__init__()
        self.gmx_path = gmx_path
        self.args = args
        self.cwd = cwd
        self.input_text = input_text

    def run(self):
        cmd = [self.gmx_path] + self.args
        cmd_str = ' '.join(cmd)
        cwd_str = self.cwd or os.getcwd()
        
        # 同时打印到控制台（Spyder / PowerShell），方便看到输出
        print(f"\n>>> 正在执行: {cmd_str}")
        print(f"    工作目录 (cwd): {cwd_str}")
        if self.input_text:
            print(f"    自动输入: {self.input_text.strip()}")

        # 只在开始时发一次启动信息到 GUI（轻量）
        self.output_signal.emit(f">>> 正在执行: {cmd_str} (详见控制台实时输出)")
        self.output_signal.emit(f"    工作目录: {cwd_str}")
        if self.input_text:
            self.output_signal.emit(f"    自动输入: {self.input_text.strip()}")

        # 额外保险：再次确保 GMXDATA 被设置（防止 runner 初始化时没生效）
        try:
            from .config import setup_gmx_environment
            setup_gmx_environment(self.gmx_path)
        except:
            pass
        
        full_output = []
        buffer_lines = []
        last_emit_time = 0
        
        try:
            popen_args = {
                "args": cmd,
                "cwd": self.cwd,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.STDOUT,
                "text": True,
                "encoding": 'utf-8',
                "errors": 'replace',
                "bufsize": 1
            }
            
            if self.input_text:
                popen_args["stdin"] = subprocess.PIPE
                
            process = subprocess.Popen(**popen_args)
            
            if self.input_text:
                try:
                    process.stdin.write(self.input_text + "\n")
                    process.stdin.close()
                except:
                    pass

            import time

            # === 终极激进保守策略（彻底防止 GUI 卡死）===
            # 控制台：100% 实时打印（你现在能看到几千行 [GMX] 就是最好的证明）
            # GUI 日志窗口：**几乎完全不更新**，只发极少关键信息
            #
            # 规则：
            #   1. 永远只发单行到 GUI
            #   2. 只在真正的里程碑时发（Making bonds, Number of bonds 等）
            #   3. 最多每 20 秒发一次心跳
            #   4. 结束时只发最后 25 行

            MILESTONES = [
                "Making bonds", "Making angles", "Generating angles",
                "Number of bonds", "Number of", "Opening force field",
                "There are", "Keeping all", "Finished",
                "pdb2gmx", "grompp", "mdrun", "solvate", "editconf",
                "Force field", "Water model", "System", "atoms", "bonds was"
            ]

            HEARTBEAT_SEC = 20.0
            line_count = 0

            def is_milestone(line):
                low = line.lower()
                return any(m.lower() in low for m in MILESTONES)

            while True:
                line = process.stdout.readline()
                if not line:
                    if process.poll() is not None:
                        break
                    continue

                stripped = line.rstrip('\n\r')
                if not stripped:
                    continue

                full_output.append(stripped)
                line_count += 1

                # ★ 控制台永远 100% 实时打印（你现在看到的几千行 [GMX] 就是证据）
                print(f"[GMX] {stripped}")

                # ★★★ 故意完全不调用 output_signal.emit() ★★★
                # pdb2gmx 在生成 S-S 表 + 二面角时会吐出上万行。
                # 任何频繁的 emit 都会让主线程（GUI）冻结 → 卡退。
                # 所以这里**完全不发**信号给 GUI。

            # 结束时也**不**通过 output_signal 发大量内容
            # 所有详细输出用户已经在控制台看到了
            # 只有 finished_signal 会在最后触发（轻量）

            return_code = process.poll()
            
            if return_code == 0:
                self.finished_signal.emit(True, "命令执行成功")
            else:
                # 关键修复：把完整的错误输出传给界面
                error_detail = "\n".join(full_output[-30:]) if full_output else "(无输出)"
                msg = f"命令执行失败，返回码: {return_code}\n\nGROMACS 输出 (最后30行):\n{error_detail}"
                self.finished_signal.emit(False, msg)
                
        except FileNotFoundError:
            self.finished_signal.emit(False, f"找不到 gmx 可执行文件: {self.gmx_path}\n请确认 gmx 已在 PATH 中或 GMX_PATH 正确设置。")
        except Exception as e:
            self.finished_signal.emit(False, f"执行异常: {str(e)}")

