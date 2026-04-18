from langchain_core.tools import tool

from Agent.BrainstormAgent import BrainstormAgent


@tool
def brainstorm_agent_tool(content: str) -> str:
    """Brainstorm子Agent，通过多Agent头脑风暴机制（Writer+Reviewer讨论）生成复杂SQL。
    Args:
        content: 复杂查询需求描述，包含涉及的数据库表、查询逻辑等;
    """
    print(f"[brainstorm_agent_tool输入] {content}")
    agent = BrainstormAgent()
    result = agent.execute(content)
    print(f"[brainstorm_agent_tool输出] {result}")
    return result if result is not None else "未找到AI响应"
