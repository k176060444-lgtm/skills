#!/usr/bin/env python3
import json
import subprocess
import sys

# 测试 MiniMax MCP 初始化
mcp_config = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "listTools",
    "params": {}
}

proc = subprocess.Popen(
    ['uvx', 'minimax-mcp'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Send request
proc.stdin.write(json.dumps(mcp_config) + '\n')
proc.stdin.flush()

# Read response
try:
    line = proc.stdout.readline()
    if line:
        print("Response:", json.dumps(json.loads(line), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
finally:
    proc.terminate()
    proc.wait(timeout=5)
