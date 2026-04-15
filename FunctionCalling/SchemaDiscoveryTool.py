from langchain_core.tools import tool

from Database_Data.SchemaDiscovery import build_env_file, get_databases


@tool
def discover_schema(database: str = "") -> str:
    """探索指定数据库的结构，生成 schema JSON 文件到 Database_Data/host_port/database/table.txt。
    包含每个表的列信息和索引信息。如果 database 为空，则探索所有用户数据库。
    Args:
        database: 数据库名称；为空时探索所有数据库
    """
    print(f"[discover_schema输入] database: {database}")

    try:
        if database:
            result = build_env_file(database)
        else:
            # 探索所有用户数据库
            all_dbs = get_databases()
            system_dbs = {"information_schema", "mysql", "performance_schema", "sys"}
            user_dbs = [db for db in all_dbs if db not in system_dbs]
            if not user_dbs:
                return "没有找到用户数据库"

            results = []
            for db in user_dbs:
                r = build_env_file(db)
                results.append(r)
            result = "\n".join(results)

        print(f"[discover_schema输出] {result}")
        return result
    except Exception as e:
        result = f"探索失败: {str(e)}"
        print(f"[discover_schema输出] {result}")
        return result
