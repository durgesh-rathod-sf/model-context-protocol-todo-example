# File: mcp_server.py
from fastapi import FastAPI, Request
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import Settings
from pydantic import BaseModel

# Initialize the MCP FastAPI server
mcp_server = FastMCP("My MCP Server", port=9002, host="0.0.0.0")

FASTAPI_APP_URL = "http://0.0.0.0:9001"

# -----------------------
# Tool Input Models
# -----------------------

class CreateTodoInput(BaseModel):
    title: str
    description: str
    completed: bool = False

class DeleteTodoInput(BaseModel):
    id: int

# -----------------------
# Tool Definitions (no Request object!)
# -----------------------

@mcp_server.tool(
    name="get_all_todos",
    description="Fetch all todos from the FastAPI app."
)
async def get_all_todos() -> dict:
    print("TOOL Called: get_all_todos")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FASTAPI_APP_URL}/todos")
        return response.json()

@mcp_server.tool(
    name="create_todo",
    description="Create a new todo with title and description."
)
async def create_todo(input: CreateTodoInput) -> dict:
    print("TOOL Called: create_todo")
    payload = input.dict()
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{FASTAPI_APP_URL}/todos", json=payload)
        return response.json()

@mcp_server.tool(
    name="delete_todo",
    description="Delete a todo by its ID."
)
async def delete_todo(input: DeleteTodoInput) -> dict:
    print("TOOL Called: delete_todo")
    todo_id = input.id
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{FASTAPI_APP_URL}/todos/{todo_id}")
        return response.json()

# -----------------------
# Run MCP Server
# -----------------------

if __name__ == "__main__":
    mcp_server.run(transport="sse")
