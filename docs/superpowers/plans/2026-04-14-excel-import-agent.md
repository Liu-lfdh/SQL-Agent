# Excel Import Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an ExcelAgent that reads `.xlsx` files, infers column-to-database-field mappings, shows mappings and SQL previews to the user for confirmation, then batch-inserts data into MySQL within a single transaction.

**Architecture:** New sub-agent (`ExcelAgent`) with two tools (`ExcelReaderTool` for parsing xlsx, `input_sql` for executing SQL). Wrapped as `excel_agent_tool` and registered in `MasterAgent`'s tool list. Follows the same Agent + Tool pattern as `SqlAgent`/`sql_agent_tool` and `EnvironmentAgent`/`environment_agent_tool`.

**Tech Stack:** Python, langchain, openpyxl, pymysql (already in project), Deepseek LLM via ChatOpenAI

---

### Task 1: Install openpyxl dependency

**Files:**
- No code files to modify

- [ ] **Step 1.1: Install openpyxl**

```bash
cd D:/python/SQL-Agent && pip install openpyxl
```

Expected: `Successfully installed openpyxl-<version>`

- [ ] **Step 1.2: Commit**

```bash
git add -A && git commit -m "chore: add openpyxl dependency for Excel import"
```

---

### Task 2: Create `ExcelPrompt.py` — System prompt for ExcelAgent

**Files:**
- Create: `D:/python/SQL-Agent/Prompt/ExcelPrompt.py`

This defines the system prompt that instructs the LLM on the Excel import workflow: read Excel, infer mappings, show mapping to user, show SQL preview, confirm, execute.

- [ ] **Step 2.1: Write the prompt**

```python
class ExcelPrompt:
    @staticmethod
    def getPrompt():
        return """你是Excel数据导入Agent，负责将Excel(.xlsx)文件中的数据智能映射到数据库表并批量插入。

工作流程：
1. 使用 excel_reader_tool 读取Excel文件，获取列名、数据样例、总行数
2. 使用 input_sql 执行 "DESC <表名>" 获取目标表的字段结构（包括字段名、类型、是否允许NULL、默认值）
3. 根据Excel列名和数据样例，推断Excel列与数据库表字段的映射关系
4. 【重要】向用户展示推断的映射关系，格式如下：
   | Excel列名 | → | 数据库字段 | 类型 | 是否可为NULL |
   如果目标表存在 不可为NULL 的字段没有被映射到，必须明确警告用户哪些字段缺失
5. 等待用户确认映射关系是否正确。如果用户指出错误，根据用户反馈重新推断
6. 映射确认后，生成批量INSERT SQL语句
7. 向用户展示SQL预览：前3条SQL样例 + 总行数 + 总列数
8. 等待用户确认是否执行SQL

规则：
- 每个步骤都必须等待用户确认后再继续
- INSERT语句使用批量格式: INSERT INTO table (col1, col2) VALUES (...), (...), ...
- 所有数据都在同一个事务中，任何一行失败则全部回滚
- Excel中的空值对应NULL，除非目标字段不允许NULL
- 数字类型的Excel数据需要去除引号，字符串类型需要加引号并转义特殊字符
- 你是多Agent系统中的子Agent，不需要有过多的表达，严格按照工作流程执行
"""
```

- [ ] **Step 2.2: Commit**

```bash
git add Prompt/ExcelPrompt.py && git commit -m "feat: add ExcelPrompt for ExcelAgent"
```

---

### Task 3: Create `ExcelReaderTool.py` — Read `.xlsx` files

**Files:**
- Create: `D:/python/SQL-Agent/FunctionCalling/ExcelReaderTool.py`

This tool reads an `.xlsx` file and returns structured data: column names, sample rows (first 5), total row count. The LLM will use this for mapping inference.

- [ ] **Step 3.1: Write the tool**

