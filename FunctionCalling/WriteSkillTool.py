import os
from langchain_core.tools import tool

_SKILLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Skill/"))


@tool
def write_skill(skill_name: str, content: str) -> str:
    """将生成的 Skill 内容写入 .md 文件。仅允许在 Skill/ 目录下创建新的 .md 文件，不允许覆盖已有文件。
    Args:
        skill_name: Skill 文件名，必须以 .md 结尾，例如 "data-backup.md"
        content: 完整的 Skill Markdown 内容（包含 frontmatter 和正文）
    """
    print(f"[write_skill输入] skill_name: {skill_name}, 内容长度: {len(content)} 字符")

    if not skill_name.endswith('.md'):
        result = "错误: Skill 文件必须以 .md 结尾"
        print(f"[write_skill输出] {result}")
        return result

    full_path = os.path.normpath(os.path.join(_SKILLS_DIR, skill_name))
    if not full_path.startswith(_SKILLS_DIR):
        result = "错误: 不允许写入 Skill 目录以外的文件"
        print(f"[write_skill输出] {result}")
        return result

    if os.path.exists(full_path):
        result = f"错误: 文件 {skill_name} 已存在，不允许覆盖已有 Skill"
        print(f"[write_skill输出] {result}")
        return result

    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        result = f"Skill 文件创建成功: {skill_name}"
        print(f"[write_skill输出] {result}")
        return result
    except Exception as e:
        result = f"创建 Skill 文件失败: {str(e)}"
        print(f"[write_skill输出] {result}")
        return result
