from langchain_core.tools import tool

from Agent.SqlAgent import SqlAgent


@tool
def sql_agent_tool(content: str) -> str:
    """SQL子Agent，整理用户需求，将任务准确描述给该agent用于生成SQL语句，会返回生成的sql语句。
    Args:
        content: 任务内容;(你需要指定database) 例：请帮我查询sql_agent这个database中user表的所有数据；
    """
    print(f"[sql_agent_tool输入] {content}")
    agent = SqlAgent().create_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": content}]})
    last_ai_content = None
    for msg in result.get("messages", []):
        msg_type = getattr(msg, 'type', None)
        content = getattr(msg, "content", None)
        if msg_type == 'ai':
            last_ai_content = content
    print(f"[sql_agent_tool输出] {last_ai_content}")
    return last_ai_content if last_ai_content is not None else "未找到AI响应"
