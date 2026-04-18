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
