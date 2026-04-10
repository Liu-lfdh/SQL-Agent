import re
from langchain_core.tools import tool
from Database_Data.Database import execute_sql

# 不幂等的 DML 语句
DANGEROUS_KEYWORDS = ["DELETE", "UPDATE", "INSERT", "DROP", "TRUNCATE", "ALTER", "CREATE", "REPLACE"]


def is_dangerous_sql(sql: str) -> bool:
    """判断 SQL 是否包含不幂等的危险操作"""
    sql_upper = sql.upper().strip()
    return any(re.match(rf"\b{kw}\b", sql_upper) for kw in DANGEROUS_KEYWORDS)


# 自定义工具
@tool
def input_sql(sql: str) -> str:
    """输入SQL语句并执行，获取执行结果
    Args:
        sql: 执行的SQL语句
    """
    print(f"[input_sql输入] {sql}")
    """执行SQL语句前进行安全检查，禁止执行包含不幂等操作的SQL"""
    if is_dangerous_sql(sql):
        confirm = input(f"⚠️ 该 SQL 包含不幂等操作 ({', '.join(DANGEROUS_KEYWORDS)})，是否确认执行？输入 yes 继续: ")
        if confirm.strip().lower() != "yes":
            result = "操作已取消"
            print(f"[input_sql输出] {result}")
            return result

    result = execute_sql(sql)
    print(f"[input_sql输出] {result}")
    return result