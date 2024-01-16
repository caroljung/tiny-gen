import logging
from enum import Enum
from openai import AsyncOpenAI, AsyncStream
from ..utils.prompts import *

GPT_MODEL = "gpt-4-1106-preview"

class Role(str, Enum):
    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'

class GptClient:
  def __init__(self):
    self.messages = []
    self.client = AsyncOpenAI()

  async def prompt(self):
    return await self.client.chat.completions.create(
          model=GPT_MODEL,
          messages=self.messages,
          stream = True,
      )

  async def get_unified_diff(self, repo_content, prompt):
      self.messages.clear()
      self.messages.append({"role": Role.SYSTEM, "content": PRIMER})
      self.messages.append({"role": Role.USER, "content": GENERATE_DIFF.format(repo_content, prompt)})
      return await self.prompt()

  async def reflect(self):
      self.messages.append({"role": Role.USER, "content": REFLECT})
      return await self.prompt()
      
  def save_response(self, content):
      self.messages.append({"role": Role.ASSISTANT, "content": content})
