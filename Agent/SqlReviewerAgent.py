import sys
import os


from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from FunctionCalling.ExplainTool import explain_sql
from FunctionCalling.ReadFile import read_file
from FunctionCalling.ListFiles import readList_command
from Prompt.SqlReviewerPrompt import SqlReviewerPrompt
from Llm.qwen import Qwen_3_6_Plus
from Database_Data.Database import get_db_config


class SqlReviewerAgent:
    def create_agent(self):
        tools = [explain_sql, read_file, readList_command]

        agent = create_agent(
            model=Qwen_3_6_Plus.getLlm(),
            tools=tools,
            system_prompt=SystemMessage(content="当前连接数据库信息：" + str(get_db_config()) + " " + SqlReviewerPrompt.getPrompt()),
        )
        return agent
