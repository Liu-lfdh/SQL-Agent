from langchain_openai import ChatOpenAI

class Deepseek:
    @staticmethod
    def getLlm():
        return ChatOpenAI(
            api_key="",
            base_url="https://api.deepseek.com",
            model="deepseek-chat")