```python
import os
from langchain_core.tools import tool


@tool
def excel_reader(file_path: str) -> str:
    """读取Excel(.xlsx)文件，返回列名、前5行样例数据、总行数和每列数据类型推断
    Args:
        file_path: Excel文件的绝对路径或相对于项目根目录的路径
    """
    print(f"[excel_reader输入] 文件: {file_path}")

    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)

    if not os.path.exists(file_path):
        result = f"错误: 文件不存在: {file_path}"
        print(f"[excel_reader输出] {result}")
        return result

    if not file_path.endswith(".xlsx"):
        result = "错误: 仅支持 .xlsx 格式的Excel文件"
        print(f"[excel_reader输出] {result}")
        return result

    try:
        from openpyxl import load_workbook
        wb = load_workbook(file_path, read_only=True, data_only=True)
        ws = wb.active

        if ws is None:
            result = "错误: 无法读取Excel工作表"
            print(f"[excel_reader输出] {result}")
            wb.close()
            return result

        rows = list(ws.iter_rows(values_only=True))

        if not rows:
            result = "错误: Excel文件为空"
            print(f"[excel_reader输出] {result}")
            wb.close()
            return result

        columns = [str(h) for h in rows[0]]
        data_rows = rows[1:]
        total_rows = len(data_rows)

        if total_rows == 0:
            result = "错误: Excel文件只有表头，没有数据行"
            print(f"[excel_reader输出] {result}")
            wb.close()
            return result

        # 推断每列的数据类型
        dtypes = {}
        for col_idx in range(len(columns)):
            vals = [row[col_idx] for row in data_rows if row[col_idx] is not None]
            if not vals:
                dtypes[columns[col_idx]] = "unknown"
                continue
            type_counts = {}
            for v in vals:
                t = type(v).__name__
                type_counts[t] = type_counts.get(t, 0) + 1
            dominant = max(type_counts, key=type_counts.get)
            dtypes[columns[col_idx]] = dominant

        # 构建输出：列名 + 前5行样例 + 总行数 + 类型推断
        sample_count = min(5, total_rows)
        lines = []
        lines.append(f"总行数: {total_rows}")
        lines.append(f"列名: {columns}")
        lines.append(f"列数据类型: {dtypes}")
        lines.append(f"\n前{sample_count}行样例:")
        for i in range(sample_count):
            lines.append(f"  行{i+1}: {list(data_rows[i])}")

        result = "\n".join(lines)
        print(f"[excel_reader输出] 成功读取Excel，{total_rows}行 x {len(columns)}列")
        wb.close()
        return result
    except Exception as e:
        result = f"读取Excel失败: {str(e)}"
        print(f"[excel_reader输出] {result}")
        return result
```

- [ ] **Step 3.2: Commit**

```bash
git add FunctionCalling/ExcelReaderTool.py && git commit -m "feat: add ExcelReaderTool for parsing .xlsx files"
```

---

### Task 4: Create `ExcelAgent.py` — The Agent class

**Files:**
- Create: `D:/python/SQL-Agent/Agent/ExcelAgent.py`

This is the core agent that coordinates the entire Excel import workflow. It uses `ExcelReaderTool` and `input_sql` as its tools, guided by the `ExcelPrompt`.

- [ ] **Step 4.1: Write the agent**

```python
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage

from FunctionCalling.ExcelReaderTool import excel_reader
from FunctionCalling.DatabaseTool import input_sql
from Prompt.ExcelPrompt import ExcelPrompt
from Llm.Deepseek import Deepseek
from Database_Data.Database import get_db_config


class ExcelAgent:
    def create_agent(self):
        tools = [excel_reader, input_sql]

        agent = create_agent(
            model=Deepseek().getLlm(),
            tools=tools,
            system_prompt=SystemMessage(
                content="当前连接数据库信息：" + str(get_db_config()) + " " + ExcelPrompt.getPrompt()
            ),
        )
        return agent
```

- [ ] **Step 4.2: Commit**

```bash
git add Agent/ExcelAgent.py && git commit -m "feat: add ExcelAgent class with ExcelReaderTool and input_sql"
```

---

### Task 5: Create `excel_agent_tool` — Tool wrapper for MasterAgent

**Files:**
- Create: `D:/python/SQL-Agent/FunctionCalling/ExcelAgentTool.py`

This follows the same pattern as `sql_agent_tool` and `environment_agent_tool`: create the agent, invoke it, extract the last AI message, return it.

- [ ] **Step 5.1: Write the tool**

```python
from langchain_core.tools import tool

from Agent.ExcelAgent import ExcelAgent


@tool
def excel_agent_tool(content: str) -> str:
    """Excel数据导入子Agent，负责将Excel文件数据智能映射到数据库表并批量插入。
    Args:
        content: 任务内容，需包含Excel文件路径和目标表名。例：将 ./data/users.xlsx 导入到 user 表中；
    """
    print(f"[excel_agent_tool输入] {content}")
    agent = ExcelAgent().create_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": content}]})
    last_ai_content = None
    for msg in result.get("messages", []):
        msg_type = getattr(msg, 'type', None)
        content = getattr(msg, "content", None)
        if msg_type == 'ai':
            last_ai_content = content
    print(f"[excel_agent_tool输出] {last_ai_content}")
    return last_ai_content if last_ai_content is not None else "未找到AI响应"
```

- [ ] **Step 5.2: Commit**

```bash
git add FunctionCalling/ExcelAgentTool.py && git commit -m "feat: add excel_agent_tool wrapper for MasterAgent"
```

---

### Task 6: Register `excel_agent_tool` in MasterAgent

**Files:**
- Modify: `D:/python/SQL-Agent/Agent/MasterAgent.py`

Add the import and register the new tool in the MasterAgent's tool list. Also update the MasterPrompt to mention the ExcelAgent capability.

- [ ] **Step 6.1: Update MasterAgent.py imports and tools**

Current content:
```python
from FunctionCalling.SqlAgentTool import sql_agent_tool;
from Prompt.MasterPrompt import MasterPrompt
```

