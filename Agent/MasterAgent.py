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
from FunctionCalling.SchemaDiscoveryTool import discover_schema
from FunctionCalling.SqlAgentTool import sql_agent_tool;
from FunctionCalling.ExcelAgentTool import excel_agent_tool
from FunctionCalling.ExcelReaderTool import excel_reader
from FunctionCalling.ReadSkill import read_skill
from FunctionCalling.ExcelWriterTool import excel_writer
from FunctionCalling.ExcelImportTool import excel_import
from FunctionCalling.ExcelExportTool import excel_export
from Prompt.MasterPrompt import MasterPrompt
from Llm.Deepseek import Deepseek
from Database_Data.Database import get_db_config
from Skill.skills import get_skill_prompt

class MasterAgent:
    def create_agent(self):
        tools = [input_sql, read_file, readList_command, discover_schema, sql_agent_tool, excel_agent_tool, excel_reader, read_skill, excel_writer, excel_import, excel_export]

        agent = create_agent(
            model=Deepseek().getLlm(),
            tools=tools,
            system_prompt=SystemMessage(content="当前连接数据库信息：" + str(get_db_config()) + " " + MasterPrompt.getPrompt() + "\n" + get_skill_prompt()),
            )
        return agent