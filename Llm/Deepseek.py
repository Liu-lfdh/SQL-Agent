from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

class Deepseek:
    @staticmethod
    def getLlm():
        return ChatOpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
            model="deepseek-chat")
