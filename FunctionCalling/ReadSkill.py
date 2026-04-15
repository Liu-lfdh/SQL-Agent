import os
from langchain_core.tools import tool

_SKILLS_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../Skill/"


@tool
def read_skill(skill_name: str) -> str:
    """读取指定名称的 Skill 工作流程文件。根据 skill 名称（name 字段）在 Skill/ 目录下查找对应的 .md 文件并返回完整内容。
    Args:
        skill_name: Skill 的名称，对应 Skill 文件中 frontmatter 的 name 字段，例如 "excel-import"
    """
    print(f"[read_skill输入] skill: {skill_name}")

    skills_dir = os.path.abspath(_SKILLS_DIR)
    for name in os.listdir(skills_dir):
        if name.endswith('.md'):
            filepath = os.path.join(skills_dir, name)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            # 从 frontmatter 中提取 name 字段进行匹配
            import re
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if match:
                for line in match.group(1).split('\n'):
                    if ':' in line:
                        key, _, value = line.partition(':')
                        if key.strip() == 'name' and value.strip() == skill_name:
                            result = f"已找到 Skill '{skill_name}' ({name}):\n\n{content}"
                            print(f"[read_skill输出] 成功读取 Skill: {name}")
                            return result

    result = f"错误: 未找到名称为 '{skill_name}' 的 Skill。可用 Skill: {', '.join(_list_skill_names())}"
    print(f"[read_skill输出] {result}")
    return result


def _list_skill_names():
    """列出所有可用 Skill 的 name"""
    import re
    skills_dir = os.path.abspath(_SKILLS_DIR)
    names = []
    for name in os.listdir(skills_dir):
        if name.endswith('.md'):
            filepath = os.path.join(skills_dir, name)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if match:
                for line in match.group(1).split('\n'):
                    if ':' in line:
                        key, _, value = line.partition(':')
                        if key.strip() == 'name':
                            names.append(value.strip())
    return names
