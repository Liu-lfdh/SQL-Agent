import sys
import os


from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from FunctionCalling.DatabaseTool import input_sql
from FunctionCalling.WriteFile import write_file
from FunctionCalling.ReadFile import read_file
from FunctionCalling.ListFiles import readList_command
from FunctionCalling.CreateFile import create_file
from Prompt.SqlPrompt import SqlPrompt
from Database_Data.Database import get_db_config

class SqlAgent:
    def create_agent(self):
        DeepseekLlm = ChatOpenAI(
            api_key="sk-ad872c810fdf4f2bb0dfb0e51115115f",
            base_url="https://api.deepseek.com",
            model="deepseek-chat")
        
        tools = [input_sql,read_file,readList_command]
        

        agent = create_agent(
            model=DeepseekLlm,
            tools=tools,
            system_prompt=SystemMessage(content="当前连接数据库信息：" + str(get_db_config()) + " " + SqlPrompt.getPrompt()),
            )
        return agent