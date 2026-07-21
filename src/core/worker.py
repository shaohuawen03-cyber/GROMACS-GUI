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
        
        self.output_signal.emit(f">>> 正在执行: {cmd_str}")
        self.output_signal.emit(f"    工作目录 (cwd): {cwd_str}")
        if self.input_text:
            self.output_signal.emit(f"    自动输入: {self.input_text.strip()}")
        
        full_output = []
        
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

            # 实时读取所有输出
            while True:
                line = process.stdout.readline()
                if not line:
                    if process.poll() is not None:
                        break
                    continue
                stripped = line.rstrip('\n\r')
                if stripped:
                    full_output.append(stripped)
                    self.output_signal.emit(stripped)

            return_code = process.poll()
            
            if return_code == 0:
                self.finished_signal.emit(True, "命令执行成功")
            else:
                # 关键修复：把完整的错误输出传给界面
                error_detail = "\n".join(full_output[-25:]) if full_output else "(无输出)"
                msg = f"命令执行失败，返回码: {return_code}\n\nGROMACS 输出:\n{error_detail}"
                self.finished_signal.emit(False, msg)
                
        except FileNotFoundError:
            self.finished_signal.emit(False, f"找不到 gmx 可执行文件: {self.gmx_path}\n请确认 gmx 已在 PATH 中或 GMX_PATH 正确设置。")
        except Exception as e:
            self.finished_signal.emit(False, f"执行异常: {str(e)}")

