from langchain_openai import ChatOpenAI
class QwenPlus20250728:
    @staticmethod
    def getLlm():
        return ChatOpenAI(
            api_key="sk-ead34420bd364abd896e0e7db1b5b4e2",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen-plus-2025-07-28")