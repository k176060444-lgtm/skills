#!/usr/bin/env python3
import json
import subprocess
import os

# MCP protocol: first send initialize request
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

# Send initialize
proc.stdin.write(json.dumps(initialize) + '\n')
proc.stdin.flush()

# Read initialize response
line1 = proc.stdout.readline()
if line1:
    print("=== Initialize response ===")
    try:
        data = json.loads(line1)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Raw: {repr(line1)}")
        print(f"Error: {e}")

# Send tools/list
tools_request = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
}

proc.stdin.write(json.dumps(tools_request) + '\n')
proc.stdin.flush()

# Read tools response
line2 = proc.stdout.readline()
if line2:
    print("\n=== Tools list response ===")
    try:
        data = json.loads(line2)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Raw: {repr(line2)}")
        print(f"Error: {e}")

proc.terminate()
proc.wait(timeout=5)
