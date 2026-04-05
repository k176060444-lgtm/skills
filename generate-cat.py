#!/usr/bin/env python3
import json
import subprocess
import os

# MCP protocol
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
print(f"Initialize: {line1[:100]}...")

# Call text_to_image
generate_request = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "text_to_image",
        "arguments": {
            "prompt": "一只猫，正在阳光下的窗台晒太阳睡觉，温馨舒适的氛围，柔和的阳光，慵懒的猫咪",
            "aspect_ratio": "1:1",
            "n": 1,
            "prompt_optimizer": True,
            "output_directory": "/root/.openclaw/workspace/minimax-output"
        }
    }
}

proc.stdin.write(json.dumps(generate_request) + '\n')
proc.stdin.flush()

# Read response
print("\nWaiting for generation...")
all_lines = []
while True:
    line = proc.stdout.readline()
    if not line:
        break
    all_lines.append(line)
    try:
        data = json.loads(line)
        if "id" in data and data["id"] == 2:
            print("\n=== Generation result ===")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            break
    except Exception as e:
        print(f"Partial: {line[:80]}...")

proc.terminate()
proc.wait(timeout=10)

# Print any stderr
stderr = proc.stderr.read()
if stderr:
    print("\n=== stderr ===")
    print(stderr)
