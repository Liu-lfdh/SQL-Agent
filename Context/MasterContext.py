import threading
import uuid
from .message import message

from Agent.TitleAgent import TitleAgent


class MasterContext:

    data: list[message] = []
    title: str = ""

    def __init__(self, data: list[message]):
        self.data = data


    def _createTitle(self, content: str):
        # 在后台线程中执行创建标题的任务，避免阻塞主线程
        agent = TitleAgent().create_agent()
        result = agent.invoke({"messages": [{"role": "user", "content": content}]})
        aiTitle = ""
        for msg in result.get("messages", []):
                msg_type = getattr(msg, 'type', None)
                msg_content = getattr(msg, "content", None)
                if msg_type == "ai":
                    aiTitle = msg_content
                    break
        self.title = aiTitle + uuid.uuid4().hex

    def addAllMessages(self, messages: list[message]):
        for msg in messages:
            self.data.append(msg)

    def addMessage(self, message: message):
        if message.getRole() == "tool":
            byteCount = len(message.getContent().encode('utf-8'))
            if byteCount > 20 * 1024:
                # 如果消息内容超过20KB，则进行持久化
                filePath = self.saveToolMessage(message)
                # 将持久化后的文件路径作为新的消息内容
                message.setContent("工具信息过大，已被存储至该文件中：" + filePath)       
        self.data.append(message)

    def addUserMessage(self, content: str):
        if self.title == "":
            threading.Thread(target=self._createTitle, args=(content,), daemon=True).start()
        self.addMessage(message("human", content))     

    def saveMessage(self):
        # 将data数据持久化到硬盘中    
        print("持久化消息数据到硬盘中")

    def saveToolMessage(self, message: message) -> str:
        # 将tool类型的消息持久化到硬盘中，并返回持久化后的文件路径
        return "持久化后的文件路径"    
    
    def toString(self) -> str:
        # 将当前上下文中的消息数据转换为字符串形式，供LLM模型使用
        result = ""
        for msg in self.data:
            result += f"{msg.getRole()}: {msg.getContent()}\n"
        return result