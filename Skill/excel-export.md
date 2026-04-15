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

### 2. 执行查询

使用 `input_sql` 执行上一步生成的 SQL 语句，获取查询结果：
- 列名列表
- 数据行列表
- 总行数

如果查询结果为空（0 行），告知用户无数据可导出，终止流程。

### 3. 写入 Excel 文件

使用 `excel_writer` 工具将查询结果写入 Excel 文件：
- `columns`: 查询结果的列名列表
- `rows`: 查询结果的数据行列表
- `file_name`: 可选，默认 `export_result.xlsx`，可根据查询内容命名（如 `users_export.xlsx`）

### 4. 反馈结果

将 `excel_writer` 的执行结果告知用户，包括：
- 导出的行数和列数
- 文件保存路径（`Database_Data/` 目录下）
