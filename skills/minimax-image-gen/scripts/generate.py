#!/usr/bin/env python3
"""
MiniMax 图像生成脚本
通过 MCP 协议调用 MiniMax API 生成图片
"""

import json
import argparse
import subprocess
import os
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='MiniMax 文生图')
    parser.add_argument('prompt', nargs='?', help='生成图片的提示词')
    parser.add_argument('--prompt', dest='prompt_opt', help='生成图片的提示词')
    parser.add_argument('--model', default='image-01', help='模型名称 (默认: image-01)')
    parser.add_argument('--aspect-ratio', default='1:1', 
                        choices=['1:1', '16:9', '4:3', '3:2', '2:3', '3:4', '9:16', '21:9'],
                        help='宽高比 (默认: 1:1)')
    parser.add_argument('--n', type=int, default=1, help='生成图片数量 1-9 (默认: 1)')
    parser.add_argument('--no-optimizer', action='store_true', help='禁用提示词优化')
    parser.add_argument('--output-dir', default='/root/.openclaw/workspace/minimax-output', 
                        help='输出目录 (默认: /root/.openclaw/workspace/minimax-output)')
    
    args = parser.parse_args()
    
    # Get prompt from positional or optional
    prompt = args.prompt or args.prompt_opt
    if not prompt:
        print("Error: prompt is required", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    # Check environment
    api_key = os.environ.get('MINIMAX_API_KEY')
    if not api_key:
        print("Error: MINIMAX_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    api_host = os.environ.get('MINIMAX_API_HOST', 'https://api.minimaxi.com')
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Environment for subprocess
    env = {
        **dict(os.environ),
        'MINIMAX_API_KEY': api_key,
        'MINIMAX_API_HOST': api_host,
        'MINIMAX_MCP_BASE_PATH': str(output_dir),
    }
    
    # MCP initialize request
    initialize = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {
                "name": "minimax-image-gen-openclaw",
                "version": "1.0.0"
            },
            "capabilities": {}
        }
    }
    
    # Generate image request
    generate_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "text_to_image",
            "arguments": {
                "model": args.model,
                "prompt": prompt,
                "aspect_ratio": args.aspect_ratio,
                "n": args.n,
                "prompt_optimizer": not args.no_optimizer,
                "output_directory": str(output_dir)
            }
        }
    }
    
    # Start process
    print(f"Generating image with prompt: {prompt}")
    print(f"Aspect ratio: {args.aspect_ratio}, Number of images: {args.n}")
    
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
    if not line1:
        print("Error: No response from MCP server on initialize", file=sys.stderr)
        proc.terminate()
        sys.exit(1)
    
    # Send generate request
    proc.stdin.write(json.dumps(generate_request) + '\n')
    proc.stdin.flush()
    
    # Wait for response
    result = None
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        try:
            data = json.loads(line)
            if "id" in data and data["id"] == 2:
                result = data
                break
        except json.JSONDecodeError:
            continue
    
    proc.terminate()
    proc.wait(timeout=10)
    
    # Check result
    if not result:
        stderr = proc.stderr.read()
        print(f"Error: No result received from MCP server", file=sys.stderr)
        if stderr:
            print(f"\nSTDERR:\n{stderr}", file=sys.stderr)
        sys.exit(1)
    
    if "error" in result:
        print(f"Error: {result['error'].get('message', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)
    
    # Print result
    print("\n✅ 生成成功!")
    content = result['result']['content']
    for item in content:
        if item['type'] == 'text':
            print(f"\n{item['text']}")
    
    sys.exit(0)

if __name__ == "__main__":
    main()
