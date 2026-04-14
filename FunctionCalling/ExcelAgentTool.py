from langchain_core.tools import tool

from Agent.ExcelAgent import ExcelAgent


@tool
def excel_agent_tool(content: str) -> str:
    """Excel数据导入子Agent，负责根据已确认的列映射将Excel文件数据批量插入到数据库表。

    注意：调用此工具时，content 中必须包含以下三项信息：
    1. Excel文件路径
    2. 目标数据库表名
    3. 已确认的列映射关系（Excel列名 → 数据库字段名），格式为：Excel列A→字段A, Excel列B→字段B...

    调用示例：
    - "将 ./test_data.xlsx 导入到 coupon_info 表，列映射为：优惠券类型→coupon_type, 优惠券名字→name, 金额→amount, 折扣→discount, 使用门槛→condition_amount, 发行数量→publish_count, 每人限领→per_limit, 已使用数量→use_count, 领取数量→receive_count, 过期时间→expire_time, 优惠券描述→description, 状态→status, 删除标记→is_deleted"

    如果用户尚未确认列映射关系，请不要调用此工具，应先完成映射确认流程。

    Args:
        content: 任务内容，必须包含Excel文件路径、目标表名和已确认的列映射关系。
    """
    print(f"[excel_agent_tool输入] {content}")
    agent = ExcelAgent().create_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": content}]})
    last_ai_content = None
    for msg in result.get("messages", []):
        msg_type = getattr(msg, 'type', None)
        content = getattr(msg, "content", None)
        if msg_type == 'ai':
            last_ai_content = content
    print(f"[excel_agent_tool输出] {last_ai_content}")
    return last_ai_content if last_ai_content is not None else "未找到AI响应"
