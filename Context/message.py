class message:
    role: str = ""
    content: str = ""
    tool_call_id: str = ""
    tool_calls: str = ""

    def __init__(self, role: str, content: str, tool_call_id: str = "", tool_calls: str = ""):
        self.role = role
        self.content = content
        self.tool_call_id = tool_call_id
        self.tool_calls = tool_calls

    def getRole(self):
        return self.role

    def getContent(self):
        return self.content

    def getToolCallId(self):
        return self.tool_call_id

    def getToolCalls(self):
        return self.tool_calls

    def setRole(self, role: str):
        self.role = role

    def setContent(self, content: str):
        self.content = content