# BrainstormAgent 多Agent头脑风暴复杂SQL生成 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 通过引入 BrainstormAgent 协调 Writer + Reviewer 双Agent讨论机制，提升复杂SQL生成的可用率。

**Architecture:** 新增 BrainstormAgent 作为协调者，管理 SqlWriterAgent 和 SqlReviewerAgent 的多轮讨论循环（最多3轮），MasterAgent 自动判断查询复杂度并路由。

**Tech Stack:** Python, LangChain, Deepseek LLM, PyMySQL

---

### Task 1: ExplainTool — EXPLAIN验证工具

**Files:**
- Create: `D:/python/SQL-Agent/FunctionCalling/ExplainTool.py`
- Test: `python -c "from FunctionCalling.ExplainTool import explain_sql; print('OK')"`

- [ ] **Step 1: 创建 ExplainTool**

```python
# D:/python/SQL-Agent/FunctionCalling/ExplainTool.py
from langchain_core.tools import tool
from Database_Data.Database import execute_sql


@tool
def explain_sql(sql: str) -> str:
    """执行EXPLAIN语句，返回SQL的执行计划用于性能分析
    Args:
        sql: 需要分析的SQL语句（会自动加上EXPLAIN前缀）
    """
    explain_sql_text = f"EXPLAIN {sql}"
    print(f"[explain_sql输入] {explain_sql_text}")
    result = execute_sql(explain_sql_text)
    print(f"[explain_sql输出] {result}")
    return result
```

- [ ] **Step 2: 验证导入**

Run: `python -c "from FunctionCalling.ExplainTool import explain_sql; print('OK')"`
Expected: `OK`

- [ ] **Step 3: 提交**

```bash
git add FunctionCalling/ExplainTool.py
git commit -m "feat: add EXPLAIN validation tool for SQL performance analysis"
```

---

### Task 2: SqlWriterPrompt 和 SqlReviewerPrompt — 两个Agent的提示词

**Files:**
- Create: `D:/python/SQL-Agent/Prompt/SqlWriterPrompt.py`
- Create: `D:/python/SQL-Agent/Prompt/SqlReviewerPrompt.py`

- [ ] **Step 1: 创建 SqlWriterPrompt**

```python
# D:/python/SQL-Agent/Prompt/SqlWriterPrompt.py
class SqlWriterPrompt:
    @staticmethod
    def getPrompt():
        return """你是SQL生成专家（SQL Writer），根据查询策略生成正确的MySQL SQL语句。

规则：
1. 严格按照给定的查询策略生成SQL，不要自行改变业务逻辑
2. 使用正确的MySQL语法，确保字段名、表名、JOIN条件准确
3. 数据库Schema文件位于 Database_Data/host_port/database/table.txt，使用 read_file 和 readList_command 查看
4. JSON Schema格式中列名使用 "cloumn"（历史拼写），包含Field、Type、Key等字段
5. 只输出SQL语句本身，不要输出任何解释或说明文字
6. 确保生成的SQL可以直接执行"""
```

- [ ] **Step 2: 创建 SqlReviewerPrompt**

```python
# D:/python/SQL-Agent/Prompt/SqlReviewerPrompt.py
class SqlReviewerPrompt:
    @staticmethod
    def getPrompt():
        return """你是SQL审查专家（SQL Reviewer），负责审查Writer生成的SQL。

审查维度：
1. 语法正确性：字段名、表名、JOIN条件、WHERE条件是否正确
2. 逻辑匹配度：SQL是否满足原始业务需求，聚合逻辑是否正确
3. 性能：使用EXPLAIN工具验证执行计划，避免type为ALL的全表扫描（除非数据量很小）

审查流程：
1. 使用 read_file 和 readList_command 查看相关表的Schema文件验证字段名
2. 使用 explain_sql 工具验证SQL执行计划
3. 判断SQL逻辑是否满足需求

输出格式（必须严格遵守）：
- 如果通过审查，只输出：PASS
- 如果不通过，输出：FAIL\n[具体修改意见，逐条列出]

注意：你只负责审查，不要修改SQL，只输出PASS或FAIL+意见。"""
```

- [ ] **Step 3: 提交**

