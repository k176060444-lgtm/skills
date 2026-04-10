#!/usr/bin/env python3
"""
MiniMax 音乐生成工具
模型：music-2.6（默认固定）
输出格式：MP3（默认）
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from binascii import unhexlify

import requests


def generate_music(
    prompt: str,
    lyrics: str = None,
    is_instrumental: bool = False,
    duration: int = 60,
    lyrics_optimizer: bool = False,
    output_format: str = "hex",
    api_key: str = None,
    output_path: str = None
) -> dict:
    """
    生成音乐
    
    Args:
        prompt: 音乐描述（风格、情绪、场景）
        lyrics: 歌词（用 \\n 分隔行），非纯音乐时必填
        is_instrumental: 是否纯音乐（无人声）
        duration: 时长（秒）
        lyrics_optimizer: 是否自动根据 prompt 生成歌词
        output_format: 输出格式（hex 或 url）
        api_key: MiniMax API Key
        output_path: 输出文件路径
        
    Returns:
        dict: 包含 status, message, file_path 等
    """
    
    # 获取 API Key
    if not api_key:
        api_key = os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        return {
            "status": "error",
            "message": "未找到 MINIMAX_API_KEY 环境变量"
        }
    
    # 验证参数
    if is_instrumental:
        if not prompt or len(prompt) < 1:
            return {
                "status": "error", 
                "message": "纯音乐模式需要提供 prompt（1-2000字符）"
            }
        if len(prompt) > 2000:
            return {
                "status": "error",
                "message": "prompt 长度不能超过 2000 字符"
            }
    else:
        if not lyrics_optimizer and (not lyrics or len(lyrics) < 1):
            return {
                "status": "error",
                "message": "非纯音乐模式需要提供 lyrics（1-3500字符）或设置 lyrics_optimizer=true"
            }
    
    # 构建请求
    url = "https://api.minimaxi.com/v1/music_generation"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 构建请求体
    payload = {
        "model": "music-2.6",
        "prompt": prompt,
        "is_instrumental": is_instrumental,
        "output_format": output_format,
        "audio_setting": {
            "sample_rate": 44100,
            "bitrate": 256000,
            "format": "mp3"
        }
    }
    
    # 添加歌词或启用歌词优化
    if lyrics:
        payload["lyrics"] = lyrics
    elif lyrics_optimizer:
        payload["lyrics_optimizer"] = True
    
    try:
        print(f"正在生成音乐...")
        print(f"  模型: music-2.6")
        print(f"  类型: {'纯音乐' if is_instrumental else '歌曲'}")
        print(f"  描述: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        if lyrics and not lyrics_optimizer:
            print(f"  歌词: {lyrics[:50]}{'...' if len(lyrics) > 50 else ''}")
        if lyrics_optimizer:
            print(f"  歌词: 自动生成")
        print(f"  时长: {duration} 秒")
        
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        result = response.json()
        
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "请求超时，请检查网络连接"
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"请求失败: {str(e)}"
        }
    except json.JSONDecodeError:
        return {
            "status": "error", 
            "message": "响应 JSON 解析失败"
        }
    
    # 检查 API 响应状态
    base_resp = result.get("base_resp", {})
    status_code = base_resp.get("status_code", -1)
    status_msg = base_resp.get("status_msg", "")
    
    if status_code != 0:
        error_messages = {
            1002: "触发限流，请稍后再试",
            1004: "账号鉴权失败，请检查 API Key",
            1008: "账号余额不足",
            2013: "参数异常，请检查输入",
            2049: "无效的 API Key"
        }
        return {
            "status": "error",
            "message": f"API 错误 [{status_code}]: {error_messages.get(status_code, status_msg)}"
        }
    
    # 获取音频数据
    data = result.get("data", {})
    audio_hex = data.get("audio", "")
    
    if not audio_hex:
        return {
            "status": "error",
            "message": "未获取到音频数据"
        }
    
    # 解码音频（HEX 编码 → bytes）
    try:
        audio_bytes = unhexlify(audio_hex)
    except Exception as e:
        return {
            "status": "error",
            "message": f"音频解码失败: {str(e)}"
        }
    
    # 获取音频信息
    extra_info = result.get("extra_info", {})
    music_duration = extra_info.get("music_duration", 0) / 1000  # 转换为秒
    bitrate = extra_info.get("bitrate", 0)
    music_size = extra_info.get("music_size", 0)
    
    # 确定输出路径
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"/root/.openclaw/workspace/music_{timestamp}.mp3"
    
    # 保存文件
    try:
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
    except IOError as e:
        return {
            "status": "error",
            "message": f"文件保存失败: {str(e)}"
        }
    
    return {
        "status": "success",
        "message": "音乐生成成功",
        "file_path": output_path,
        "duration": f"{int(music_duration // 60)}:{int(music_duration % 60):02d}",
        "duration_seconds": music_duration,
        "bitrate": bitrate,
        "size_bytes": music_size,
        "size_mb": round(music_size / 1024 / 1024, 2)
    }


def main():
    parser = argparse.ArgumentParser(
        description="MiniMax 音乐生成工具 - 使用 music-2.6 模型"
    )
    
    # 主要参数
    parser.add_argument(
        "--prompt", "-p",
        type=str,
        default=None,
        help="音乐描述（风格、情绪、场景），纯音乐模式必填"
    )
    parser.add_argument(
        "--lyrics", "-l",
        type=str,
        default=None,
        help="歌词（用 \\n 分隔行），非纯音乐时必填"
    )
    parser.add_argument(
        "--is_instrumental", "-i",
        action="store_true",
        default=False,
        help="生成纯音乐（无人声）"
    )
    parser.add_argument(
        "--lyrics_optimizer",
        action="store_true", 
        default=False,
        help="自动根据 prompt 生成歌词"
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=60,
        help="音乐时长（秒），默认 60"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出文件路径"
    )
    parser.add_argument(
        "--api_key",
        type=str,
        default=None,
        help="MiniMax API Key（也可通过 MINIMAX_API_KEY 环境变量）"
    )
    
    args = parser.parse_args()
    
    # 执行生成
    result = generate_music(
        prompt=args.prompt or "",
        lyrics=args.lyrics,
        is_instrumental=args.is_instrumental,
        duration=args.duration,
        lyrics_optimizer=args.lyrics_optimizer,
        output_path=args.output,
        api_key=args.api_key
    )
    
    # 输出结果
    if result["status"] == "success":
        print("\n✅ 音乐生成成功！")
        print(f"   文件路径: {result['file_path']}")
        print(f"   时长: {result['duration']}")
        print(f"   大小: {result['size_mb']} MB")
        print(f"   比特率: {result['bitrate']} bps")
        return 0
    else:
        print(f"\n❌ 生成失败: {result['message']}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
