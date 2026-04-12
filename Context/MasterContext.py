import json
import os
import threading
import uuid
from .message import message

from Agent.TitleAgent import TitleAgent
from Prompt.CompressionPrompt import CompressionPrompt


class MasterContext:
    """管理对话上下文，支持消息的添加、持久化和加载"""

    data: list[message] = []
    title: str = ""

    max_tokens: int
    compression_threshold: float
    now_tokens: int = 0
    agent = None

    # 持久化文件存储目录（相对于项目根目录）
    _DATA_DIR = os.path.join(os.path.dirname(__file__), "Data")
    _PERSISTED_DATA_PREFIX = "./Context/Data/"

    def __init__(self, data: list[message], max_tokens: int = 100 * 1024, compression_threshold: float = 0.85):
        self.data = data
        # 未定义max_tokens时默认为100KB，单位为字节，实际使用中可根据需要调整
        self.max_tokens = max_tokens
        # 压缩阈值表示当上下文总 tokens 数超过 max_tokens 的多少比例时触发压缩，默认为 0.85 即 85%
        self.compression_threshold = compression_threshold
        self.now_tokens = 0

    def setAgent(self, agent):
        self.agent = agent   

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

    def addAllMessagesFromResult(self, result: dict):
        """从 LLM 调用结果中批量添加消息"""
        userContent = self.getLastUserContent()
        isNewMessage = False
        for msg in result.get("messages", []):
            if isNewMessage == True:
                self.addMessage(message(
                    msg.type,
                    msg.content,
                    getattr(msg, "tool_call_id", ""),
                    getattr(msg, "tool_calls", "")
                ))
            elif msg.type == "human" and msg.content == userContent:
                isNewMessage = True   
        # 当超出阈值后触发压缩机制  
        if self.now_tokens / self.max_tokens > self.compression_threshold:  
            self.clearToolMessages()             

    def addMessage(self, msg: message):
        """添加单条消息，对 tool 类型消息进行持久化处理"""
        if msg.getRole() == "tool":
            self._handleToolMessage(msg)
        # 计算消息内容的大小  
        msg_len = len(msg)
        self.now_tokens += msg_len
        self.data.append(msg)

    # ==================== 持久化与加载 ====================

    def saveMessage(self):
        """将上下文数据持久化为 JSON 文件，文件名为会话标题"""
        if self.title == "":
            return
        os.makedirs(self._DATA_DIR, exist_ok=True)
        file_path = os.path.join(self._DATA_DIR, self.title + ".json")
        json_data = {
            "title": self.title,
            "max_tokens": self.max_tokens,
            "compression_threshold": self.compression_threshold,
            "now_tokens": self.now_tokens,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "tool_call_id": msg.tool_call_id,
                    "tool_calls": msg.tool_calls
                }
                for msg in self.data
            ]
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

    def loadMessage(self, filePath: str):
        """从 JSON 文件加载上下文数据到内存"""
        with open(filePath, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        self.title = json_data.get("title", "")
        self.max_tokens = json_data.get("max_tokens", self.max_tokens)
        self.compression_threshold = json_data.get("compression_threshold", self.compression_threshold)
        self.now_tokens = json_data.get("now_tokens", 0)
        self.data = [
            message(
                role=item["role"],
                content=item["content"],
                tool_call_id=item.get("tool_call_id", ""),
                tool_calls=item.get("tool_calls", "")
            )
            for item in json_data["messages"]
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
    
    def getLastUserContent(self) -> str:
        """获取上下文中最后一条用户消息的内容"""
        for i in range(1, len(self.data) + 1):
            msg = self.data[-i]
            if msg.getRole() == "human":
                return msg.getContent() 
        return ""
    
    def clearToolMessages(self):
        """"清理上下文中的 tool 消息，释放存储空间"""
        # 清理 白名单外的 工具信息
        TOOL_WHITELIST: set[str] = {"delete_file", "input_sql"}

        # 构建 tool_call_id -> tool_name 映射，标记非白名单工具
        non_whitelisted_ids: set[str] = set()
        for msg in self.data:
            if msg.getRole() == "ai":
                for tc in msg.getToolCalls() or []:
                    tc_id = tc.get("id", "")
                    tc_name = tc.get("name", "")
                    if tc_id and tc_name and tc_name not in TOOL_WHITELIST:
                        non_whitelisted_ids.add(tc_id)

        # 新建数组，保留所有消息，仅清理非白名单工具的 args 和 content
        cleaned_data: list[message] = []
        for msg in self.data:
            if msg.getRole() == "ai" and msg.getToolCalls():
                # 复制消息，去掉非白名单工具调用的 args 参数
                new_tool_calls = []
                for tc in msg.getToolCalls():
                    new_tc = dict(tc)
                    if tc.get("id") in non_whitelisted_ids:
                        new_tc["args"] = {}
                    new_tool_calls.append(new_tc)
                cleaned_data.append(message(msg.getRole(), msg.getContent(), msg.getToolCallId(), new_tool_calls))
            elif msg.getRole() == "tool":
                if msg.getToolCallId() in non_whitelisted_ids:
                    # 非白名单工具：content 替换为占位文本
                    cleaned_data.append(message(msg.getRole(), "工具已经成功调用，相关信息已被清理", msg.getToolCallId(), ""))
                else:
                    cleaned_data.append(msg)
            else:
                cleaned_data.append(msg)

        # 重新计算 tokens 数
        new_tokens = sum(len(m) for m in cleaned_data)

        if new_tokens / self.max_tokens <= self.compression_threshold:
            # 压缩到阈值以下，替换 data
            self.data = cleaned_data
            self.now_tokens = new_tokens
        else:
            # 仅清理 tool 消息仍超出阈值，执行全量压缩
            self.fullCompress()

    def fullCompress(self):
        """全量压缩：保留近三轮对话，将更早的对话交给压缩Agent摘要后拼接到最早一轮user消息中"""
        print("正在压缩上下文以释放空间...")
        # 按轮次拆分：一轮 = 从 human 消息开始到下一条 human 消息之前
        rounds: list[list[message]] = []
        current_round: list[message] = []
        for msg in self.data:
            if msg.getRole() == "human" and current_round:
                rounds.append(current_round)
                current_round = []
            current_round.append(msg)
        if current_round:
            rounds.append(current_round)

        # 保留近三轮，其余交给压缩Agent
        keep_rounds = rounds[-3:]
        compress_rounds = rounds[:-3]
        if not compress_rounds:
            return

        # 构建压缩Agent的输入消息
        messages = []
        for r in compress_rounds:
            for msg in r:
                msg_dict = {"role": msg.getRole(), "content": msg.getContent()}
                if msg.getRole() == "tool" and msg.getToolCallId():
                    msg_dict["tool_call_id"] = msg.getToolCallId()
                if msg.getRole() == "ai" and msg.getToolCalls():
                    msg_dict["tool_calls"] = msg.getToolCalls()
                messages.append(msg_dict)
        messages.append({"role": "user", "content": CompressionPrompt.getPrompt()})
        result = self.agent.invoke({"messages": messages})

        # 提取最后一个 message 的 content 作为摘要
        summary = ""
        for msg in result.get("messages", []):
            content = getattr(msg, "content", "") or ""
            if content:
                summary = content

        if not summary:
            return

        # 将摘要拼接到最早一轮 keep_rounds 中 human 的 content 前面
        first_human_msg = keep_rounds[0][0]  # 每轮第一条就是 human
        original_content = first_human_msg.getContent()
        first_human_msg.setContent(f"前情摘要：\n{summary}\n\nuser: {original_content}")

        # 用保留的轮次替换 data
        self.data = [msg for r in keep_rounds for msg in r]
        self.now_tokens = sum(len(m) for m in self.data)

        # 对保留的近三轮也执行一次工具消息压缩
        self.clearToolMessages()

