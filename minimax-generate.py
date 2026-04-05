#!/usr/bin/env python3
import os
import json
import subprocess
import sys
from pathlib import Path

# 配置
api_key = os.environ.get('MINIMAX_API_KEY')
api_host = 'https://api.minimaxi.com'
output_dir = Path('/root/.openclaw/workspace/minimax-output')
output_dir.mkdir(exist_ok=True)

prompt = "一只猫，正在晒太阳睡觉，温馨舒适的氛围"

# 调用 MiniMax MCP 通过 uvx
# MCP 需要通过 JSON-RPC 交互，这里我们直接调用 HTTP API

import requests

url = f"{api_host}/v1/text_to_image"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "prompt": prompt,
    "model": "image-01",
    "aspect_ratio": "1:1",
    "n": 1
}

print(f"Generating image with prompt: {prompt}")
response = requests.post(url, headers=headers, json=data, timeout=120)
print(f"Status code: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
else:
    print(f"Error: {response.text}")
