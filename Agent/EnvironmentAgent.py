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
from FunctionCalling.DeleteFile import delete_file
from Prompt.EnvironmentPrompt import EnvironmentPrompt
from Llm.Deepseek import Deepseek
from Database_Data.Database import get_db_config


class EnvironmentAgent:
    def create_agent(self):
        tools = [input_sql, write_file, read_file, readList_command, create_file, delete_file]

        agent = create_agent(
            model=Deepseek().getLlm(),
            tools=tools,
            system_prompt=SystemMessage(content="当前连接数据库信息：" + str(get_db_config()) + " " + EnvironmentPrompt.getPrompt()),
        )
        return agent

