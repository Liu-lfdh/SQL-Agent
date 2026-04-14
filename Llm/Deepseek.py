from langchain_openai import ChatOpenAI

class Deepseek:
    @staticmethod
    def getLlm():
        return ChatOpenAI(
            api_key="sk-ad872c810fdf4f2bb0dfb0e51115115f",
            base_url="https://api.deepseek.com",
            model="deepseek-chat")
