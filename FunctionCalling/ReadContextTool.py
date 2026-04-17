import json
import os
from langchain_core.tools import tool

_CONTEXT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Context/Data/"))


@tool
def read_context(context_file_path: str) -> str:
    """读取上下文持久化 JSON 文件，返回完整的消息历史（包含工具调用链路信息）。仅允许读取 Context/Data/ 目录下的 .json 文件。
    Args:
        context_file_path: 上下文 JSON 文件的路径（相对于 Context/Data/ 目录），例如 "导入数据1e70.json"
    """
    print(f"[read_context输入] 文件: {context_file_path}")

    if not context_file_path.endswith('.json'):
        result = "错误: 只允许读取 .json 文件"
        print(f"[read_context输出] {result}")
        return result

    full_path = os.path.normpath(os.path.join(_CONTEXT_DIR, context_file_path))
    if not full_path.startswith(_CONTEXT_DIR):
        result = "错误: 不允许读取 Context/Data 目录以外的文件"
        print(f"[read_context输出] {result}")
        return result

    if not os.path.exists(full_path):
        result = f"错误: 文件 {context_file_path} 不存在"
        print(f"[read_context输出] {result}")
        return result

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 构建包含工具调用链路的消息摘要
        messages = data.get("messages", [])
        output_lines = []
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            tool_calls = msg.get("tool_calls", "")
            tool_call_id = msg.get("tool_call_id", "")

            if role == "human":
                output_lines.append(f"[用户] {content}")
            elif role == "ai":
                ai_line = f"[AI] {content}" if content else "[AI]"
                if tool_calls:
                    for tc in tool_calls:
                        tc_name = tc.get("name", "")
                        tc_args = tc.get("args", {})
                        ai_line += f"\n  -> 调用工具: {tc_name}({tc_args})"
                output_lines.append(ai_line)
            elif role == "tool":
                # 工具结果，截断过长内容
                result_preview = content[:500] + "..." if len(content) > 500 else content
                output_lines.append(f"[工具结果 call_id={tool_call_id}] {result_preview}")

        result = "\n".join(output_lines)
        print(f"[read_context输出] 读取成功，共 {len(messages)} 条消息")
        return result
    except Exception as e:
        result = f"读取上下文文件失败: {str(e)}"
        print(f"[read_context输出] {result}")
        return result
