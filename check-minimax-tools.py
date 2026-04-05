#!/usr/bin/env python3
import json
import subprocess
import os

# MCP initialize
initialize = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "clientInfo": {
            "name": "openclaw-test",
            "version": "1.0.0"
        },
        "capabilities": {}
    }
}

env = {
    **dict(os.environ),
    "MINIMAX_API_KEY": os.environ.get("MINIMAX_API_KEY", ""),
    "MINIMAX_API_HOST": "https://api.minimaxi.com",
    "MINIMAX_MCP_BASE_PATH": "/root/.openclaw/workspace/minimax-output",
}

proc = subprocess.Popen(
    ['uvx', 'minimax-mcp'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    env=env
)

proc.stdin.write(json.dumps(initialize) + '\n')
proc.stdin.flush()
proc.stdout.readline()

# List tools
tools_request = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
}

proc.stdin.write(json.dumps(tools_request) + '\n')
proc.stdin.flush()

line = proc.stdout.readline()
data = json.loads(line)
tools = data['result']['tools']

print("=== Available tools ===")
for tool in tools:
    print(f"- {tool['name']}: {tool['description'].splitlines()[0]}")

proc.terminate()
proc.wait(timeout=5)
