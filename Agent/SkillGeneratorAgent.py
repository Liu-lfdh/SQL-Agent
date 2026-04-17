import sys
import os

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage

from FunctionCalling.ReadContextTool import read_context
from FunctionCalling.ReadSkill import read_skill
from FunctionCalling.WriteSkillTool import write_skill
from Prompt.SkillGeneratorPrompt import SkillGeneratorPrompt
from Llm.Deepseek import Deepseek


class SkillGeneratorAgent:
    def create_agent(self):
        tools = [read_context, read_skill, write_skill]

        agent = create_agent(
            model=Deepseek().getLlm(),
            tools=tools,
            system_prompt=SystemMessage(content=SkillGeneratorPrompt.getPrompt()),
        )
        return agent
