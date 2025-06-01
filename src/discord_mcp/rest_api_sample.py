import os
import requests
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")  # サーバーID

headers = {
    "Authorization": f"Bot {DISCORD_TOKEN}",
    "Content-Type": "application/json"
}

# ログ出力関数
def log(msg):
    print(msg, flush=True)
    with open("/tmp/discord_mcp_rest_api.log", "a", encoding="utf-8") as log_file:
        log_file.write(msg + "\n")

# REST APIラッパー関数

def send_message(channel_id: str, content: str):
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    data = {"content": content}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code in (200, 201):
        return response.json()
    raise Exception(f"エラー: {response.status_code}\n{response.text}")

def get_guild():
    url = f"https://discord.com/api/v10/guilds/{GUILD_ID}"
    response = requests.get(url, headers=headers)
    log(f"[get_guild] url={url} status={response.status_code} text={response.text}")
    if response.status_code == 200:
        return response.json()
    raise Exception(f"エラー: {response.status_code}\n{response.text}")

def list_members(limit=100):
    url = f"https://discord.com/api/v10/guilds/{GUILD_ID}/members?limit={limit}"
    response = requests.get(url, headers=headers)
    log(f"[list_members] url={url} status={response.status_code} text={response.text}")
    if response.status_code == 200:
        return response.json()
    raise Exception(f"エラー: {response.status_code}\n{response.text}")

def get_roles():
    url = f"https://discord.com/api/v10/guilds/{GUILD_ID}/roles"
    response = requests.get(url, headers=headers)
    log(f"[get_roles] url={url} status={response.status_code} text={response.text}")
    if response.status_code == 200:
        return response.json()
    raise Exception(f"エラー: {response.status_code}\n{response.text}")

def get_user(user_id: str):
    url = f"https://discord.com/api/v10/users/{user_id}"
    response = requests.get(url, headers=headers)
    log(f"[get_user] url={url} status={response.status_code} text={response.text}")
    if response.status_code == 200:
        return response.json()
    raise Exception(f"エラー: {response.status_code}\n{response.text}")

# MCPサーバー初期化
app = Server("discord-rest-server")

@app.list_tools()
async def list_tools():
    log("[MCP] list_tools called")
    return [
        Tool(
            name="send_message",
            description="Send a message to a specific channel via REST API",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {"type": "string", "description": "Discord channel ID"},
                    "content": {"type": "string", "description": "Message content"}
                },
                "required": ["channel_id", "content"]
            }
        ),
        Tool(
            name="get_server_info",
            description="Get information about a Discord server",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_members",
            description="Get a list of members in a server",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "number", "description": "Maximum number of members to fetch", "minimum": 1, "maximum": 1000}
                },
                "required": []
            }
        ),
        Tool(
            name="get_user_info",
            description="Get information about a Discord user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Discord user ID"}
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="get_roles",
            description="Get all roles in the server",
            inputSchema={"type": "object", "properties": {}, "required": []}
        )
    ]

@app.call_tool()
async def call_tool(name, arguments):
    log(f"[MCP] call_tool called: name={name}, arguments={arguments}")
    if name == "send_message":
        result = send_message(arguments["channel_id"], arguments["content"])
        log(f"[MCP] send_message result: {result}")
        return [TextContent(type="text", text=f"Message sent successfully. Message ID: {result['id']}")]
    elif name == "get_server_info":
        info = get_guild()
        log(f"[MCP] get_server_info result: {info}")
        return [TextContent(type="text", text=f"Server Information:\n" + "\n".join(f"{k}: {v}" for k, v in info.items()))]
    elif name == "list_members":
        limit = int(arguments.get("limit", 100))
        members = list_members(limit=limit)
        roles = {r['id']: r['name'] for r in get_roles()}
        def role_names(role_ids):
            return ", ".join([roles.get(rid, rid) for rid in role_ids])
        log(f"[MCP] list_members result: {len(members)} members")
        return [TextContent(
            type="text",
            text=f"Server Members ({len(members)}):\n" +
                 "\n".join(f"{m['user']['username']} (ID: {m['user']['id']}, Roles: {role_names(m['roles'])})" for m in members)
        )]
    elif name == "get_user_info":
        user = get_user(arguments["user_id"])
        log(f"[MCP] get_user_info result: {user}")
        return [TextContent(
            type="text",
            text=f"User information:\n" +
                 f"Name: {user['username']}#{user.get('discriminator', '0000')}\n" +
                 f"ID: {user['id']}\n" +
                 f"Bot: {user.get('bot', False)}\n"
        )]
    elif name == "get_roles":
        roles = get_roles()
        log(f"[MCP] get_roles result: {roles}")
        return [TextContent(
            type="text",
            text="Roles:\n" + "\n".join(f"{r['id']}: {r['name']}" for r in roles)
        )]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
