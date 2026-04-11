import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI


class TitleAgent:
    def create_agent(self):
        DeepseekLlm = ChatOpenAI(
            api_key="sk-ad872c810fdf4f2bb0dfb0e51115115f",
            base_url="https://api.deepseek.com",
            model="deepseek-chat")


        agent = create_agent(
            model=DeepseekLlm,
            system_prompt=SystemMessage(content="你需要为用户给出的消息，生成一个合适的标题，要求标题简洁明了控制在20个字符以内，能够概括消息的主要内容"),
        )
        return agent