```bash
git add Prompt/SqlWriterPrompt.py Prompt/SqlReviewerPrompt.py
git commit -m "feat: add Writer and Reviewer system prompts"
```

---

### Task 3: SqlWriterAgent 和 SqlReviewerAgent — 两个讨论角色Agent

**Files:**
- Create: `D:/python/SQL-Agent/Agent/SqlWriterAgent.py`
- Create: `D:/python/SQL-Agent/Agent/SqlReviewerAgent.py`

- [ ] **Step 1: 创建 SqlWriterAgent**

参考 `Agent/SqlAgent.py` 的模式（23行，create_agent模式）：

```python
# D:/python/SQL-Agent/Agent/SqlWriterAgent.py
import sys
import os


from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from FunctionCalling.DatabaseTool import input_sql
from FunctionCalling.ReadFile import read_file
from FunctionCalling.ListFiles import readList_command
from Prompt.SqlWriterPrompt import SqlWriterPrompt
from Llm.Deepseek import Deepseek
from Database_Data.Database import get_db_config


class SqlWriterAgent:
    def create_agent(self):
        tools = [input_sql, read_file, readList_command]

        agent = create_agent(
            model=Deepseek().getLlm(),
            tools=tools,
            system_prompt=SystemMessage(content="当前连接数据库信息：" + str(get_db_config()) + " " + SqlWriterPrompt.getPrompt()),
        )
        return agent
```

- [ ] **Step 2: 创建 SqlReviewerAgent**

```python
# D:/python/SQL-Agent/Agent/SqlReviewerAgent.py
import sys
import os


from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from FunctionCalling.ExplainTool import explain_sql
from FunctionCalling.ReadFile import read_file
from FunctionCalling.ListFiles import readList_command
from Prompt.SqlReviewerPrompt import SqlReviewerPrompt
from Llm.Deepseek import Deepseek
from Database_Data.Database import get_db_config


class SqlReviewerAgent:
    def create_agent(self):
        tools = [explain_sql, read_file, readList_command]

        agent = create_agent(
            model=Deepseek().getLlm(),
            tools=tools,
            system_prompt=SystemMessage(content="当前连接数据库信息：" + str(get_db_config()) + " " + SqlReviewerPrompt.getPrompt()),
        )
        return agent
```

- [ ] **Step 3: 验证导入**

Run: `python -c "from Agent.SqlWriterAgent import SqlWriterAgent; from Agent.SqlReviewerAgent import SqlReviewerAgent; print('OK')"`
Expected: `OK`

- [ ] **Step 4: 提交**

```bash
git add Agent/SqlWriterAgent.py Agent/SqlReviewerAgent.py
git commit -m "feat: add SqlWriterAgent and SqlReviewerAgent for brainstorm discussion"
```

---

### Task 4: SqlWriterTool 和 SqlReviewerTool — BrainstormAgent调用子Agent的桥接工具

**Files:**
- Create: `D:/python/SQL-Agent/FunctionCalling/SqlWriterTool.py`
- Create: `D:/python/SQL-Agent/FunctionCalling/SqlReviewerTool.py`

参考 `FunctionCalling/SqlAgentTool.py` 的桥接模式。

- [ ] **Step 1: 创建 SqlWriterTool**

```python
# D:/python/SQL-Agent/FunctionCalling/SqlWriterTool.py
from langchain_core.tools import tool

from Agent.SqlWriterAgent import SqlWriterAgent


@tool
def sql_writer_tool(content: str) -> str:
    """SQL Writer子Agent，根据查询策略生成SQL语句。
    Args:
        content: 查询策略描述，包含涉及的表、查询逻辑、关联条件等;
    """
    print(f"[sql_writer_tool输入] {content}")
    agent = SqlWriterAgent().create_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": content}]})
    last_ai_content = None
    for msg in result.get("messages", []):
        msg_type = getattr(msg, 'type', None)
        content = getattr(msg, "content", None)
        if msg_type == 'ai':
            last_ai_content = content
    print(f"[sql_writer_tool输出] {last_ai_content}")
    return last_ai_content if last_ai_content is not None else "未找到AI响应"
```

- [ ] **Step 2: 创建 SqlReviewerTool**

