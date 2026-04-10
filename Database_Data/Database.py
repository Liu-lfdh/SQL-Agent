import pymysql

_db_config = None
_connection = None


def init_db(host, port, user, password, charset="utf8mb4"):
    """初始化数据库配置并建立连接"""
    global _db_config, _connection
    _db_config = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "charset": charset
    }
    _connection = pymysql.connect(**_db_config)
    print("数据库连接成功")
    return _connection


def get_db():
    """获取全局数据库连接，如果断开则自动重连"""
    global _connection
    if _connection is None:
        raise RuntimeError("数据库未初始化，请先调用 init_db()")
    try:
        _connection.ping(reconnect=True)
    except Exception:
        _connection = pymysql.connect(**_db_config)
    return _connection


def execute_sql(sql):
    """执行 SQL 语句并返回结果"""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                if not rows:
                    return "(0 行记录)"

                # 计算每列最大宽度
                col_widths = [len(str(c)) for c in columns]
                for row in rows:
                    for i, v in enumerate(row):
                        col_widths[i] = max(col_widths[i], len(str(v)))

                # 构建表格输出
                lines = []
                header = " | ".join(str(c).ljust(col_widths[i]) for i, c in enumerate(columns))
                lines.append(header)
                lines.append("-+-".join("-" * w for w in col_widths))
                for row in rows:
                    line = " | ".join(str(v).ljust(col_widths[i]) for i, v in enumerate(row))
                    lines.append(line)
                lines.append(f"\n共 {len(rows)} 行记录")
                return "\n".join(lines)
            else:
                conn.commit()
                return f"影响 {cursor.rowcount} 行"
    except Exception as e:
        conn.rollback()
        return f"错误: {e}"


def get_db_config():
    """获取数据库连接配置（host 和 port）"""
    if _db_config is None:
        raise RuntimeError("数据库未初始化，请先调用 init_db()")
    return {"host": _db_config["host"], "port": _db_config["port"]}


def close_db():
    """关闭数据库连接"""
    global _connection
    if _connection:
        _connection.close()
        _connection = None
        print("数据库已断开")
