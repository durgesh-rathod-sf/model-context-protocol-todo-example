# File: mcp_client.py
import uuid
import traceback
import asyncio
import os
import json
import logging

from fastapi import FastAPI, Request
from pydantic import BaseModel
from dotenv import load_dotenv
from mcp_use import MCPAgent, MCPClient, set_debug
from langchain_openai import AzureChatOpenAI
import httpx
# from mcp_use.transports.streamable_http import StreamableHTTPClientTransport

# Load environment variables
load_dotenv()

# Enable debug logs from mcp_use
set_debug(2)

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mcp_client")

# FastAPI app
app = FastAPI()

# HTTPX client for outbound calls (if needed)
http_client = httpx.AsyncClient(timeout=10.0)

# Azure OpenAI LLM config
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# MCP server endpoint (stateless)
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://0.0.0.0:9002")

# Pydantic schema for chat input
class ChatRequest(BaseModel):
    prompt: str

async def load_mcp_client(headers: dict):
    logger.debug("🔧 Building MCP client config for stateless server...")
    # transport = StreamableHTTPClientTransport(
    #     url=f"{MCP_SERVER_URL}/sse",
    #     # headers=headers or {},
    #     # poll_notifications=False  # ✅ prevent GET /mcp
    # )
    # return MCPClient(transports={"http": transport})

    config = {
    "mcpServers": {
        "http": {
            "url": f"{MCP_SERVER_URL}/sse",
            # "transport": "streamable_http",  # ✅ Force streamable HTTP
            # "headers": headers or {}
        }
    }
}

    return MCPClient.from_dict(config)

async def setup_agent(headers: dict) -> MCPAgent:
    logger.debug("🧠 Setting up MCP agent with Azure OpenAI and MCP client...")
    mcp_client = await load_mcp_client(headers)

    llm = AzureChatOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=azure_api_key,
        deployment_name=azure_deployment_name,
        api_version=api_version,
        temperature=0.2
    )

    agent = MCPAgent(
        llm=llm,
        client=mcp_client,
        max_steps=20,
        memory_enabled=False,
        verbose=True,
    )

    logger.info("✅ MCP Agent initialized successfully")
    return agent

@app.post("/chat")
async def chat(req: ChatRequest, request: Request):
    try:
        logger.info(f"📨 Incoming chat request: {req.prompt!r}")

        # Construct formatted system prompt
        prompt = f"""
        ### Goal and Instructions:
        You are a helpful and approachable professional assistant. 
        Respond to the user in a friendly and engaging manner.
        All your response should be in a formatted markdown text only.
        Use the tools provided.

        User Query: {req.prompt}
        """

        # Filter relevant headers to forward
        incoming_headers = {
            key: value for key, value in dict(request.headers).items()
            if key.lower() not in {"host", "content-length"}
        }

        # Setup the MCP agent
        agent = await setup_agent({})

        # Run the MCP agent with the prompt
        response = await agent.run(prompt)

        logger.info("✅ Agent response generated")
        return {"response": response}

    except Exception as e:
        logger.exception("❌ Exception in /chat")
        return {"error": str(e)}

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()
    logger.info("🔌 HTTPX client closed on shutdown")
