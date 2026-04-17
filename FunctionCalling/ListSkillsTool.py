from langchain_core.tools import tool

from Skill.skills import list_skills


@tool
def list_skills_tool() -> str:
    """动态获取当前所有可用的 Skill 列表。当需要查看最新可用 Skill 时调用此工具，返回的列表可能比系统提示词中的更完整（例如对话过程中新增了 Skill）。
    """
    print("[list_skills_tool输入] 查询最新 Skill 列表")
    skills = list_skills()
    if not skills:
        result = "当前没有可用的 Skill"
        print(f"[list_skills_tool输出] {result}")
        return result

    lines = ["当前可用 Skill："]
    for s in skills:
        lines.append(f"- {s['name']}: {s['description']}")
    result = "\n".join(lines)
    print(f"[list_skills_tool输出] 共 {len(skills)} 个 Skill")
    return result
