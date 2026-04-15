---
name: schema-discovery
description: 获取数据库结构并生成 schema JSON 数据建库结构的文件，用于后续 SQL 生成时的结构参考
---

# 数据库 Schema 探索

## 使用场景

当需要获取数据库的结构信息时使用，例如：

- 初始化新数据库连接后的首次环境探索
- 数据库结构变更后更新本地 schema 缓存
- 为 SQL 生成 Agent 提供准确的表结构信息

## 执行步骤

### 1. 调用发现工具

使用 `discover_schema(database)` 工具：
- 如果指定数据库名，只探索该数据库
- 如果不指定数据库名，探索所有用户数据库（跳过系统库）

### 2. 反馈结果

将 `discover_schema` 的执行结果告知用户，包括：
- 探索的表数量
- 生成的文件路径
- 失败时返回错误信息

## 文件结构

生成的文件位于 `Database_Data/<host>_<port>/<database>/<table>.txt`，JSON 格式：

```json
{
    "cloumn": [
        {
            "Field": "id",
            "Type": "int(11)",
            "Collation": "utf8_general_ci",
            "Null": "NO",
            "Key": "PRI",
            "Default": null,
            "Extra": "auto_increment",
            "Privileges": "select,insert,update,references",
            "Comment": ""
        }
    ],
    "index": [
        {
            "key_name": "PRIMARY",
            "non_unique": 0,
            "column_name": [
                {"Field": "id"}
            ],
            "index_type": "BTREE",
            "comment": ""
        }
    ]
}
```
