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
from FunctionCalling.DeleteFile import delete_file
from FunctionCalling.EnvironmentAgentTool import environment_agent_tool;
from FunctionCalling.SqlAgentTool import sql_agent_tool;
from Prompt.MasterPrompt import MasterPrompt
from Database_Data.Database import get_db_config

class MasterAgent:
    def create_agent(self):
        # DeepseekLlm = ChatOpenAI(
        #     api_key="sk-ead34420bd364abd896e0e7db1b5b4e2",
        #     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        #     model="qwen3.6-plus")
        DeepseekLlm = ChatOpenAI(
            api_key="sk-ad872c810fdf4f2bb0dfb0e51115115f",
            base_url="https://api.deepseek.com",
            model="deepseek-chat")
        
        tools = [input_sql, read_file, readList_command, environment_agent_tool, sql_agent_tool]
        

        agent = create_agent(
            model=DeepseekLlm,
            tools=tools,
            system_prompt=SystemMessage(content="当前连接数据库信息：" + str(get_db_config()) + " " + MasterPrompt.getPrompt()),
            )
        return agent