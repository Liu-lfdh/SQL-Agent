import os
from langchain_core.tools import tool


ALLOWED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Database_Data/"))


@tool
def create_file(file_path: str, content: str) -> str:
    """在 Database_Data 目录下创建 txt 文件
    Args:
        file_path: 文件路径，相对于 Database_Data/ 目录
        content: 要写入的文件内容
    """
    print(f"[create_file输入] 文件: {file_path}, 内容长度: {len(content)} 字符")

    full_path = os.path.normpath(os.path.join(ALLOWED_DIR, file_path))
    if not full_path.startswith(ALLOWED_DIR):
        result = "错误: 不允许在 Database_Data 目录以外创建文件"
        print(f"[create_file输出] {result}")
        return result

    if not full_path.endswith('.txt'):
        result = "错误: 只允许创建 .txt 文件"
        print(f"[create_file输出] {result}")
        return result

    try:
        parent_dir = os.path.dirname(full_path)
        os.makedirs(parent_dir, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as file:
            file.write(content)
        result = f"文件创建成功: {file_path}"
    except Exception as e:
        result = f"创建文件失败: {str(e)}"
    print(f"[create_file输出] {result}")
    return result
