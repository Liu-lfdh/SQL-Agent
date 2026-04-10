import os
from langchain_core.tools import tool

from Agent.EnvironmentAgent import EnvironmentAgent

@tool
def environment_agent_tool(content: str) -> str:
    """向环境构建子Agent下达指令，生成环境配置文件
    Args:
        content: 指令内容，指令中需要明确告知该子Agent应该去为mysql下哪一个database生成环境配置文件，例：开始初始化sql_agent这个database的环境信息；
    """
    print(f"[environment_agent_tool输入] {content}")
    agent = EnvironmentAgent().create_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": content}]})
    last_ai_content = None
    for msg in result.get("messages", []):
        msg_type = getattr(msg, 'type', None)
        content = getattr(msg, "content", None)
        if msg_type == 'ai':
            last_ai_content = content
    print(f"[environment_agent_tool输出] {last_ai_content}")        
    return last_ai_content if last_ai_content is not None else "未找到AI响应"

