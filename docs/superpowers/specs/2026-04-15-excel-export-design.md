# Excel 导出 Skill 设计

## 概述

为 SQL-Agent 添加数据库查询结果导出为 Excel(.xlsx) 文件的 Skill 能力。用户用自然语言描述导出需求，系统自动生成 SQL、执行查询、写入 Excel 文件。

## 架构

### 新增组件

1. **`FunctionCalling/ExcelWriterTool.py`** — `excel_writer` 工具
   - 参数：`columns`（列名列表）、`rows`（数据行列表）、`file_name`（文件名）
   - 功能：用 `openpyxl` 写入 `.xlsx` 文件，保存到 `Database_Data/`
   - 返回：导出结果摘要（行数、列数、文件路径）

2. **`Skill/excel-export.md`** — Skill 文档
   - 4 步工作流：生成 SQL → 执行查询 → 写入 Excel → 反馈结果
   - 使用 `sql_agent_tool` 生成 SQL，`input_sql` 执行，`excel_writer` 写入

### 依赖

- `openpyxl`（已安装，项目已有）
- 现有工具：`sql_agent_tool`、`input_sql`

### 注册

- `MasterAgent.tools` 新增 `excel_writer`
- `skills.py` 自动扫描 `Skill/` 目录，`excel-export.md` 自动注册

## 数据流

```
用户描述 → read_skill("excel-export") 获取流程
         → sql_agent_tool 生成 SQL
         → input_sql 执行查询
         → excel_writer 写入 .xlsx
         → 反馈结果
```

## 错误处理

- 查询结果为空：提示用户无数据，不生成空文件
- SQL 执行失败：返回错误信息，告知用户
- Excel 写入失败：清理临时文件，返回错误信息
