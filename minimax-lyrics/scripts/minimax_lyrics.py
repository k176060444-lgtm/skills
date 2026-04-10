#!/usr/bin/env python3
"""
MiniMax 歌词生成脚本
API 文档: https://platform.minimaxi.com/docs/api-reference/lyrics-generation.md
"""

import argparse
import json
import sys
import os
import urllib.request
import urllib.error


def load_api_key():
    """从配置文件加载 API Key"""
    config_path = os.path.expanduser('~/.openclaw/config/minimax.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('api_key')
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def generate_lyrics(api_key, mode, prompt=None, lyrics=None, title=None):
    """
    调用 MiniMax 歌词生成 API

    Args:
        api_key: API Key
        mode: write_full_song 或 edit
        prompt: 歌曲主题/风格描述
        lyrics: 现有歌词（edit 模式用）
        title: 指定歌曲标题

    Returns:
        dict: 包含 song_title, style_tags, lyrics
    """
    url = "https://api.minimaxi.com/v1/lyrics_generation"

    payload = {"mode": mode}
    if prompt:
        payload["prompt"] = prompt
    if lyrics:
        payload["lyrics"] = lyrics
    if title:
        payload["title"] = title

    data = json.dumps(payload).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ''
        try:
            error_json = json.loads(error_body)
            status_code = error_json.get('base_resp', {}).get('status_code', e.code)
            status_msg = error_json.get('base_resp', {}).get('status_msg', str(e))
        except:
            status_code = e.code
            status_msg = str(e)
        print(f"Error {status_code}: {status_msg}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)

    base_resp = result.get('base_resp', {})
    if base_resp.get('status_code') != 0:
        print(f"API error {base_resp.get('status_code')}: {base_resp.get('status_msg', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)

    return {
        'song_title': result.get('song_title', ''),
        'style_tags': result.get('style_tags', ''),
        'lyrics': result.get('lyrics', '')
    }


def main():
    parser = argparse.ArgumentParser(description='MiniMax 歌词生成')
    parser.add_argument('--mode', '-m', choices=['write_full_song', 'edit'],
                        default='write_full_song',
                        help='生成模式: write_full_song(完整歌曲) 或 edit(编辑/续写)')
    parser.add_argument('--prompt', '-p', type=str,
                        help='歌曲主题/风格描述（最多2000字）')
    parser.add_argument('--lyrics', '-l', type=str,
                        help='现有歌词内容（仅 edit 模式使用，最多3500字）')
    parser.add_argument('--title', '-t', type=str,
                        help='指定歌曲标题')
    parser.add_argument('--output', '-o', type=str, default='-',
                        help='输出文件路径（默认输出到标准输出）')

    args = parser.parse_args()

    api_key = load_api_key()
    if not api_key:
        print("Error: API Key not found. Please configure ~/.openclaw/config/minimax.json", file=sys.stderr)
        sys.exit(1)

    result = generate_lyrics(
        api_key=api_key,
        mode=args.mode,
        prompt=args.prompt,
        lyrics=args.lyrics,
        title=args.title
    )

    # 构建输出
    output_lines = [
        f"🎵 歌名: {result['song_title']}",
        f"🏷️ 风格: {result['style_tags']}",
        "",
        "📝 歌词:",
        "-" * 40,
        result['lyrics'],
        "-" * 40,
        "",
        "💡 使用提示: 将上述歌词作为 --lyrics 参数配合 mmx music generate 生成歌曲"
    ]

    output_text = '\n'.join(output_lines)

    if args.output == '-':
        print(output_text)
    else:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"✅ 歌词已保存到: {args.output}", file=sys.stderr)


if __name__ == '__main__':
    main()
