#!/usr/bin/env python3
"""DeepSeek 余额查询脚本"""

import os
import json
import subprocess

def get_balance():
    # 从环境变量读取 key
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY environment variable not set")
        return None

    cmd = [
        "curl", "-s", "-X", "GET",
        "https://api.deepseek.com/user/balance",
        "-H", "Accept: application/json",
        "-H", f"Authorization: Bearer {api_key}"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


if __name__ == "__main__":
    resp = get_balance()
    try:
        data = json.loads(resp)
        if "balance_infos" in data:
            info = data["balance_infos"][0]
            print("=== DeepSeek 账户余额 ===")
            print(f"状态: {'可用' if data.get('is_available') else '不可用'}")
            print(f"货币: {info.get('currency', 'N/A')}")
            print(f"总余额: ¥{info.get('total_balance', 'N/A')}")
            print(f"赠送余额: ¥{info.get('granted_balance', '0')}")
            print(f"充值余额: ¥{info.get('topped_up_balance', 'N/A')}")
        else:
            print(resp)
    except json.JSONDecodeError:
        print("解析失败:", resp)