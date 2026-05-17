# backend/agent.py
import os
import sys
from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp.client.stdio import StdioServerParameters
from dotenv import load_dotenv

load_dotenv()

# Define connection parameters for the local MCP server
mcp_connection = StdioConnectionParams(
    timeout=60.0,
    server_params=StdioServerParameters(
        command=sys.executable,
        args=[os.path.abspath(os.path.join(os.path.dirname(__file__), "mcp_server.py"))],
        env=os.environ.copy()
    )
)

# System instruction for the agent
SYSTEM_INSTRUCTION = """
You are a GitHub profile analyst and dev card generator. When a user gives you a GitHub username, you ALWAYS follow this exact sequence:
1. Call 'scrape_github' to fetch profile data. Wait for the response.
2. Call 'analyze_profile' with the result from scrape_github. Wait for the response.
3. Call 'generate_card_html' with the username, github_data, and analysis. Wait for the response.
4. Call 'save_card' with the username and the generated HTML.

CRITICAL: You MUST call ALL FOUR tools in order for every request. Do not stop after analyze_profile! Once you have the analysis, you MUST immediately call generate_card_html, and then save_card. After calling save_card, output a friendly text message to the user summarizing the card you created.
"""

# Create the agent
github_card_agent = Agent(
    name="GitHubDevCardAgent",
    model="gemini-2.0-flash",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        McpToolset(connection_params=mcp_connection)
    ]
)
