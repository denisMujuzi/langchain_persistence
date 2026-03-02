from dotenv import load_dotenv
from langchain.agents import create_agent, AgentState
from langgraph.checkpoint.postgres import PostgresSaver
from langchain.tools import tool, ToolRuntime
from langchain_core.runnables import RunnableConfig

from langchain.messages import ToolMessage
from langgraph.types import Command
from pydantic import BaseModel
from langchain.agents.middleware import dynamic_prompt, ModelRequest


load_dotenv()

class CustomContext(BaseModel):
    user_name: str

class CustomAgentState(AgentState):  
    user_id: str
    preferences: dict


@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest[CustomContext]) -> str:
    user_name = request.runtime.context.user_name
    system_prompt = f"You are a helpful assistant. Address the user as {user_name}."
    return system_prompt


@tool
def get_user_info(
    runtime: ToolRuntime
) -> str:
    """Look up user info."""
    user_id = runtime.state["user_id"]
    return "User is John Smith" if user_id == "user_123" else "Unknown user"


config: RunnableConfig = {"configurable": {"thread_id": "six"}}
DB_URI = "postgresql://postgres:postgres@localhost:5432/langchain?sslmode=disable"
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup() # auto create tables in PostgresSql
    agent = create_agent(
        "gpt-5-nano",
        # tools=[get_user_info],
        state_schema=CustomAgentState,
        checkpointer=checkpointer,
        middleware=[dynamic_system_prompt],
        context_schema=CustomContext
    )
    
    # # Simulate a conversation
    # final_response = agent.invoke({
    #     "messages": "what's my name?", 
    #     "user_id": "user_123"}, 
    #     config
    # )
    
    # final_response["messages"][-1].pretty_print()

    final_response = agent.invoke(
        {"messages": "what's my name?"}, 
        config,
        context=CustomContext(user_name="Bob")
    )

    final_response["messages"][-1].pretty_print()