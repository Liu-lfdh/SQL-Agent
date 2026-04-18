---
name: BrainstormAgent Multi-Agent Complex SQL Generation
date: 2026-04-18
status: approved
---

# BrainstormAgent 多Agent头脑风暴复杂SQL生成设计

## 问题

当前 SqlAgent 仅23行代码，通过单次 `agent.invoke()` 生成SQL，缺乏迭代验证、多步分解能力。对于多表JOIN、窗口函数、子查询等复杂SQL，生成的语句经常不可用。

## 目标

引入多Agent头脑风暴机制（Writer + Reviewer 双Agent讨论），通过"分析需求 → Writer生成 → Reviewer审查 → 迭代修改"的流程，提升复杂SQL的可用率。

## 架构

```
用户输入复杂查询需求
         |
         v
   MasterAgent (自动判断复杂度)
         |
    [复杂?] --Yes--> BrainstormAgent (协调者)
         |              |
        No             |
         |             v
   直接走SqlAgent   分解查询计划
                      (确定涉及的表、查询策略)
                           |
                    ┌──────┴──────┐
                    |             |
                Writer         Reviewer
             (生成SQL)        (审查SQL+EXPLAIN)
                    |             |
                    └──────┬──────┘
                           |
                    讨论循环（最多3轮）
                    ┌──────────────────────┐
                    |                      |
                  Writer 生成SQL           |
                    → Reviewer 审查        |
                      → 通过? → 输出最终SQL |
                      → 不通过? → 提修改意见 |
                        → Writer 根据意见重写 |
                        → Reviewer 再审查     |
                        → ...（最多3轮）      |
                    └──────────────────────┘
                           |
                    BrainstormAgent 汇总输出
                           |
                           v
                    MasterAgent 执行
```

## 组件设计

### 1. BrainstormAgent (`Agent/BrainstormAgent.py`)

- **角色**: 协调者（Coordinator），管理 Writer 和 Reviewer 的讨论流程
- **职责**:
  1. 分析用户需求，确定涉及的表和查询策略
  2. 将查询策略传递给 Writer 生成初版 SQL
  3. 将 Writer 的 SQL 传递给 Reviewer 审查
  4. 如果 Reviewer 通过 → 输出最终 SQL
  5. 如果 Reviewer 不通过 → 将修改意见传给 Writer 重写
  6. 最多循环 3 轮，超过则 BrainstormAgent 介入裁决
- **工具**: `[sql_writer_tool, sql_reviewer_tool, explain_tool, read_file, readList_command]`
- **LLM**: `Deepseek().getLlm()`

### 2. SqlWriterAgent (`Agent/SqlWriterAgent.py`)

- **角色**: SQL 生成专家（Writer）
- **职责**: 根据 BrainstormAgent 提供的查询策略生成 SQL
- **工具**: `[input_sql, read_file, readList_command]`
- **LLM**: `Deepseek().getLlm()`

### 3. SqlReviewerAgent (`Agent/SqlReviewerAgent.py`)

- **角色**: SQL 审查专家（Reviewer）
- **职责**: 审查 Writer 生成的 SQL，包括语法正确性、性能、逻辑匹配度
- **工具**: `[explain_tool, read_file, readList_command]`
- **LLM**: `Deepseek().getLlm()`

### 4. ExplainTool (`FunctionCalling/ExplainTool.py`)

- **功能**: 执行 `EXPLAIN <sql>` 语句，返回执行计划
- **输入**: SQL字符串
- **输出**: EXPLAIN 结果的文本格式（type, key, rows, Extra等列）
- **安全性**: 只读操作，无危险

### 5. BrainstormAgentTool (`FunctionCalling/BrainstormAgentTool.py`)

- **功能**: MasterAgent 调用 BrainstormAgent 的桥接工具
- **输入**: `content` — 用户的复杂查询需求 + 相关数据库规格
- **输出**: BrainstormAgent 生成的最终SQL语句
- **每次创建新实例**，无状态复用（与 sql_agent_tool 一致）

### 6. SqlWriterTool (`FunctionCalling/SqlWriterTool.py`)