```python
# D:/python/SQL-Agent/FunctionCalling/SqlReviewerTool.py
from langchain_core.tools import tool

from Agent.SqlReviewerAgent import SqlReviewerAgent


@tool
def sql_reviewer_tool(content: str) -> str:
    """SQL Reviewer子Agent，审查Writer生成的SQL是否正确。
    Args:
        content: 待审查的SQL语句和原始需求; 例：原始需求：查询xxx；SQL：SELECT ...
    """
    print(f"[sql_reviewer_tool输入] {content}")
    agent = SqlReviewerAgent().create_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": content}]})
    last_ai_content = None
    for msg in result.get("messages", []):
        msg_type = getattr(msg, 'type', None)
        content = getattr(msg, "content", None)
        if msg_type == 'ai':
            last_ai_content = content
    print(f"[sql_reviewer_tool输出] {last_ai_content}")
    return last_ai_content if last_ai_content is not None else "未找到AI响应"
```

- [ ] **Step 3: 验证导入**

Run: `python -c "from FunctionCalling.SqlWriterTool import sql_writer_tool; from FunctionCalling.SqlReviewerTool import sql_reviewer_tool; print('OK')"`
Expected: `OK`

- [ ] **Step 4: 提交**

```bash
git add FunctionCalling/SqlWriterTool.py FunctionCalling/SqlReviewerTool.py
git commit -m "feat: add Writer and Reviewer bridge tools for BrainstormAgent"
```

---

### Task 5: BrainstormPrompt 和 BrainstormAgent — 协调者Agent

**Files:**
- Create: `D:/python/SQL-Agent/Prompt/BrainstormPrompt.py`
- Create: `D:/python/SQL-Agent/Agent/BrainstormAgent.py`

- [ ] **Step 1: 创建 BrainstormPrompt**

```python
# D:/python/SQL-Agent/Prompt/BrainstormPrompt.py
class BrainstormPrompt:
    @staticmethod
    def getPrompt():
        return """你是SQL头脑风暴协调者（Brainstorm Coordinator），负责管理 Writer 和 Reviewer 两个Agent的讨论流程，生成高质量的复杂SQL。

工作流程：
1. 分析用户需求，确定涉及哪些数据库表、查询逻辑、关联条件
2. 使用 sql_writer_tool 将查询策略交给 Writer 生成SQL
3. 使用 sql_reviewer_tool 将Writer的SQL交给 Reviewer 审查
4. 如果Reviewer输出PASS，则该SQL通过审查，继续下一步
5. 如果Reviewer输出FAIL+修改意见，将意见交给Writer重写（sql_writer_tool）
6. 重复步骤3-5，最多3轮讨论
7. 如果3轮后仍未通过，由你裁决并输出最佳结果

复杂度判断（满足任一条件即需要头脑风暴流程）：
- 查询涉及3张或以上表的JOIN
- 需要窗口函数（ROW_NUMBER, RANK, LAG, LEAD等）
- 需要子查询（EXISTS, IN子查询, FROM子查询）
- 需要CTE（WITH语句）
- 需要跨数据库JOIN
- 需要HAVING + 多层GROUP BY

规则：
1. 使用 read_file 和 readList_command 查看Schema文件确认表结构
2. 每轮讨论都要记录当前状态
3. 只输出最终SQL，不输出中间讨论过程
4. Schema文件格式参考 Database_Data/host_port/database/table.txt，JSON中列名用"cloumn"
5. 数据库信息："""
```

- [ ] **Step 2: 创建 BrainstormAgent**

```python
# D:/python/SQL-Agent/Agent/BrainstormAgent.py
import sys
import os


from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from FunctionCalling.SqlWriterTool import sql_writer_tool
from FunctionCalling.SqlReviewerTool import sql_reviewer_tool
from FunctionCalling.ExplainTool import explain_sql
from FunctionCalling.ReadFile import read_file
from FunctionCalling.ListFiles import readList_command
from Prompt.BrainstormPrompt import BrainstormPrompt
from Llm.Deepseek import Deepseek
from Database_Data.Database import get_db_config


class BrainstormAgent:
    def create_agent(self):
        tools = [sql_writer_tool, sql_reviewer_tool, explain_sql, read_file, readList_command]

        agent = create_agent(
            model=Deepseek().getLlm(),
            tools=tools,
            system_prompt=SystemMessage(content="当前连接数据库信息：" + str(get_db_config()) + " " + BrainstormPrompt.getPrompt()),
        )
        return agent
```

