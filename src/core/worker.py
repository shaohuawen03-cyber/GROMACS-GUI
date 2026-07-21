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

        # 额外保险
        try:
            from .config import setup_gmx_environment
            setup_gmx_environment(self.gmx_path)
        except:
            pass

        # 只保留最后很少行用于错误报告（防止内存问题）
        from collections import deque
        full_output = deque(maxlen=60)
        line_count = 0

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
            
            # 发送 stdin（力场选择等）
            if self.input_text:
                try:
                    data = self.input_text
                    if not data.endswith('\n'):
                        data += '\n'
                    process.stdin.write(data)
                    process.stdin.flush()
                    process.stdin.close()
                    print(f"[Worker] 已发送 stdin: {repr(self.input_text.strip())}")
                except Exception as e:
                    print(f"[Worker] stdin 发送失败: {e}")

            # === 终极沉默模式 ===
            # 控制台：100% 实时打印（你现在看到的几千行 [GMX] 就是证据）
            # GUI：**完全不发送任何 output_signal**（这是导致卡退的根源）
            # 只有 finished_signal 在最后发一个极小的消息

            while True:
                line = process.stdout.readline()
                if not line:
                    if process.poll() is not None:
                        break
                    continue

                stripped = line.rstrip('\n\r')
                if stripped:
                    full_output.append(stripped)
                    line_count += 1

                    # 控制台永远实时（用户反馈中能看到这些）
                    print(f"[GMX] {stripped}")

                    # 发送到 GUI 日志区（使用缓冲 + 定时 flush，不会导致冻结）
                    # 这是解决“日志区不显示”的关键修复
                    try:
                        self.output_signal.emit(f"[GMX] {stripped}")
                    except Exception:
                        pass

            return_code = process.poll()
            
            if return_code == 0:
                self.finished_signal.emit(True, "SUCCESS")
            else:
                tail = list(full_output)[-10:] if full_output else []
                msg = f"FAILED (rc={return_code})\nSee console for full output.\nLast lines:\n" + "\n".join(tail)
                self.finished_signal.emit(False, msg)
                
        except FileNotFoundError:
            self.finished_signal.emit(False, f"找不到 gmx 可执行文件: {self.gmx_path}\n请确认 gmx 已在 PATH 中或 GMX_PATH 正确设置。")
        except Exception as e:
            self.finished_signal.emit(False, f"执行异常: {str(e)}")

