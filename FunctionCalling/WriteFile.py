import os
from langchain_core.tools import tool

ALLOWED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Database_Data/"))

@tool
def write_file(file_path: str, content: str) -> str:
    """写入内容到文件
    Args:
        file_path: 需要写入的文件路径，必须位于 Database_Data/ 目录下
        content: 要写入的内容,内容会直接覆盖原文件内容
    """
    print(f"[write_file输入] 文件: {file_path}, 内容长度: {len(content)} 字符")
    full_path = os.path.normpath(os.path.join(ALLOWED_DIR, file_path))
    if not full_path.startswith(ALLOWED_DIR):
        result = "错误: 不允许写入 Database_Data 目录以外的文件"
        print(f"[write_file输出] {result}")
        return result
    try:
        with open(full_path, 'w', encoding='utf-8') as file:
            file.write(content)
        result = "文件写入成功"
    except Exception as e:
        result = f"写入文件失败: {str(e)}"
    print(f"[write_file输出] {result}")
    return result