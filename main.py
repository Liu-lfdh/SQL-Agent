import glob
import os

from Database_Data.Database import init_db, close_db
from Agent.MasterAgent import MasterAgent
from Context.MasterContext import MasterContext
from Context.message import message
from FunctionCalling.SkillGeneratorTool import set_current_context


def list_contexts() -> list[str]:
    data_dir = os.path.join(os.path.dirname(__file__), "Context", "Data")
    if not os.path.exists(data_dir):
        return []
    files = glob.glob(os.path.join(data_dir, "*.json"))
    return [os.path.splitext(os.path.basename(f))[0] for f in files]


def pick_context() -> str | None:
    contexts = list_contexts()
    if not contexts:
        return None
    print("\n已保存的上下文：")
    for i, name in enumerate(contexts):
        print(f"  {i + 1}. {name}")
    print(f"  0. 新建会话")
    while True:
        choice = input("请选择要加载的上下文编号（0 新建）: ")
        try:
            idx = int(choice)
            if idx == 0:
                return None
            if 1 <= idx <= len(contexts):
                return contexts[idx - 1]
        except ValueError:
            pass
        print("输入无效，请重新选择")


def load_or_create_context() -> MasterContext:
    name = pick_context()
    if name is None:
        return MasterContext([])
    ctx = MasterContext([])
    ctx.title = name
    data_dir = os.path.join(os.path.dirname(__file__), "Context", "Data")
    file_path = os.path.join(data_dir, name + ".json")
    ctx.loadMessage(file_path)
    print(f"已加载上下文: {name}\n")
    return ctx


def init_db_connection():
    print("正在连接数据库")
    try:
        init_db(
            host="192.168.200.130",
            port=3306,
            user="root",
            password="root"
        )
    except Exception:
        print("连接失败")
        return False
    print("连接成功\n")
    return True


def build_messages(context: MasterContext) -> list:
    messages = []
    for msg in context.data:
        msg_dict = {"role": msg.getRole(), "content": msg.getContent()}
        if msg.getRole() == "tool" and msg.getToolCallId():
            msg_dict["tool_call_id"] = msg.getToolCallId()
        if msg.getRole() == "ai" and msg.getToolCalls():
            msg_dict["tool_calls"] = msg.getToolCalls()
        messages.append(msg_dict)
    return messages


def save_result_messages(result: dict, context: MasterContext,userContent: str) -> None:
    context.addAllMessagesFromResult(result)
      


def chat_loop(agent, context: MasterContext) -> None:
    while True:
        content = input("user: ")
        if content == "exit":
            print("退出程序")
            break
        if not content.strip():
            continue
        context.addUserMessage(content)
        messages = build_messages(context)
        result = agent.invoke({"messages": messages})
        save_result_messages(result, context, content)
        context.saveMessage()
        print(f"assistant: {result.get('messages', [])[-1].content}")


def main():
    if not init_db_connection():
        return
    agent = MasterAgent().create_agent()
    context = load_or_create_context()
    # 将 context 设置为全局引用，供 SkillGeneratorTool 获取上下文文件路径
    set_current_context(context)
    # 将 agent 存储在 context 中，以便在需要时调用
    context.setAgent(agent)
    chat_loop(agent, context)


if __name__ == "__main__":
    try:
        main()
    finally:
        close_db()    