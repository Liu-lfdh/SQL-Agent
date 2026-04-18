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
