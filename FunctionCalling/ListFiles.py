import os
from langchain_core.tools import tool


@tool
def readList_command(path: str = ".") -> str:
    """列出指定目录下的文件和子目录，使用相对路径,你可以使用这个工具来查看项目中的所有文件和目录结构.
    Args:
        path: 要列出的目录路径，相对路径基于项目根目录。默认为项目根目录（./）
    """
    print(f"[readList_command输入] 目录: {path}")
    target = os.path.normpath(os.path.join(".", path))

    if not os.path.exists(target):
        result = f"错误: 路径不存在: {path}"
        print(f"[readList_command输出] {result}")
        return result

    if not os.path.isdir(target):
        result = f"错误: 路径不是目录: {path}"
        print(f"[readList_command输出] {result}")
        return result

    try:
        lines = []
        for root, dirs, files in os.walk(target):
            rel_root = os.path.relpath(root, target)
            prefix = "" if rel_root == "." else rel_root.replace(os.sep, "/") + "/"
            for d in sorted(dirs):
                lines.append(f"  📁 {prefix}{d}/")
            for f in sorted(files):
                lines.append(f"  📄 {prefix}{f}")
        result = "\n".join(lines) if lines else "目录为空"
    except Exception as e:
        result = f"执行失败: {str(e)}"
    print(f"[readList_command输出] {result}")
    return result
