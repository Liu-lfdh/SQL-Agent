import sys
import os


from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from FunctionCalling.SqlWriterTool import sql_writer_tool
from FunctionCalling.SqlReviewerTool import sql_reviewer_tool
from FunctionCalling.ExplainTool import explain_sql
from FunctionCalling.ReadFile import read_file
from FunctionCalling.ListFiles import readList_command
from Prompt.BrainstormPrompt import BrainstormPrompt
from Llm.qwen import Qwen_3_6_Plus
from Database_Data.Database import get_db_config


MAX_DISCUSSION_ROUNDS = 3


class BrainstormAgent:
    def create_agent(self):
        tools = [sql_writer_tool, sql_reviewer_tool, explain_sql, read_file, readList_command]

        agent = create_agent(
            model=Qwen_3_6_Plus.getLlm(),
            tools=tools,
            system_prompt=SystemMessage(content="当前连接数据库信息：" + str(get_db_config()) + " " + BrainstormPrompt.getPrompt()),
        )
        return agent

    def execute(self, content: str) -> str:
        """执行头脑风暴讨论循环（代码级控制，最多MAX_DISCUSSION_ROUNDS轮）"""
        agent = self.create_agent()

        # 第一轮：Writer 生成 SQL
        print(f"[BrainstormAgent] 第1轮：Writer生成SQL")
        sql = sql_writer_tool.invoke({"content": content})
        print(f"[BrainstormAgent] Writer输出: {sql[:200]}...")

        # 讨论循环：最多3轮
        for round_num in range(1, MAX_DISCUSSION_ROUNDS + 1):
            print(f"[BrainstormAgent] 第{round_num}轮：Reviewer审查")
            review_input = f"原始需求：{content}\n待审查SQL：{sql}"
            review_result = sql_reviewer_tool.invoke({"content": review_input})
            print(f"[BrainstormAgent] Reviewer输出: {review_result[:200]}...")

            # 判断是否通过
            if review_result.strip().startswith("PASS"):
                print(f"[BrainstormAgent] 第{round_num}轮审查通过，输出最终SQL")
                return sql

            # 未通过，Writer 重写
            if round_num < MAX_DISCUSSION_ROUNDS:
                print(f"[BrainstormAgent] 第{round_num}轮审查未通过，Writer重写")
                rewrite_input = f"原始需求：{content}\n上一版SQL：{sql}\nReviewer修改意见：{review_result}"
                sql = sql_writer_tool.invoke({"content": rewrite_input})
                print(f"[BrainstormAgent] Writer重写: {sql[:200]}...")

        # 3轮后仍未通过，BrainstormAgent 裁决
        print(f"[BrainstormAgent] 3轮讨论结束仍未通过，BrainstormAgent裁决输出")
        return sql