- **功能**: BrainstormAgent 调用 SqlWriterAgent 的桥接工具
- **输入**: `content` — 查询策略（涉及的表、需要查询的逻辑）
- **输出**: SqlWriterAgent 生成的 SQL 语句

### 7. SqlReviewerTool (`FunctionCalling/SqlReviewerTool.py`)

- **功能**: BrainstormAgent 调用 SqlReviewerAgent 的桥接工具
- **输入**: `content` — 待审查的 SQL + 原始需求
- **输出**: Reviewer 的审查意见（通过/不通过 + 具体修改建议）

## 提示词设计

### BrainstormPrompt (`Prompt/BrainstormPrompt.py`)

系统提示词要点：
- 你是SQL头脑风暴协调者，负责管理 Writer 和 Reviewer 的讨论
- 先分析用户需求，确定涉及哪些表、查询策略是什么
- 将查询策略交给 Writer 生成 SQL
- 将 Writer 的 SQL 交给 Reviewer 审查
- 如果 Reviewer 通过，输出最终 SQL
- 如果 Reviewer 不通过，将修改意见交给 Writer 重写
- 最多讨论 3 轮，超过由你裁决并输出最佳结果
- **只输出最终SQL，不输出中间过程**

### SqlWriterPrompt (`Prompt/SqlWriterPrompt.py`)

系统提示词要点：
- 你是SQL生成专家，根据查询策略生成正确的 SQL
- 严格按照给定的查询策略生成，不要自行改变逻辑
- 使用正确的 MySQL 语法
- Schema 文件格式参考 `Database_Data/host_port/database/table.txt`
- **只输出 SQL 语句，不要输出解释**

### SqlReviewerPrompt (`Prompt/SqlReviewerPrompt.py`)

系统提示词要点：
- 你是SQL审查专家，审查 Writer 生成的 SQL
- 审查维度：
  1. 语法正确性（字段名、表名、JOIN条件是否正确）
  2. 逻辑匹配度（SQL是否满足原始需求）
  3. 性能（用 EXPLAIN 验证，避免全表扫描）
- 如果通过 → 输出 "PASS"
- 如果不通过 → 输出 "FAIL" + 具体修改意见
- **只输出审查结果，不要修改 SQL**

### 复杂度判断规则

MasterAgent 的 prompt 中增加以下自动判断条件：
1. 查询涉及表数量 >= 3
2. 需要聚合 + 子查询 / 窗口函数
3. 需要 CTE (WITH 语句)
4. 需要跨数据库 JOIN
5. 需要 HAVING + 多层 GROUP BY

满足任一条件 → 路由到 BrainstormAgent

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `Agent/BrainstormAgent.py` | 新增 | 协调者Agent主体 |
| `Agent/SqlWriterAgent.py` | 新增 | Writer Agent |
| `Agent/SqlReviewerAgent.py` | 新增 | Reviewer Agent |
| `FunctionCalling/BrainstormAgentTool.py` | 新增 | MasterAgent调用BrainstormAgent的桥接工具 |
| `FunctionCalling/SqlWriterTool.py` | 新增 | BrainstormAgent调用Writer的桥接工具 |
| `FunctionCalling/SqlReviewerTool.py` | 新增 | BrainstormAgent调用Reviewer的桥接工具 |
| `FunctionCalling/ExplainTool.py` | 新增 | EXPLAIN验证工具 |
| `Prompt/BrainstormPrompt.py` | 新增 | BrainstormAgent系统提示词 |
| `Prompt/SqlWriterPrompt.py` | 新增 | Writer系统提示词 |
| `Prompt/SqlReviewerPrompt.py` | 新增 | Reviewer系统提示词 |
| `Agent/MasterAgent.py` | 修改 | 注册 brainstorm_agent_tool |
| `Prompt/MasterPrompt.py` | 修改 | 增加复杂度判断和路由规则 |

## 成功标准

- 复杂SQL（3表以上JOIN、窗口函数、子查询）能生成可执行且正确的SQL
- Writer 和 Reviewer 能进行有效讨论，最多3轮迭代
- EXPLAIN 验证确保生成SQL的执行计划合理
- MasterAgent 能自动判断是否需要头脑风暴流程
