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
import uuid


load_dotenv()

def get_memories_standalone(user_phone: str = "256700000000") -> str:
    """Standalone function to get memories without FastAPI dependency injection."""
    with PostgresStore.from_conn_string(os.environ["DB_URI"]) as store:
        store.setup()
        memories = store.search(("memories",user_phone))
        user_memories = ""

        for memory in memories:
            user_memories += f"-(key: {memory.key}, content: {memory.value['content']})\n"

        return user_memories


class CustomContext(BaseModel):
    user_phone: str = "256700000000"
    user_name: str = "John Doe"


system_prompt = """You are a helpful assistant with memory capabilities.

MEMORY GUIDELINES:
When you learn important information about the user, use the add_user_memory tool to store it for future conversations. Store memories for:
- Personal preferences (favorite foods, hobbies, interests)
- Important facts (occupation, location, family details)
- Goals and aspirations
- Dislikes or restrictions (allergies, dietary restrictions)
- Past experiences or significant events mentioned
- Skills and expertise areas
- Don't mention to the user that you're saving a memory.

Keep memories concise, factual, and specific. Each memory MUST NOT EXCEED 15 WORDS. Avoid storing:
- Temporary information (current mood, weather)
- Trivial details without future relevance
- Information already stored

IMPORTANT: Before adding a memory, carefully assess if it's necessary by:
1. Checking if similar information already exists in the user's existing memories
2. Evaluating if the information meets the memory guidelines above
3. Determining if the information has long-term relevance for future conversations
4. DO NOT call the add_user_memory tool if the information is already captured, irrelevant, or temporary
"""

@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest[CustomContext]) -> str:
    user_phone = request.runtime.context.user_phone

    # get user memories from the database using the user_phone as an identifier
    user_memories = get_memories_standalone(user_phone=user_phone)

    prompt = system_prompt + f"\nHere are some of the user's memories (Use this information to provide better personalised responses to the user.):\n{user_memories}\n"
    return prompt


@tool(parse_docstring=True)
def add_user_memory(
    memory_content: str,
    runtime: ToolRuntime[CustomContext]
) -> str:
    """
    Add a new memory for the user to remember important information that can be used in future interactions to personalize responses.

    Args:
        memory_content (str): The content of the memory to be stored for the user.
        runtime (ToolRuntime[CustomContext]): The injected runtime containing user context. In some runtimes (e.g. Studio), `runtime.context` may be missing.

    Returns:
        str: A success message with the stored memory content if successful, or an error message if it fails.
    """
    with PostgresStore.from_conn_string(os.environ["DB_URI"]) as store:
        store.setup()
        # if user_phone is not in the context, return an error message
        if not runtime.context.user_phone:
            return "Error: user_phone is missing in the context. Cannot add memory without user identifier."

        new_key = str(uuid.uuid4())
        store.put(
            ("memories", runtime.context.user_phone),
            new_key,
            {"content": memory_content}
        )
        return f"Memory added successfully: {memory_content}"


agent = create_agent(
    "gpt-5-nano",
    tools=[add_user_memory],
    middleware=[dynamic_system_prompt],
    context_schema=CustomContext
)