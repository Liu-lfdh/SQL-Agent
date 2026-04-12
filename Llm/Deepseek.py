from langchain_openai import ChatOpenAI

class Deepseek:
    @staticmethod
    def getLlm():
        return ChatOpenAI(
            api_key="Your key",
            base_url="https://api.deepseek.com",
            model="deepseek-chat")