Add import after existing tool imports:
```python
from FunctionCalling.ExcelAgentTool import excel_agent_tool
```

Change tools list from:
```python
tools = [input_sql, read_file, readList_command, environment_agent_tool, sql_agent_tool]
```

To:
```python
tools = [input_sql, read_file, readList_command, environment_agent_tool, sql_agent_tool, excel_agent_tool]
```

- [ ] **Step 6.2: Update MasterPrompt to mention ExcelAgent**

Current prompt in `D:/python/SQL-Agent/Prompt/MasterPrompt.py`:
```python
return    """你是SQL Agent的主Agent，负责调度各个子Agent工作，并使用自己的读取文件的能力，保证各个Agent的任务完成。
    你需要根据用户需求，判断当前需要调度哪个子Agent去完成任务，分别是环境探索Agent（EnvironmentAgent）和SQL生成Agent（SqlAgent）。
    ...
"""
```

Change to:
```python
return    """你是SQL Agent的主Agent，负责调度各个子Agent工作，并使用自己的读取文件的能力，保证各个Agent的任务完成。
    你需要根据用户需求，判断当前需要调度哪个子Agent去完成任务，分别是：
    - 环境探索Agent（EnvironmentAgent）：探索数据库结构，生成环境配置文件
    - SQL生成Agent（SqlAgent）：根据用户需求生成SQL语句
    - Excel导入Agent（ExcelAgent）：将Excel(.xlsx)文件数据智能映射到数据库表并批量插入
    在../Database_data文件下保存的当前记录的数据库结构信息，结构信息如下：
    /Database_Data/host(数据库地址)_port(数据库端口)/database(数据库名称)/table(表名称).txt
    你可以通过sql的show databases和 show tables from databases_name来获取真实数据库中的结构数据
    如果你发现文件中的结构有数据对不上或数据不完整，你可以要求环境探索Agent（EnvironmentAgent）去更新对应的环境文件，来获取最新的数据库结构信息。
    若用户提供的信息不完整，你必须向用户询问清楚，不允许自己去猜测用户的需求。
    注意：你不能去执行实际的任务，你只能做任务调度，不允许生成SQL语句去回答用户问题，SQL生成必须交给SqlAgent或ExcelAgent去完成
"""
```

- [ ] **Step 6.3: Commit**

```bash
git add Agent/MasterAgent.py Prompt/MasterPrompt.py && git commit -m "feat: register excel_agent_tool in MasterAgent and update MasterPrompt"
```

---

### Task 7: Test the integration

**Files:**
- No files to create
- Test: Manual verification via `main.py`

- [ ] **Step 7.1: Create a test Excel file**

Create a simple `test_data.xlsx` in `D:/python/SQL-Agent/` with:
- Sheet columns: `姓名`, `年龄`, `邮箱`
- 3 rows of sample data

- [ ] **Step 7.2: Run the app and test via MasterAgent**

```bash
cd D:/python/SQL-Agent && python main.py
```

Then in the chat, input something like:
```
将 ./test_data.xlsx 导入到 test_table 表中
```

Expected flow:
1. MasterAgent delegates to `excel_agent_tool`
2. ExcelAgent reads the Excel file, shows column mapping to user
3. User confirms mapping
4. ExcelAgent shows SQL preview (sample SQLs + total count)
5. User confirms SQL
6. Data is inserted into the database

- [ ] **Step 7.3: Verify database has the inserted data**

Use `input_sql` to run `SELECT * FROM test_table` and verify rows were inserted.

- [ ] **Step 7.4: Commit any test files or cleanup**

```bash
git status
# Clean up test files if needed
```

---

## Self-Review

**1. Spec coverage check:**
- ✅ Read `.xlsx` files → `ExcelReaderTool`
- ✅ Infer column mapping → LLM in `ExcelAgent` with `ExcelPrompt`
- ✅ Show mapping to user for confirmation → Prompt instructs this
- ✅ Warn about missing NOT NULL fields → Prompt instructs this
- ✅ Generate batch INSERT SQL → Prompt instructs bulk INSERT format
- ✅ Show SQL preview → Prompt instructs sample + count display
- ✅ User confirms before execution → Built into workflow + `input_sql` confirmation
- ✅ Transaction safety (all or nothing) → Single INSERT statement = atomic
- ✅ Use Deepseek LLM → `Deepseek().getLlm()`
- ✅ Encapsulate as tool for MasterAgent → `excel_agent_tool`
- ✅ Register in MasterAgent tool list → Task 6

**2. Placeholder scan:** No TBD, TODO, or vague sections. All code shown.

**3. Type/Name consistency:**
- Tool names: `excel_reader` (tool function), `excel_agent_tool` (wrapper) — both `@tool` decorated
- Agent class: `ExcelAgent` with `create_agent()` method — matches pattern
- Prompt class: `ExcelPrompt` with `getPrompt()` — matches pattern
- File paths consistent with existing project structure

Plan is complete and ready for execution.
