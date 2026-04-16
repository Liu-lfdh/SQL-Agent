---
name: excel-export
description: 将数据库查询结果导出为 Excel(.xlsx) 文件，支持自然语言描述查询需求
---

# Excel 导出

## 使用场景

当需要将数据库查询结果导出为 Excel(.xlsx) 文件时使用，例如：

- 导出某个表的全部或部分数据
- 导出自定义查询的结果
- 生成数据报表供线下分析

## 执行步骤

### 1. 生成 SQL

使用 `sql_agent_tool` 根据用户的自然语言描述生成 SQL 查询语句。
- 告诉 sql_agent_tool 用户想要导出什么数据
- 确保生成的 SQL 是 SELECT 语句

如果无法确定用户的需求，可直接告知用户需要什么数据，让用户提供更多信息。

### 2. 导出文件

使用 `excel_export(sql, file_name)` 工具执行查询并写入 Excel：
- `sql`: 上一步生成的 SELECT 查询语句
- `file_name`: 可选，默认 `export_result.xlsx`，可根据查询内容命名（如 `users_export.xlsx`）

工具内部会自动执行查询、获取结果、写入 Excel 文件。

如果查询无数据，告知用户无数据可导出。

### 3. 反馈结果

将 `excel_export` 的执行结果告知用户，包括：
- 导出的行数和列数
- 文件保存路径（`Database_Data/` 目录下）
