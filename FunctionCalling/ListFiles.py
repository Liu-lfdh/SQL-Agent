import subprocess
from langchain_core.tools import tool
import os


ALLOWED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
ALLOWED_PREFIX = "dir /b ..\\"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@tool
def readList_command(command: str) -> str:
    """执行目录列表命令，用于查看目录下的文件列表
    Args:
        command: 执行的Windows命令，输入必须以 'dir /b ..\\' 开头，返回命令行输出
    """
    print(f"[readList_command输入] {command}")
    if not command.strip().startswith(ALLOWED_PREFIX):
        result = f"错误: 命令必须以 '{ALLOWED_PREFIX}' 开头"
        print(f"[readList_command输出] {result}")
        return result

    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='gbk',
            timeout=10,
            cwd=os.path.join(PROJECT_ROOT, "FunctionCalling")
        )
        output = (proc.stdout or "").strip() or (proc.stderr or "").strip()
        result = output or "目录为空"
    except subprocess.TimeoutExpired:
        result = "错误: 命令执行超时"
    except Exception as e:
        result = f"执行命令失败: {str(e)}"
    print(f"[readList_command输出] {result}")
    return result
