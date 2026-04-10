import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from FunctionCalling.DatabaseTool import input_sql
from FunctionCalling.WriteFile import write_file
from FunctionCalling.ReadFile import read_file
from FunctionCalling.ListFiles import readList_command
from FunctionCalling.CreateFile import create_file
from Prompt.EnvironmentPrompt import EnvironmentPrompt
from Database_Data.Database import get_db_config


class EnvironmentAgent:
    def create_agent(self):
        # llm = ChatOpenAI(
        #     api_key="sk-ead34420bd364abd896e0e7db1b5b4e2",
        #     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        #     model="qwen-plus-2025-07-28")
        
        DeepseekLlm = ChatOpenAI(
            api_key="sk-ad872c810fdf4f2bb0dfb0e51115115f",
            base_url="https://api.deepseek.com",
            model="deepseek-chat")

        tools = [input_sql, write_file, read_file, readList_command, create_file]

        agent = create_agent(
            model=DeepseekLlm,
            tools=tools,
            system_prompt=SystemMessage(content="当前连接数据库信息：" + str(get_db_config()) + " " + EnvironmentPrompt.getPrompt()),
        )
        return agent


# if __name__ == "__main__":
#     agent = EnvironmentAgent().create_agent()
#     result = agent.invoke({"messages": [{"role": "user", "content": "开始生成环境配置文件。"}]})
#     print("Agent执行结果:\n")
#     print(result)
