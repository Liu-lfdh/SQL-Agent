from Database_Data.Database import init_db, execute_sql, close_db
from Agent.EnvironmentAgent import EnvironmentAgent
from Agent.SqlAgent import SqlAgent
from Agent.TestAgent import TestAgent
from Agent.MasterAgent import MasterAgent
from Context.MasterContext import MasterContext
from Context.message import message

def main():
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
        return
    print("连接成功\n")

if __name__ == "__main__":
    try:
        main()
        agent = MasterAgent().create_agent()
        content = ""
        context = MasterContext([])
        while(True):
            content = input("user: ")
            if content == "exit":
                print("退出程序")
                break
            context.addUserMessage(content)
            # 构建消息列表，保留 tool_call_id 和 tool_calls
            messages = []
            for msg in context.data:
                msg_dict = {"role": msg.getRole(), "content": msg.getContent()}
                if msg.getRole() == "tool" and msg.getToolCallId():
                    msg_dict["tool_call_id"] = msg.getToolCallId()
                if msg.getRole() == "ai" and msg.getToolCalls():
                    msg_dict["tool_calls"] = msg.getToolCalls()
                messages.append(msg_dict)
            result = agent.invoke({"messages": messages})
            print("Agent 执行结果:\n")
            newMessage = False
            for msg in result.get("messages", []):
                msg_type = getattr(msg, 'type', None)
                msg_Content = getattr(msg, "content", None)
                msg_tool_call_id = getattr(msg, "tool_call_id", "")
                msg_tool_calls = getattr(msg, "tool_calls", "")
                if newMessage == True:
                    print(f"[type]: {msg_type}")
                    print(f"[content]: {msg_Content}")
                    context.addMessage(message(msg_type, msg_Content, msg_tool_call_id, msg_tool_calls))
                    print("---")
                elif msg_type == "human" and msg_Content == content:
                    newMessage = True
    finally:
        close_db()    