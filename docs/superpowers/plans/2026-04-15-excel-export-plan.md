# Excel 导出 Skill 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 添加数据库查询结果导出为 Excel(.xlsx) 文件的 Skill 能力，用户用自然语言描述导出需求，系统自动生成 SQL、执行查询、写入 Excel 文件。

**Architecture:** 新增 `excel_writer` 工具接收列名+数据行+文件名，用 `openpyxl` 写入 `.xlsx` 到 `Database_Data/` 目录。新增 `excel-export.md` Skill 文档定义 4 步工作流：生成 SQL → 执行查询 → 写入 Excel → 反馈结果。注册工具到 MasterAgent，Skill 自动被 `skills.py` 扫描发现。

**Tech Stack:** openpyxl, langchain_core.tools, pymysql（已有）

---

### Task 1: 创建 ExcelWriterTool 工具

**Files:**
- Create: `FunctionCalling/ExcelWriterTool.py`

- [ ] **Step 1: 创建 ExcelWriterTool.py**

```python
import os
from langchain_core.tools import tool
from openpyxl import Workbook

ALLOWED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Database_Data/"))


@tool
def excel_writer(columns: list, rows: list, file_name: str = "export_result.xlsx") -> str:
    """将查询结果写入 Excel(.xlsx) 文件
    Args:
        columns: 列名列表，例如 ["id", "name", "email"]
        rows: 数据行列表，每行是一个值的列表，例如 [["1", "Alice", "alice@example.com"]]
        file_name: 导出文件名，默认 export_result.xlsx，文件会保存到 Database_Data/ 目录下
    """
    print(f"[excel_writer输入] 列: {columns}, 行数: {len(rows)}, 文件: {file_name}")

    if not rows:
        result = "错误: 没有数据可导出"
        print(f"[excel_writer输出] {result}")
        return result

    if not file_name.lower().endswith(".xlsx"):
        file_name += ".xlsx"

    full_path = os.path.normpath(os.path.join(ALLOWED_DIR, file_name))
    if not full_path.startswith(ALLOWED_DIR):
        result = "错误: 仅允许导出到 Database_Data/ 目录"
        print(f"[excel_writer输出] {result}")
        return result

    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        wb = Workbook()
        ws = wb.active
        ws.append(columns)
        for row in rows:
            ws.append([str(v) if v is not None else None for v in row])
        wb.save(full_path)
        wb.close()

        rel_path = os.path.relpath(full_path, ALLOWED_DIR)
        result = f"导出成功: {len(rows)} 行 x {len(columns)} 列 → Database_Data/{rel_path}"
        print(f"[excel_writer输出] {result}")
        return result
    except Exception as e:
        result = f"导出失败: {str(e)}"
        print(f"[excel_writer输出] {result}")
        return result
```

- [ ] **Step 2: 验证语法**

Run: `python -c "import FunctionCalling.ExcelWriterTool; print('OK')"`
Expected: `OK`

- [ ] **Step 3: 提交**

```bash
git add FunctionCalling/ExcelWriterTool.py
git commit -m "feat: add excel_writer tool for exporting query results to .xlsx"
```

---

### Task 2: 注册 excel_writer 到 MasterAgent

**Files:**
- Modify: `Agent/MasterAgent.py`

- [ ] **Step 1: 修改 MasterAgent.py**

在 import 部分添加：
```python
from FunctionCalling.ExcelWriterTool import excel_writer
```

在 tools 列表中添加 `excel_writer`：
```python
tools = [input_sql, read_file, readList_command, environment_agent_tool, sql_agent_tool, excel_agent_tool, excel_reader, read_skill, excel_writer]
```

完整文件内容为：
```python
import sys
import os


from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from FunctionCalling.DatabaseTool import input_sql
from FunctionCalling.WriteFile import write_file
from FunctionCalling.ReadFile import read_file
from FunctionCalling.ListFiles import readList_command
from FunctionCalling.CreateFile import create_file
from FunctionCalling.DeleteFile import delete_file
from FunctionCalling.EnvironmentAgentTool import environment_agent_tool;
from FunctionCalling.SqlAgentTool import sql_agent_tool;
from FunctionCalling.ExcelAgentTool import excel_agent_tool
from FunctionCalling.ExcelReaderTool import excel_reader
from FunctionCalling.ReadSkill import read_skill
from FunctionCalling.ExcelWriterTool import excel_writer
from Prompt.MasterPrompt import MasterPrompt
from Llm.Deepseek import Deepseek
from Database_Data.Database import get_db_config
from Skill.skills import get_skill_prompt

class MasterAgent:
    def create_agent(self):
        tools = [input_sql, read_file, readList_command, environment_agent_tool, sql_agent_tool, excel_agent_tool, excel_reader, read_skill, excel_writer]

        agent = create_agent(
            model=Deepseek().getLlm(),
            tools=tools,
            system_prompt=SystemMessage(content="当前连接数据库信息：" + str(get_db_config()) + " " + MasterPrompt.getPrompt() + "\n" + get_skill_prompt()),
            )
        return agent
```

- [ ] **Step 2: 验证导入**

Run: `python -c "from Agent.MasterAgent import MasterAgent; print('OK')"`
Expected: `OK`

- [ ] **Step 3: 提交**

```bash
git add Agent/MasterAgent.py
git commit -m "feat: register excel_writer tool in MasterAgent"
```

---

### Task 3: 创建 excel-export Skill 文档

**Files:**
- Create: `Skill/excel-export.md`

- [ ] **Step 1: 创建 Skill 文件**

```markdown
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
```

- [ ] **Step 2: 验证 skills.py 能自动扫描到新 Skill**

Run: `python Skill/skills.py`
Expected output should include:
```
可用 Skill：
- excel-export: 将数据库查询结果导出为 Excel(.xlsx) 文件，支持自然语言描述查询需求
- excel-import: 将 Excel(.xlsx) 文件数据导入到数据库表中，支持自动列映射和用户确认流程
...
```

- [ ] **Step 3: 提交**

```bash
git add Skill/excel-export.md
git commit -m "feat: add excel-export skill documentation"
```

---

## 自审检查

1. **Spec 覆盖：** 设计文档中的 4 步工作流全部有对应任务实现（SQL生成→sql_agent_tool、执行查询→input_sql、写入Excel→excel_writer、反馈→excel_writer返回值）
2. **无占位符：** 所有代码步骤都有完整代码，无 TBD/TODO
3. **类型一致：** `excel_writer` 参数签名（columns: list, rows: list, file_name: str）与 Skill 文档中描述一致
4. **Scope 聚焦：** 仅实现导出功能，无额外功能扩展
