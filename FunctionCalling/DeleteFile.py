import os
from langchain_core.tools import tool


ALLOWED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Database_Data/"))


@tool
def delete_file(file_path: str) -> str:
    """删除 Database_Data 目录下的文件
    Args:
        file_path: 文件路径，相对于 ../Database_Data/ 目录下
    """
    print(f"[delete_file输入] {file_path}")

    full_path = os.path.normpath(os.path.join(ALLOWED_DIR, file_path))
    if not full_path.startswith(ALLOWED_DIR):
        result = "错误: 不允许删除 Database_Data 目录以外的文件"
        print(f"[delete_file输出] {result}")
        return result

    if not os.path.exists(full_path):
        result = f"错误: 文件 '{file_path}' 不存在"
        print(f"[delete_file输出] {result}")
        return result

    if os.path.isdir(full_path):
        result = "错误: 只允许删除文件，不允许删除目录"
        print(f"[delete_file输出] {result}")
        return result

    try:
        os.remove(full_path)
        result = f"文件删除成功: {file_path}"
    except Exception as e:
        result = f"删除文件失败: {str(e)}"
    print(f"[delete_file输出] {result}")
    return result