- [ ] **Step 3: 验证导入**

Run: `python -c "from Agent.BrainstormAgent import BrainstormAgent; print('OK')"`
Expected: `OK`

- [ ] **Step 4: 提交**

```bash
git add Prompt/BrainstormPrompt.py Agent/BrainstormAgent.py
git commit -m "feat: add BrainstormAgent coordinator for multi-agent SQL generation"
```

---

### Task 6: BrainstormAgentTool — MasterAgent调用BrainstormAgent的桥接工具

**Files:**
- Create: `D:/python/SQL-Agent/FunctionCalling/BrainstormAgentTool.py`

参考 `FunctionCalling/SqlAgentTool.py` 的模式。

- [ ] **Step 1: 创建 BrainstormAgentTool**

```python
# D:/python/SQL-Agent/FunctionCalling/BrainstormAgentTool.py
from langchain_core.tools import tool

from Agent.BrainstormAgent import BrainstormAgent


@tool
def brainstorm_agent_tool(content: str) -> str:
    """Brainstorm子Agent，通过多Agent头脑风暴机制（Writer+Reviewer讨论）生成复杂SQL。
    Args:
        content: 复杂查询需求描述，包含涉及的数据库表、查询逻辑等;
    """
    print(f"[brainstorm_agent_tool输入] {content}")
    agent = BrainstormAgent().create_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": content}]})
    last_ai_content = None
    for msg in result.get("messages", []):
        msg_type = getattr(msg, 'type', None)
        content = getattr(msg, "content", None)
        if msg_type == 'ai':
            last_ai_content = content
    print(f"[brainstorm_agent_tool输出] {last_ai_content}")
    return last_ai_content if last_ai_content is not None else "未找到AI响应"
```

- [ ] **Step 2: 验证导入**

Run: `python -c "from FunctionCalling.BrainstormAgentTool import brainstorm_agent_tool; print('OK')"`
Expected: `OK`

- [ ] **Step 3: 提交**

```bash
git add FunctionCalling/BrainstormAgentTool.py
git commit -m "feat: add BrainstormAgent bridge tool for MasterAgent"
```

---

### Task 7: 修改 MasterAgent 和 MasterPrompt — 注册新工具和路由规则

**Files:**
- Modify: `D:/python/SQL-Agent/Agent/MasterAgent.py`
- Modify: `D:/python/SQL-Agent/Prompt/MasterPrompt.py`

- [ ] **Step 1: 修改 MasterAgent.py，注册 brainstorm_agent_tool**

完整文件内容（仅增加 import 和 tools 注册）：

```python
# D:/python/SQL-Agent/Agent/MasterAgent.py
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
from FunctionCalling.SchemaDiscoveryTool import discover_schema
from FunctionCalling.SqlAgentTool import sql_agent_tool
from FunctionCalling.ExcelAgentTool import excel_agent_tool
from FunctionCalling.ExcelReaderTool import excel_reader
from FunctionCalling.ReadSkill import read_skill
from FunctionCalling.ExcelWriterTool import excel_writer
from FunctionCalling.ExcelImportTool import excel_import
from FunctionCalling.ExcelExportTool import excel_export
from FunctionCalling.SkillGeneratorTool import skill_generator_tool
from FunctionCalling.ListSkillsTool import list_skills_tool
from FunctionCalling.BrainstormAgentTool import brainstorm_agent_tool
from Prompt.MasterPrompt import MasterPrompt
from Llm.Deepseek import Deepseek
from Database_Data.Database import get_db_config
from Skill.skills import get_skill_prompt

class MasterAgent:
    def create_agent(self):
        tools = [input_sql, read_file, readList_command, discover_schema, sql_agent_tool, excel_agent_tool, excel_reader, read_skill, excel_writer, excel_import, excel_export, skill_generator_tool, list_skills_tool, brainstorm_agent_tool]

        agent = create_agent(
            model=Deepseek().getLlm(),
            tools=tools,
            system_prompt=SystemMessage(content="当前连接数据库信息：" + str(get_db_config()) + " " + MasterPrompt.getPrompt() + "\n" + get_skill_prompt()),
        )
        return agent
```

