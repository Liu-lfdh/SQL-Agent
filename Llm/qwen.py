from langchain_openai import ChatOpenAI
import os
class Qwen_3_6_Plus:
    @staticmethod
    def getLlm():
        return ChatOpenAI(
            api_key=os.getenv("ALI_QWEN_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen3.6-plus")
