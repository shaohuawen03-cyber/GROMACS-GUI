import subprocess
import os
from .config import get_gmx_path
from .worker import GromacsWorker

class GromacsRunner:
    def __init__(self):
        raw_path = get_gmx_path()
        self.gmx_path = raw_path

        # 关键修复：尝试设置 GROMACS 数据目录（解决 No force fields found）
        try:
            from .config import setup_gmx_environment
            setup_gmx_environment(self.gmx_path)
        except:
            pass

    def run_command(self, args, cwd=None, input_text=None):
        """
        同步执行 GROMACS 命令并返回输出 (保留用于快速、无阻塞的命令)
        :param args: 参数列表
        :param cwd: 工作目录
        :param input_text: 标准输入内容
        :return: (bool, str) 成功与否，以及输出日志
        """
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
        """
        创建一个异步 Worker 用于执行耗时命令
        """
        return GromacsWorker(self.gmx_path, args, cwd, input_text)
