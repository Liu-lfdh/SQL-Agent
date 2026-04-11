import json
import os
import threading
import uuid
from .message import message

from Agent.TitleAgent import TitleAgent


class MasterContext:
    """管理对话上下文，支持消息的添加、持久化和加载"""

    data: list[message] = []
    title: str = ""

    # 持久化文件存储目录（相对于项目根目录）
    _DATA_DIR = os.path.join(os.path.dirname(__file__), "Data")
    _PERSISTED_DATA_PREFIX = "./Context/Data/"

    def __init__(self, data: list[message]):
        self.data = data

    # ==================== 消息添加 ====================

    def addUserMessage(self, content: str):
        """添加用户消息，首次添加时异步创建会话标题"""
        if self.title == "":
            threading.Thread(target=self._createTitle, args=(content,), daemon=True).start()
        self.addMessage(message("human", content))

    def addAllMessages(self, messages: list[message]):
        """批量添加消息"""
        for msg in messages:
            self.data.append(msg)

    def addMessage(self, msg: message):
        """添加单条消息，对 tool 类型消息进行持久化处理"""
        if msg.getRole() == "tool":
            self._handleToolMessage(msg)
        self.data.append(msg)

    # ==================== 持久化与加载 ====================

    def saveMessage(self):
        """将上下文数据持久化为 JSON 文件，文件名为会话标题"""
        if self.title == "":
            return
        os.makedirs(self._DATA_DIR, exist_ok=True)
        file_path = os.path.join(self._DATA_DIR, self.title + ".json")
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
        """从 JSON 文件加载上下文数据到内存"""
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

    # ==================== 内部方法 ====================

    def _createTitle(self, content: str):
        """在后台线程中通过 AI 生成会话标题"""
        agent = TitleAgent().create_agent()
        result = agent.invoke({"messages": [{"role": "user", "content": content}]})
        aiTitle = ""
        for msg in result.get("messages", []):
            if getattr(msg, 'type', None) == "ai":
                aiTitle = getattr(msg, "content", "")
                break
        self.title = aiTitle + uuid.uuid4().hex[:4]

    def _handleToolMessage(self, msg: message):
        """处理 tool 类型消息：检测是否读取持久化数据，或按需持久化"""
        if self._isReadingPersistedData():
            # LLM 正在读取已持久化的数据，清空结果避免重复存储
            msg.setContent("")
        elif len(msg.getContent().encode('utf-8')) > 20 * 1024:
            # 内容超过 20KB，将内容保存到文件并替换为文件路径
            file_path = self.saveToolMessage(msg)
            msg.setContent("工具信息过大，已被存储至该文件中：" + file_path)

    def _isReadingPersistedData(self) -> bool:
        """检查 LLM 最后一次调用是否使用了 read_file 工具读取持久化数据"""
        if not self.data:
            return False
        last_msg = self.data[-1]
        if last_msg.getRole() != "ai":
            return False
        for tc in last_msg.getToolCalls() or []:
            if tc.get("name") == "read_file":
                file_path = str(tc.get("args", {}).get("file_path", ""))
                if self._PERSISTED_DATA_PREFIX in file_path:
                    return True
        return False

    def saveToolMessage(self, msg: message) -> str:
        """将 tool 消息内容持久化为 txt 文件，返回相对文件路径"""
        tool_dir = os.path.join(self._DATA_DIR, self.title)
        os.makedirs(tool_dir, exist_ok=True)
        file_name = msg.getToolCallId() + ".txt"
        file_path = os.path.join(tool_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(msg.getContent())
        return f"{self._PERSISTED_DATA_PREFIX}{self.title}/{file_name}"
