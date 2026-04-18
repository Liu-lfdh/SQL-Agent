from langchain_core.tools import tool
from Database_Data.Database import execute_sql


@tool
def explain_sql(sql: str) -> str:
    """执行EXPLAIN语句，返回SQL的执行计划用于性能分析
    Args:
        sql: 需要分析的SQL语句（会自动加上EXPLAIN前缀）
    """
    explain_sql_text = f"EXPLAIN {sql}"
    print(f"[explain_sql输入] {explain_sql_text}")
    result = execute_sql(explain_sql_text)
    print(f"[explain_sql输出] {result}")
    return result
