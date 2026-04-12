import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI


class TestAgent:
    def create_agent(self):
        llm = ChatOpenAI(
            api_key="",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen-plus-2025-07-28")


        agent = create_agent(
            model=llm,
            system_prompt=SystemMessage(content="你是一个友好的助手"),
        )
        return agent
