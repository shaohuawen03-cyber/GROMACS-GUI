import subprocess
import os
from .config import get_gmx_path
from .worker import GromacsWorker

class GromacsRunner:
    def __init__(self):
        self.gmx_path = get_gmx_path()

        # 强制设置数据目录（解决 No force fields found）
        try:
            from .config import setup_gmx_environment
            setup_gmx_environment(self.gmx_path)
        except:
            pass

        # 调试日志（启动时打印一次）
        gmxdata = os.environ.get("GMXDATA", "(未设置)")
        gmxlib = os.environ.get("GMXLIB", "(未设置)")
        print(f"[GromacsRunner] 使用 gmx: {self.gmx_path}")
        print(f"[GromacsRunner] GMXDATA={gmxdata}")
        print(f"[GromacsRunner] GMXLIB={gmxlib}")

    def run_command(self, args, cwd=None, input_text=None):
        cmd = [self.gmx_path] + args
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                input=input_text,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, f"命令执行失败，返回码: {e.returncode}\n\n输出详情:\n{e.output}"
        except Exception as e:
            return False, f"执行出现异常: {str(e)}"

    def create_worker(self, args, cwd=None, input_text=None):
        return GromacsWorker(self.gmx_path, args, cwd, input_text)
