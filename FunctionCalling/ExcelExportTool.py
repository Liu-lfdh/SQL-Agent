import os
import time
from langchain_core.tools import tool
from openpyxl import Workbook

from Database_Data.Database import get_db

ALLOWED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Database_Data/"))

# 只读关键字，只允许 SELECT 查询
SAFE_KEYWORDS = ["SELECT"]
DANGEROUS_KEYWORDS = ["INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER", "CREATE", "REPLACE"]


@tool
def excel_export(sql: str, file_name: str = "export_result.xlsx") -> str:
    """执行 SQL SELECT 查询并将结果直接写入 Excel(.xlsx) 文件，不经过 LLM 中转数据。

    Args:
        sql: SELECT 查询语句
        file_name: 导出文件名，默认 export_result.xlsx，文件会保存到 Database_Data/ 目录下
    """
    print(f"[excel_export输入] SQL: {sql[:100]}..., 文件: {file_name}")

    # --- SQL 安全检查 ---
    sql_upper = sql.strip().upper()
    if not any(sql_upper.startswith(kw) for kw in SAFE_KEYWORDS):
        result = "错误: 仅支持 SELECT 查询语句"
        print(f"[excel_export输出] {result}")
        return result

    if any(sql_upper.startswith(kw) for kw in DANGEROUS_KEYWORDS):
        result = "错误: 不允许执行写操作"
        print(f"[excel_export输出] {result}")
        return result

    # --- 文件名安全检查 ---
    if not file_name.lower().endswith(".xlsx"):
        file_name += ".xlsx"

    full_path = os.path.normpath(os.path.join(ALLOWED_DIR, file_name))
    if not full_path.startswith(ALLOWED_DIR):
        result = "错误: 仅允许导出到 Database_Data/ 目录"
        print(f"[excel_export输出] {result}")
        return result

    # --- 执行查询 + 写入 Excel ---
    start_time = time.time()
    wb = None

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(sql)

        # 获取列名
        if cursor.description is None:
            result = "错误: 查询没有返回列信息"
            print(f"[excel_export输出] {result}")
            return result

        columns = [desc[0] for desc in cursor.description]

        # 分批写入 Excel，避免全部加载到内存
        BATCH_SIZE = 1000
        total_rows = 0

        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        wb = Workbook()
        ws = wb.active
        ws.append(columns)

        while True:
            rows = cursor.fetchmany(BATCH_SIZE)
            if not rows:
                break
            for row in rows:
                ws.append([_convert_value(v) for v in row])
            total_rows += len(rows)

        wb.save(full_path)

        if total_rows == 0:
            result = "查询无数据可导出"
            print(f"[excel_export输出] {result}")
            return result

        elapsed = time.time() - start_time
        rel_path = os.path.relpath(full_path, ALLOWED_DIR)
        result = f"导出成功: {total_rows} 行 x {len(columns)} 列 → Database_Data/{rel_path}\n耗时: {elapsed:.2f} 秒"
        print(f"[excel_export输出] {result}")
        return result

    except Exception as e:
        result = f"导出失败: {e}"
        print(f"[excel_export输出] {result}")
        return result
    finally:
        if wb is not None:
            wb.close()


def _convert_value(val):
    """将数据库查询值转换为适合 Excel 的类型。"""
    from datetime import datetime, date, time as dt_time

    if val is None:
        return None
    if isinstance(val, datetime):
        return val.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(val, date):
        return val.strftime('%Y-%m-%d')
    if isinstance(val, dt_time):
        return val.strftime('%H:%M:%S')
    # Decimal 转 float
    if hasattr(val, '__float__') and not isinstance(val, (int, float, bool)):
        return float(val)
    return val
