import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage

from FunctionCalling.ExcelReaderTool import excel_reader
from FunctionCalling.DatabaseTool import input_sql
from Prompt.ExcelPrompt import ExcelPrompt
from Llm.Deepseek import Deepseek
from Database_Data.Database import get_db_config


class ExcelAgent:
    def create_agent(self):
        tools = [excel_reader, input_sql]

        agent = create_agent(
            model=Deepseek().getLlm(),
            tools=tools,
            system_prompt=SystemMessage(
                content="当前连接数据库信息：" + str(get_db_config()) + " " + ExcelPrompt.getPrompt()
            ),
        )
        return agent
