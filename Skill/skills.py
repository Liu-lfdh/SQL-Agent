import os
import re

_SKILLS_DIR = os.path.dirname(os.path.abspath(__file__))

def _parse_frontmatter(filepath):
    """解析 MD 文件的 YAML frontmatter，返回 {name, description, file}"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return None
    meta = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            meta[key.strip()] = value.strip()
    if 'name' not in meta or 'description' not in meta:
        return None
    meta['file'] = os.path.relpath(filepath, _SKILLS_DIR)
    return meta


def list_skills():
    """扫描 Skill 目录下所有 .md 文件，返回 skill 元数据列表"""
    skills = []
    for name in sorted(os.listdir(_SKILLS_DIR)):
        if name.endswith('.md'):
            filepath = os.path.join(_SKILLS_DIR, name)
            meta = _parse_frontmatter(filepath)
            if meta:
                skills.append(meta)
    return skills


def get_skill_prompt():
    """生成可用 Skill 列表提示，供 MasterAgent 系统提示词使用"""
    skills = list_skills()
    if not skills:
        return ""
    lines = ["可用 Skill："]
    for s in skills:
        lines.append(f"- {s['name']}: {s['description']}")
    lines.append("\n当用户需求匹配某个 Skill 时，请先读取对应 Skill 文件了解完整工作流程，然后按步骤执行。")
    return "\n".join(lines)


if __name__ == '__main__':
    print(get_skill_prompt())
