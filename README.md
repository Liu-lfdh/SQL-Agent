[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# SQL-Agent

基于 Windows 操作系统的 MySQL 数据库智能 Agent，采用多 Agent + Skill 架构，支持自然语言对话式的 SQL 查询生成、执行、数据库结构探索和 Excel 数据导入/导出。

## 功能特性

- **自然语言查询**：用自然语言描述需求，Agent 自动生成并执行对应 SQL
- **数据库结构探索**：纯代码自动发现数据库表结构、字段信息、索引等元数据，无需 LLM
- **Excel 数据导入**：读取 `.xlsx` 文件，智能映射列到数据库字段，用户确认后批量插入
- **Excel 数据导出**：将数据库查询结果导出为 `.xlsx` 文件
- **Skill 系统**：可扩展的 Skill 文档驱动工作流，新增能力只需添加 `.md` 文件
- **多 Agent 协作**：主控 Agent 根据任务类型智能路由到专用子 Agent
- **上下文持久化**：对话历史自动保存为 JSON，支持跨会话恢复
- **SQL 安全保护**：危险操作（DELETE/UPDATE/DROP 等）执行前需手动确认
- **大内容自动卸载**：超过 20KB 的工具输出自动存储为独立文件，避免上下文膨胀
- **上下文自动压缩**：超出阈值时触发清理，工具调用详情自动精简，必要时调用压缩 Agent 对历史对话进行摘要

## 项目结构

```
SQL-Agent/
├── main.py                      # 程序入口，数据库配置，对话循环
│
├── Agent/                       # Agent 定义
│   ├── MasterAgent.py           # 主控 Agent，负责任务路由
│   ├── SqlAgent.py              # SQL 生成专家 Agent
│   ├── ExcelAgent.py            # Excel 数据导入 Agent
│   └── TitleAgent.py            # 会话标题生成 Agent
│
├── FunctionCalling/             # 工具函数
│   ├── DatabaseTool.py          # SQL 执行工具 (input_sql)
│   ├── ExcelReaderTool.py       # Excel 读取工具 (excel_reader)
│   ├── ExcelWriterTool.py       # Excel 写入工具 (excel_writer)
│   ├── SchemaDiscoveryTool.py   # 数据库结构探索工具 (discover_schema)
│   ├── ReadSkill.py             # Skill 文件读取工具 (read_skill)
│   ├── ReadFile.py              # 文件读取工具 (read_file)
│   ├── ListFiles.py             # 目录列表工具 (readList_command)
│   ├── WriteFile.py             # 文件写入工具 (write_file)
│   ├── CreateFile.py            # 文件创建工具 (create_file)
│   ├── DeleteFile.py            # 文件删除工具 (delete_file)
│   ├── ExcelAgentTool.py        # ExcelAgent 调用工具
│   └── SqlAgentTool.py          # SqlAgent 调用工具
│
├── Prompt/                      # 系统提示词
│   ├── MasterPrompt.py          # MasterAgent 提示词
│   ├── SqlPrompt.py             # SqlAgent 提示词
│   ├── ExcelPrompt.py           # ExcelAgent 提示词
│   └── CompressionPrompt.py     # CompressionAgent 提示词
│
├── Skill/                       # Skill 文档目录
│   ├── skills.py                # Skill 元数据扫描器
│   ├── excel-import.md          # Excel 导入 Skill
│   ├── excel-export.md          # Excel 导出 Skill
│   └── schema-discovery.md      # 数据库结构探索 Skill
│
├── Context/                     # 上下文管理
│   ├── MasterContext.py         # 上下文管理器（持久化/加载）
│   └── message.py               # 消息数据模型
│
├── Database_Data/               # 数据库结构缓存目录
│   ├── Database.py              # MySQL 连接层
│   └── SchemaDiscovery.py       # 数据库结构探索（纯 Python 代码）
│
└── Llm/                         # LLM 提供商抽象
    ├── Deepseek.py              # Deepseek Chat 模型
    └── qwen.py                  # Qwen Plus 模型
```

## 架构设计

```
                         用户输入
                            |
                            v
                      +-----------+
                      |  main.py  |  (对话循环、上下文管理)
                      +-----------+
                            |
                            v
                  +-------------------+
                  |   MasterAgent     |  (任务编排/路由)
                  |  (Deepseek LLM)   |
                  +-------------------+
                            |
        +-------------------+-------------------+-------------------+
        |                   |                   |                   |
        v                   v                   v                   v
+----------------+  +----------------+  +---------------+  +----------------+
| discover_schema|  |    sql_agent   |  | excel_agent_  |  | 内置工具       |
| (纯 Python 代码) |  |    tool        |  | tool          |  | input_sql     |
+----------------+  +----------------+  +---------------+  | read_file     |
        |                   |                   |         | readList      |
        v                   v                   v         +---------------+
+----------------+  +----------------+  +---------------+
|SchemaDiscovery |  |   SqlAgent     |  |  ExcelAgent   |
| (纯 Python 代码) |  | (Deepseek)     |  | (Deepseek)    |
+----------------+  +----------------+  +---------------+
                                              |
                                              v
                                      +----------------+
                                      | excel_reader   |
                                      +----------------+
                                              |
                                              v
                                       openpyxl 读取
                                       .xlsx 文件
+-------------------+
|  Database.py      |  (pymysql 连接层)
|  Database_Data/   |  (表结构缓存文件)
+-------------------+
        |
        v
     MySQL 服务器
```

## Agent 说明

### MasterAgent
主控 Agent，负责任务识别和路由。不直接生成 SQL 或执行查询，而是根据用户意图将任务委派给专用子 Agent 或 Skill。

### SqlAgent
SQL 生成专家。接收任务描述和数据库结构信息，生成对应的 SQL 查询语句。

### ExcelAgent
Excel 数据导入专家。读取 `.xlsx` 文件，根据已确认的列映射关系生成批量 INSERT SQL 并执行。
- 通过 `excel_reader` 工具解析 Excel 文件，获取列名、数据样例和总行数
- 根据用户提供的列映射（Excel 列名 → 数据库字段名）生成批量 INSERT 语句
- 执行前展示 SQL 预览，用户通过 `input_sql` 内置确认机制审核后执行
- 所有数据在同一事务中提交，任何一行失败则全部回滚

### TitleAgent
会话标题生成器。根据用户的第一条消息自动生成简洁的会话标题（20 字符以内）。

### CompressionAgent
对话压缩专家。接收过长的历史对话，提取关键信息（客观事实、用户意图、SQL 语句），生成精简摘要。

## Skill 系统

SQL-Agent 采用 Skill 文档驱动的可扩展架构。每个 Skill 是一个 `.md` 文件，定义完整的工作流程。新增能力只需：

1. 在 `Skill/` 目录下创建 `.md` 文件
2. 添加 frontmatter：`name` 和 `description`
3. 编写执行步骤，引用现有工具

系统启动时自动扫描所有 Skill，并在 MasterAgent 提示词中动态注入 Skill 列表。

| Skill | 描述 |
|-------|------|
| `schema-discovery` | 探索数据库结构并生成 schema JSON 文件 |
| `excel-import` | 将 Excel 数据导入到数据库表 |
| `excel-export` | 将数据库查询结果导出为 Excel 文件 |

## 工具说明

| 工具 | 功能 |
|------|------|
| `input_sql` | 执行 SQL 查询，危险操作需确认 |
| `read_file` | 读取项目根目录下的文件 |
| `readList_command` | 列出目录内容 |
| `write_file` | 写入文件到 `Database_Data/` |
| `create_file` | 创建 `.txt` 文件到 `Database_Data/` |
| `delete_file` | 删除 `Database_Data/` 中的文件 |
| `excel_reader` | 读取 `.xlsx` 文件，返回列名、样例数据、总行数和列类型推断 |
| `excel_writer` | 将查询结果（列名+数据行）写入 `.xlsx` 文件 |
| `discover_schema` | 探索数据库结构，生成 JSON 缓存文件（纯 Python 代码，无需 LLM） |
| `read_skill` | 读取指定名称的 Skill 工作流程文件 |
| `sql_agent_tool` | 调用 SqlAgent 进行 SQL 生成 |
| `excel_agent_tool` | 调用 ExcelAgent 进行 Excel 数据导入 |

## 快速开始

### 环境要求

- Python 3.x
- MySQL 数据库

### 安装依赖

```bash
pip install pymysql langchain langchain-openai openpyxl python-dotenv
```

### 配置

复制 `.env.example` 为 `.env`，填入 API Key：

```
DEEPSEEK_API_KEY=your-api-key-here
```

在 [main.py](main.py) 的 `init_db_connection()` 函数中修改数据库连接信息：

```python
init_db(
    host="192.168.200.130",
    port=3306,
    user="root",
    password="root"
)
```

### 运行

```bash
python main.py
```

启动后：
1. 连接数据库
2. 选择已有会话或创建新会话
3. 输入自然语言问题即可开始对话
4. 输入 `exit` 退出程序

## 使用场景

### Excel 数据导入

向对话中输入类似以下的指令即可触发 Excel 导入流程：

```
将 ./test_coupon_info.xlsx 导入到 coupon_info 表中
```

MasterAgent 会自动：
1. 读取 Excel 文件的列名和数据样例
2. 查询目标表结构，推断列映射关系
3. 向你展示映射表格，等待确认
4. 确认后将任务交给 ExcelAgent 执行插入

ExcelAgent 会生成批量 INSERT SQL，展示预览后通过 `input_sql` 执行。

### Excel 数据导出

向对话中输入类似以下的指令即可触发出：

```
把用户表导出为Excel
导出最近100条订单
```

系统会自动：
1. 根据描述生成 SELECT SQL
2. 执行查询获取数据
3. 写入 `.xlsx` 文件到 `Database_Data/` 目录
4. 返回导出结果（行数、列数、文件路径）

### 数据库结构探索

当数据库结构发生变化或首次连接时，可以使用：

```
探索一下数据库结构
更新 sql_agent 这个库的结构信息
```

系统会通过纯 Python 代码自动完成探索，无需 LLM 参与，速度快且准确。

## 上下文管理

### 会话持久化
每次 Agent 响应后，对话历史自动保存为 `Context/Data/<标题>.json`。

### 大内容卸载
工具返回内容超过 20KB 时，自动存储为独立文件 `Context/Data/<标题>/<tool_call_id>.txt`，消息中仅保留文件路径引用，避免上下文膨胀。

### 避免重复存储
当 LLM 调用 `read_file` 读取已持久化的数据时，返回结果会被自动清空，防止同一条数据在上下文中重复存储。

### 自动压缩机制
当上下文 tokens 数超过 `max_tokens * compression_threshold` 时，触发两级压缩：

1. **工具消息清理**：白名单外（`delete_file`、`input_sql` 以外）的工具调用 `args` 参数被清空，`content` 替换为占位文本
2. **全量压缩**：若工具清理后仍超出阈值，则保留近三轮完整对话，更早的对话交给 CompressionAgent 生成摘要，拼接到最早一轮用户消息中，随后再执行一次工具消息清理

## 技术栈

- **LangChain**：Agent 框架，提供 `create_agent` 和工具链
- **langchain-openai**：LLM 接口，通过 OpenAI 兼容协议接入 Deepseek
- **PyMySQL**：MySQL 数据库连接
- **openpyxl**：Excel (.xlsx) 文件读取与解析
- **python-dotenv**：环境变量管理
