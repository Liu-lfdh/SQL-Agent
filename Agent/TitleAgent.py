import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from Llm.Deepseek import Deepseek
from langchain_openai import ChatOpenAI


class TitleAgent:
    def create_agent(self):
        agent = create_agent(
            model=Deepseek().getLlm(),
            system_prompt=SystemMessage(content="你需要为用户给出的消息，生成一个合适的标题，要求标题简洁明了控制在20个字符以内，能够概括消息的主要内容"),
        )
        return agent