from dotenv import load_dotenv
from langchain.agents import create_agent, AgentState
from langgraph.checkpoint.postgres import PostgresSaver
from langchain.tools import tool, ToolRuntime
from langchain_core.runnables import RunnableConfig

from langchain.messages import ToolMessage
from langgraph.types import Command
from pydantic import BaseModel
from langchain.agents.middleware import dynamic_prompt, ModelRequest
import os
from fastapi import Depends, FastAPI
from langgraph.store.postgres import PostgresStore



load_dotenv()


from langchain_core.callbacks.base import BaseCallbackHandler

class RunIdHandler(BaseCallbackHandler):
    def __init__(self):
        self.run_id = None

    def on_chain_start(self, serialized, inputs, run_id, **kwargs):
        self.run_id = run_id

handler = RunIdHandler()

agent = create_agent(
    "gpt-5-nano",
    system_prompt="You are a helpful assistant",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Hello"}]},
    config={"callbacks": [handler]},
)

print(handler.run_id)