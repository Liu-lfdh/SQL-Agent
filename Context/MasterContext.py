import json
import os
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
        self.title = aiTitle + uuid.uuid4().hex[:4]

    def addAllMessages(self, messages: list[message]):
        for msg in messages:
            self.data.append(msg)

    def addMessage(self, message: message):
        if message.getRole() == "tool":
            byteCount = len(message.getContent().encode('utf-8'))
            if byteCount > 10:
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
        if self.title == "":
            return
        data_dir = os.path.join(os.path.dirname(__file__), "Data")
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, self.title + ".json")
        json_data = [
            {
                "role": msg.role,
                "content": msg.content,
                "tool_call_id": msg.tool_call_id,
                "tool_calls": msg.tool_calls
            }
            for msg in self.data
        ]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

    def loadMessage(self, filePath: str):
        with open(filePath, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        self.data = [
            message(
                role=item["role"],
                content=item["content"],
                tool_call_id=item.get("tool_call_id", ""),
                tool_calls=item.get("tool_calls", "")
            )
            for item in json_data
        ]

    def saveToolMessage(self, message: message) -> str:
        tool_dir = os.path.join(os.path.dirname(__file__), "Data", self.title)
        os.makedirs(tool_dir, exist_ok=True)
        file_name = message.getToolCallId() + ".txt"
        file_path = os.path.join(tool_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(message.getContent())
        return f"./Context/Data/{self.title}/{file_name}"    