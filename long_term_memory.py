from dataclasses import dataclass

from langchain_core.runnables import RunnableConfig
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langgraph.store.memory import InMemoryStore
from dotenv import load_dotenv
from langgraph.store.postgres import PostgresStore

import os
import uuid
import asyncio

load_dotenv()

# Dependency to get the database session
def get_store():
    """Dependency that provides a PostgresStore instance."""
    with PostgresStore.from_conn_string(os.environ["DB_URI"]) as store:
        store.setup()
        yield store


# Use the store
async def main():
    with PostgresStore.from_conn_string(os.environ["DB_URI"]) as store:
        store.setup()
        
        # Write sample data to the store using the aput method with proper dict structure
        # new_key = str(uuid.uuid4())
        # await store.aput(
        #     ("memories","256700000000"),
        #     new_key,
        #     {"content": "His male"}
        # )
        # print(f"Stored memory with key: {new_key}")

        # # Read data from the store using the aget method
        # memory = await store.aget(namespace=("memories","256700000000"), key=new_key)
        # print("Retrieved memory:", memory.value if memory else "No memory found")

        # update the memory
        # await store.aput(
        #     ("memories","256700000000"),
        #     "06782c30-319f-4fab-894c-c0e5987a95d8",
        #     {"content": "User is a football fan and a software developer"}
        # )
        # print(f"Updated memory with key: 06782c30-319f-4fab-894c-c0e5987a95d8")

        # delete memory
        # await store.adelete(
        #     ("memories","256700000000"), 
        #     "4f369534-3b19-4046-b802-f921f68fbce7"
        # )
        # print("Deleted memory with key: 4f369534-3b19-4046-b802-f921f68fbce7")

        # get all memories for a user
        memories = await store.asearch(("memories","256700000000"))
        print("All memories for user 256700000000:")
        for memory in memories:
            print(f"-(key: {memory.key}, content: {memory.value['content']})")


asyncio.run(main())

# @app.get("/memories")
# def get_memories(store: PostgresStore = Depends(get_store)):
#     return store.search(("memories",))

# @dataclass
# class Context:
#     user_id: str

# # InMemoryStore saves data to an in-memory dictionary. Use a DB-backed store in production.
# store = InMemoryStore() 



# @tool
# def get_user_info(runtime: ToolRuntime[Context]) -> str:
#     """Look up user info."""
#     # Access the store - same as that provided to `create_agent`
#     store = runtime.store 
#     user_id = runtime.context.user_id
#     # Retrieve data from store - returns StoreValue object with value and metadata
#     user_info = store.get(("users",), user_id)
#     return str(user_info.value) if user_info else "Unknown user"


# agent = create_agent(
#     "gpt-5-nano",
#     tools=[get_user_info],
#     # Pass store to agent - enables agent to access store when running tools
#     store=store, 
#     context_schema=Context
# )

# # Run the agent
# agent.invoke(
#     {"messages": [{"role": "user", "content": "look up user information"}]},
#     context=Context(user_id="user_123") 
# )
