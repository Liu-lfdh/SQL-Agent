import os
from langchain_core.tools import tool
from openpyxl import Workbook

ALLOWED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Database_Data/"))


@tool
def excel_writer(columns: list, rows: list, file_name: str = "export_result.xlsx") -> str:
    """将查询结果写入 Excel(.xlsx) 文件
    Args:
        columns: 列名列表，例如 ["id", "name", "email"]
        rows: 数据行列表，每行是一个值的列表，例如 [["1", "Alice", "alice@example.com"]]
        file_name: 导出文件名，默认 export_result.xlsx，文件会保存到 Database_Data/ 目录下
    """
    print(f"[excel_writer输入] 列: {columns}, 行数: {len(rows)}, 文件: {file_name}")

    if not columns:
        result = "错误: 没有列名，无法导出"
        print(f"[excel_writer输出] {result}")
        return result

    if not rows:
        result = "错误: 没有数据可导出"
        print(f"[excel_writer输出] {result}")
        return result

    if not file_name.lower().endswith(".xlsx"):
        file_name += ".xlsx"

    full_path = os.path.normpath(os.path.join(ALLOWED_DIR, file_name))
    if not full_path.startswith(ALLOWED_DIR):
        result = "错误: 仅允许导出到 Database_Data/ 目录"
        print(f"[excel_writer输出] {result}")
        return result

    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        wb = Workbook()
        ws = wb.active
        ws.append(columns)
        for row in rows:
            ws.append([str(v) if v is not None else None for v in row])
        wb.save(full_path)
        wb.close()

        rel_path = os.path.relpath(full_path, ALLOWED_DIR)
        result = f"导出成功: {len(rows)} 行 x {len(columns)} 列 → Database_Data/{rel_path}"
        print(f"[excel_writer输出] {result}")
        return result
    except Exception as e:
        result = f"导出失败: {str(e)}"
        print(f"[excel_writer输出] {result}")
        return result
