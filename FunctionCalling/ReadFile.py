import os
from langchain_core.tools import tool

ALLOWED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Database_Data/"))

@tool
def read_file(file_path: str) -> str:
    """输入读取文件的路径，返回文件内容
    Args:
        file_path: 需要读取的文件路径，必须位于 Database_Data/ 目录下
    """
    print(f"[read_file输入] {file_path}")
    full_path = os.path.normpath(os.path.join(ALLOWED_DIR, file_path))
    if not full_path.startswith(ALLOWED_DIR):
        result = "错误: 不允许读取 Database_Data 目录以外的文件"
        print(f"[read_file输出] {result}")
        return result
    try:
        with open(full_path, 'r', encoding='utf-8') as file:
            content = file.read()
        print(f"[read_file输出] 成功读取文件，共 {len(content)} 字符")
        return content
    except Exception as e:
        result = f"读取文件失败: {str(e)}"
        print(f"[read_file输出] {result}")
        return result
