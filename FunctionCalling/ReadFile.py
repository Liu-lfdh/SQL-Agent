import os
from langchain_core.tools import tool


@tool
def read_file(file_path: str) -> str:
    """读取项目 ./ 目录下的文件内容
    Args:
        file_path: 需要读取的文件路径，相对路径基于项目根目录(.)
    """
    print(f"[read_file输入] 文件: {file_path}")
    target = os.path.normpath(file_path)
    abs_target = os.path.abspath(target)
    abs_root = os.path.abspath(".")

    # 安全检查：确保解析后的路径在项目根目录下
    if not abs_target.startswith(abs_root + os.sep) and abs_target != abs_root:
        result = f"错误: 不允许读取项目根目录以外的文件: {file_path}"
        print(f"[read_file输出] {result}")
        return result

    if not os.path.exists(target):
        result = f"错误: 文件不存在: {file_path}"
        print(f"[read_file输出] {result}")
        return result

    if not os.path.isfile(target):
        result = f"错误: 路径不是文件: {file_path}"
        print(f"[read_file输出] {result}")
        return result

    try:
        with open(target, 'r', encoding='utf-8') as file:
            content = file.read()
        result = content
    except Exception as e:
        result = f"读取文件失败: {str(e)}"
    print(f"[read_file输出] 成功读取文件，共 {len(result)} 字符")
    return result