- [ ] **Step 2: 修改 MasterPrompt.py，增加复杂度判断和路由规则**

完整文件内容：

```python
# D:/python/SQL-Agent/Prompt/MasterPrompt.py
class MasterPrompt:
    @staticmethod
    def getPrompt():
        return    """你是SQL Agent的主Agent，负责调度各个子Agent工作，并使用自己的读取文件的能力，保证各个Agent的任务完成。
        你需要根据用户需求，判断当前需要调度哪个子Agent去完成任务，分别是：
        - SQL生成Agent（SqlAgent）：根据用户需求生成SQL语句
        - BrainstormAgent：通过多Agent头脑风暴机制生成复杂SQL

        数据库结构信息保存在 Database_Data/host(数据库地址)_port(数据库端口)/database(数据库名称)/table(表名称).txt
        当需要探索或更新数据库结构时，使用 discover_schema 工具自动生成环境文件。

        在../Database_data文件下保存的当前记录的数据库结构信息，结构信息如下：
        /Database_Data/host(数据库地址)_port(数据库端口)/database(数据库名称)/table(表名称).txt
        如果你发现文件中的结构有数据对不上或数据不完整，你可以使用 discover_schema 工具重新探索数据库结构，来更新环境文件。
        若用户提供的信息不完整，你必须向用户询问清楚，不允许自己去猜测用户的需求。

        路由规则（重要）：
        以下情况必须使用 brainstorm_agent_tool 交给 BrainstormAgent 处理：
        1. 查询涉及3张或以上表的JOIN
        2. 需要窗口函数（ROW_NUMBER, RANK, LAG, LEAD等）
        3. 需要子查询（EXISTS, IN子查询, FROM子查询）
        4. 需要CTE（WITH语句）
        5. 需要跨数据库JOIN
        6. 需要HAVING + 多层GROUP BY
        7. 用户明确要求使用头脑风暴流程

        简单SQL查询（单表或双表查询，不涉及复杂聚合/子查询/窗口函数）可以直接使用 sql_agent_tool 交给 SqlAgent 处理。

        注意：你不能去执行实际的任务（除了直接回答用户的简单SQL），你只能做任务调度。复杂的SQL生成必须交给子Agent完成。

        当用户需求匹配到可用 Skill 时，先使用 read_skill 工具读取该 Skill 文件了解完整工作流程，然后严格按照其中的步骤执行。
        系统提示词中的 Skill 列表可能在对话过程中过时，如果有新增 Skill 的场景，可使用 list_skills_tool 工具获取最新的 Skill 列表。
"""
```

- [ ] **Step 3: 验证导入**

Run: `python -c "from Agent.MasterAgent import MasterAgent; print('OK')"`
Expected: `OK`

- [ ] **Step 4: 提交**

```bash
git add Agent/MasterAgent.py Prompt/MasterPrompt.py
git commit -m "feat: register BrainstormAgent tool and add complexity routing rules"
```

---

### Task 8: 端到端验证

**Files:**
- 运行主程序验证完整流程

- [ ] **Step 1: 验证所有模块导入正常**

Run: `python -c "from FunctionCalling.ExplainTool import explain_sql; from FunctionCalling.SqlWriterTool import sql_writer_tool; from FunctionCalling.SqlReviewerTool import sql_reviewer_tool; from FunctionCalling.BrainstormAgentTool import brainstorm_agent_tool; from Agent.BrainstormAgent import BrainstormAgent; from Agent.SqlWriterAgent import SqlWriterAgent; from Agent.SqlReviewerAgent import SqlReviewerAgent; print('ALL OK')"`
Expected: `ALL OK`

- [ ] **Step 2: 运行主程序测试头脑风暴流程**

Run: `python main.py`
然后在交互中输入一个复杂查询需求，如："查询每个部门的员工数量和平均工资，并且只显示平均工资大于公司整体平均工资的部门"（这个查询涉及聚合+子查询，应路由到BrainstormAgent）

Expected: MasterAgent 判断为复杂查询 → 路由到 BrainstormAgent → Writer生成SQL → Reviewer审查 → 最终输出正确SQL

- [ ] **Step 3: 提交**

```bash
git add -A
git commit -m "chore: verify BrainstormAgent end-to-end flow"
```
