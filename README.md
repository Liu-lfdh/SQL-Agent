# SQL-Agent

基于 Windows 操作系统的 MySQL 数据库智能 Agent，采用多 Agent 架构，支持自然语言对话式的 SQL 查询生成、执行和数据库结构探索。

## 功能特性

- **自然语言查询**：用自然语言描述需求，Agent 自动生成并执行对应 SQL
- **数据库结构探索**：自动发现数据库表结构、字段信息、索引等元数据
- **多 Agent 协作**：主控 Agent 根据任务类型智能路由到专用子 Agent
- **上下文持久化**：对话历史自动保存为 JSON，支持跨会话恢复
- **SQL 安全保护**：危险操作（DELETE/UPDATE/DROP 等）执行前需手动确认
- **大内容自动卸载**：超过 20KB 的工具输出自动存储为独立文件，避免上下文膨胀

## 项目结构

```
SQL-Agent/
├── main.py                      # 程序入口，数据库配置，对话循环
│
├── Agent/                       # Agent 定义
│   ├── MasterAgent.py           # 主控 Agent，负责任务路由
│   ├── SqlAgent.py              # SQL 生成专家 Agent
│   ├── EnvironmentAgent.py      # 数据库结构探索 Agent
│   ├── TitleAgent.py            # 会话标题生成 Agent
│   └── TestAgent.py             # 测试用 Agent
│
├── FunctionCalling/             # 工具函数
│   ├── DatabaseTool.py          # SQL 执行工具 (input_sql)
│   ├── ReadFile.py              # 文件读取工具 (read_file)
│   ├── ListFiles.py             # 目录列表工具 (readList_command)
│   ├── WriteFile.py             # 文件写入工具 (write_file)
│   ├── CreateFile.py            # 文件创建工具 (create_file)
│   ├── DeleteFile.py            # 文件删除工具 (delete_file)
│   ├── EnvironmentAgentTool.py  # EnvironmentAgent 调用工具
│   └── SqlAgentTool.py          # SqlAgent 调用工具
│
├── Prompt/                      # 系统提示词
│   ├── MasterPrompt.py          # MasterAgent 提示词
│   ├── SqlPrompt.py             # SqlAgent 提示词
│   └── EnvironmentPrompt.py     # EnvironmentAgent 提示词
│
├── Context/                     # 上下文管理
│   ├── MasterContext.py         # 上下文管理器（持久化/加载）
│   └── message.py               # 消息数据模型
│
├── Database_Data/               # 数据库结构缓存目录
│   └── Database.py              # MySQL 连接层
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
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
+----------------+  +----------------+  +---------------+
| environment_   |  |    sql_agent   |  | 内置工具       |
| agent_tool     |  |    tool        |  | input_sql     |
+----------------+  +----------------+  | read_file     |
        |                   |          | readList      |
        v                   v          +---------------+
+----------------+  +----------------+
|EnvironmentAgent|  |   SqlAgent     |
| (Deepseek)     |  | (Deepseek)     |
+----------------+  +----------------+
        |                   |
        v                   v
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
主控 Agent，负责任务识别和路由。不直接生成 SQL 或执行查询，而是根据用户意图将任务委派给专用子 Agent。

### SqlAgent
SQL 生成专家。接收任务描述和数据库结构信息，生成对应的 SQL 查询语句。

### EnvironmentAgent
数据库结构探索专家。连接 MySQL 数据库，查询库、表、字段、索引等元数据，并将结构信息缓存到 `Database_Data/` 目录。

### TitleAgent
会话标题生成器。根据用户的第一条消息自动生成简洁的会话标题（20 字符以内）。

## 工具说明

| 工具 | 功能 |
|------|------|
| `input_sql` | 执行 SQL 查询，危险操作需确认 |
| `read_file` | 读取项目根目录下的文件 |
| `readList_command` | 列出目录内容 |
| `write_file` | 写入文件到 `Database_Data/` |
| `create_file` | 创建 `.txt` 文件到 `Database_Data/` |
| `delete_file` | 删除 `Database_Data/` 中的文件 |
| `environment_agent_tool` | 调用 EnvironmentAgent 进行数据库结构探索 |
| `sql_agent_tool` | 调用 SqlAgent 进行 SQL 生成 |

## 快速开始

### 环境要求

- Python 3.x
- MySQL 数据库

### 安装依赖

```bash
pip install pymysql langchain langchain-openai
```

### 配置数据库

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

## 上下文管理

### 会话持久化
每次 Agent 响应后，对话历史自动保存为 `Context/Data/<标题>.json`。

### 大内容卸载
工具返回内容超过 20KB 时，自动存储为独立文件 `Context/Data/<标题>/<tool_call_id>.txt`，消息中仅保留文件路径引用，避免上下文膨胀。

### 避免重复存储
当 LLM 调用 `read_file` 读取已持久化的数据时，返回结果会被自动清空，防止同一条数据在上下文中重复存储。

## 技术栈

- **LangChain**：Agent 框架，提供 `create_agent` 和工具链
- **langchain-openai**：LLM 接口，通过 OpenAI 兼容协议接入 Deepseek
- **PyMySQL**：MySQL 数据库连接
