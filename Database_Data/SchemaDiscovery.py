import os
import json
import pymysql
from Database_Data.Database import get_db


def get_databases():
    """获取所有数据库名称列表"""
    conn = get_db()
    with conn.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SHOW DATABASES")
        return [row["Database"] for row in cursor.fetchall()]


def get_tables(database):
    """获取指定数据库中的所有表名称列表"""
    conn = get_db()
    with conn.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(f"SHOW TABLES FROM `{database}`")
        tables = list(cursor.fetchall())
        # SHOW TABLES 的列名是 "Tables_in_<database>"
        if tables:
            key = list(tables[0].keys())[0]
            return [row[key] for row in tables]
        return []


def get_columns(database, table):
    """获取指定表的列信息，返回列字典列表"""
    conn = get_db()
    with conn.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(f"SHOW FULL COLUMNS FROM `{database}`.`{table}`")
        return cursor.fetchall()


def get_indexes(database, table):
    """获取指定表的索引信息，返回索引字典列表"""
    conn = get_db()
    with conn.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(f"SHOW INDEX FROM `{database}`.`{table}`")
        return cursor.fetchall()


def _build_index_json(indexes):
    """将索引列表转换为 Skill 文档要求的 JSON 格式"""
    index_map = {}
    for idx in indexes:
        name = idx["Key_name"]
        if name not in index_map:
            index_map[name] = {
                "key_name": name,
                "non_unique": int(idx["Non_unique"]),
                "column_name": [],
                "index_type": idx["Index_type"],
                "comment": idx.get("Comment", ""),
            }
        index_map[name]["column_name"].append({"Field": idx["Column_name"]})
    return list(index_map.values())


def build_env_file(database):
    """探索指定数据库的 schema，生成 JSON 文件到 Database_Data/host_port/database/table.txt"""
    conn = get_db()
    host = conn.host
    port = conn.port

    # 获取表列表
    tables = get_tables(database)
    if not tables:
        return f"错误: 数据库 '{database}' 中没有表"

    base_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "Database_Data",
        f"{host}_{port}",
        database,
    )
    os.makedirs(base_dir, exist_ok=True)

    created_files = []
    for table in tables:
        columns = get_columns(database, table)
        indexes = get_indexes(database, table)

        schema_data = {
            "cloumn": columns,
            "index": _build_index_json(indexes),
        }

        file_path = os.path.join(base_dir, f"{table}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(schema_data, f, indent=4, ensure_ascii=False)
        created_files.append(f"{table}.txt")

    return f"环境构建完成: {len(tables)} 个表 → {base_dir}\n文件: {', '.join(created_files)}"
