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
