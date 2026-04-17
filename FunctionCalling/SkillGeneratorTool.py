import os
from langchain_core.tools import tool

from Agent.SkillGeneratorAgent import SkillGeneratorAgent

# 全局变量，由 main.py 设置，保存当前 MasterContext 实例
_current_context = None


def set_current_context(context):
    """设置当前 MasterContext 实例，供 skill_generator_tool 获取上下文文件路径"""
    global _current_context
    _current_context = context


def _get_context_file_path() -> str:
    """获取当前上下文持久化文件的相对路径"""
    if _current_context is None or not _current_context.title:
        return ""
    return _current_context.title + ".json"


@tool
def skill_generator_tool(content: str, workflow_scope: str) -> str:
    """Skill生成子Agent，从对话上下文中提炼可复用工作流并生成新的 Skill 文件。会自动读取当前会话的上下文历史（包含工具调用链路）。
    Args:
        content: 用户对要生成的 Skill 的需求描述，例如："将刚才的Excel导入流程保存为Skill" 或 "创建一个数据备份的工作流"
        workflow_scope: 工作流范围的描述，明确从哪里开始到哪里结束，例如："从用户要求导入Excel开始，到数据导入完成反馈结果结束"
    """
    context_file_path = _get_context_file_path()
    if not context_file_path:
        return "错误: 当前没有可用的上下文文件，无法提炼工作流"

    print(f"[skill_generator_tool输入] context: {context_file_path}, 需求: {content}, 范围: {workflow_scope}")

    agent = SkillGeneratorAgent().create_agent()
    task_message = (
        f"请根据以下信息生成一个新的 Skill：\n\n"
        f"用户需求：{content}\n\n"
        f"上下文文件路径：{context_file_path}\n\n"
        f"工作流范围：{workflow_scope}\n\n"
        f"请先使用 read_context 工具读取上下文文件，"
        f"根据「工作流范围」的描述，只提取从起点到终点之间的工具调用链路，"
        f"不要把范围之外的对话内容纳入工作流。"
        f"然后提炼出可复用的工作流，生成 Skill 文件并保存。"
    )

    result = agent.invoke({"messages": [{"role": "user", "content": task_message}]})

    last_ai_content = None
    for msg in result.get("messages", []):
        msg_type = getattr(msg, 'type', None)
        msg_content = getattr(msg, "content", None)
        if msg_type == 'ai':
            last_ai_content = msg_content

    print(f"[skill_generator_tool输出] {last_ai_content}")
    return last_ai_content if last_ai_content is not None else "Skill 生成失败：未获取到AI响应"
