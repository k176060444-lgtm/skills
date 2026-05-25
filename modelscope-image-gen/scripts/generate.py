#!/usr/bin/env python3
"""
ModelScope Qwen-Image-2512 文生图脚本
用法: python3 generate.py --prompt "提示词" [--output 输出路径]
"""

import argparse
import requests
import time
import json
import os
from PIL import Image
from io import BytesIO

BASE_URL = "https://api-inference.modelscope.cn/"
API_KEY = os.environ.get("MODELSCOPE_API_KEY", "")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def generate_image(prompt: str, output_path: str = None, loras: str = None) -> str:
    """提交图片生成任务"""
    payload = {
        "model": "Qwen/Qwen-Image-2512",
        "prompt": prompt,
    }
    if loras:
        payload["loras"] = loras

    print(f"提交生成任务: {prompt[:50]}...")
    resp = requests.post(
        f"{BASE_URL}v1/images/generations",
        headers={**HEADERS, "X-ModelScope-Async-Mode": "true"},
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        timeout=30,
    )
    resp.raise_for_status()
    task_id = resp.json()["task_id"]
    print(f"任务ID: {task_id}")
    return task_id, prompt, output_path


def poll_and_save(task_id: str, prompt: str, output_path: str = None) -> str:
    """轮询任务状态并保存图片"""
    while True:
        result = requests.get(
            f"{BASE_URL}v1/tasks/{task_id}",
            headers={**HEADERS, "X-ModelScope-Task-Type": "image_generation"},
            timeout=30,
        )
        result.raise_for_status()
        data = result.json()
        status = data.get("task_status", "PROCESSING")
        print(f"状态: {status}")

        if status == "SUCCEED":
            image_url = data["output_images"][0]
            print(f"图片链接: {image_url}")

            # 下载图片
            img_resp = requests.get(image_url, timeout=60)
            img_resp.raise_for_status()
            image = Image.open(BytesIO(img_resp.content))

            # 确定输出路径
            if not output_path:
                safe_name = prompt[:30].replace("/", "-").replace(" ", "_").replace("\n", "_")
                output_path = f"/root/.openclaw/workspace/{safe_name}.jpg"

            image.save(output_path)
            print(f"图片已保存: {output_path}")
            return output_path, image_url

        elif status == "FAILED":
            raise RuntimeError("图片生成失败")

        time.sleep(5)


def main():
    if not API_KEY:
        print("ERROR: 未设置 MODELSCOPE_API_KEY 环境变量", flush=True)
        exit(1)

    parser = argparse.ArgumentParser(description="ModelScope Qwen-Image-2512 文生图")
    parser.add_argument("--prompt", "-p", required=True, help="图片提示词")
    parser.add_argument("--output", "-o", default=None, help="输出文件路径")
    parser.add_argument("--loras", "-l", default=None, help="LoRA 模型 ID（可选）")
    args = parser.parse_args()

    task_id, prompt, output_path = generate_image(args.prompt, args.output, args.loras)
    saved_path, img_url = poll_and_save(task_id, prompt, output_path)

    print(f"\n=== 完成 ===")
    print(f"文件: {saved_path}")
    print(f"链接: {img_url}")


if __name__ == "__main__":
    main()
