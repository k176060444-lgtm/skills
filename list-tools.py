#!/usr/bin/env python3
import json
import subprocess
import os

# Correct initialize request for MCP
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
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

proc.stdin.write(json.dumps(request) + '\n')
proc.stdin.flush()

import os
line = proc.stdout.readline()
if line:
    try:
        data = json.loads(line)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Raw output: {repr(line)}")
        print(f"Error: {e}")
proc.terminate()
proc.wait(timeout=5)
