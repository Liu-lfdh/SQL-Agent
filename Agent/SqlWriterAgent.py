import sys
import os


from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from FunctionCalling.DatabaseTool import input_sql
from FunctionCalling.ReadFile import read_file
from FunctionCalling.ListFiles import readList_command
from Prompt.SqlWriterPrompt import SqlWriterPrompt
from Llm.Deepseek import Deepseek
from Database_Data.Database import get_db_config


class SqlWriterAgent:
    def create_agent(self):
        tools = [input_sql, read_file, readList_command]

        agent = create_agent(
            model=Deepseek().getLlm(),
            tools=tools,
            system_prompt=SystemMessage(content="当前连接数据库信息：" + str(get_db_config()) + " " + SqlWriterPrompt.getPrompt()),
        )
        return agent
