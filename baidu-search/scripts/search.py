import sys
import json
import requests
import os
import re
from datetime import datetime, timedelta

BAIDU_SEARCH_URL = "https://qianfan.baidubce.com/v2/ai_search/web_search"


def baidu_search(api_key, request_body: dict):
    headers = {
        "Authorization": "Bearer %s" % api_key,
        "X-Appbuilder-From": "openclaw",
        "Content-Type": "application/json"
    }
    response = requests.post(BAIDU_SEARCH_URL, json=request_body, headers=headers)
    response.raise_for_status()
    results = response.json()
    if "code" in results:
        raise Exception(results["message"])
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search.py '<JSON>'")
        sys.exit(1)

    raw = sys.argv[1]
    try:
        params = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        sys.exit(1)

    if "query" not in params:
        print("Error: 'query' is required.")
        sys.exit(1)

    api_key = os.getenv("BAIDU_API_KEY")
    if not api_key:
        print("Error: BAIDU_API_KEY must be set in environment.")
        sys.exit(1)

    # ── count：网页结果数量上限 ────────────────────────────────────
    count = min(max(int(params.get("count", 10)), 1), 50)

    # ── card_limit：阿拉丁卡数量上限（0=不启用）───────────────────
    card_limit = min(max(int(params.get("card_limit", 0)), 0), 20)

    # ── freshness ─────────────────────────────────────────────────────
    search_filter = {}
    current_time = datetime.now()
    end_date = (current_time + timedelta(days=1)).strftime("%Y-%m-%d")
    pattern = r"\d{4}-\d{2}-\d{2}to\d{4}-\d{2}-\d{2}"

    freshness = params.get("freshness")
    if freshness:
        if freshness in ["pd", "pw", "pm", "py"]:
            days_map = {"pd": 1, "pw": 6, "pm": 30, "py": 364}
            start_date = (current_time - timedelta(days=days_map[freshness])).strftime("%Y-%m-%d")
            search_filter = {"range": {"page_time": {"gte": start_date, "lt": end_date}}}
        elif re.match(pattern, freshness):
            start_date, end_date = freshness.split("to")
            search_filter = {"range": {"page_time": {"gte": start_date, "lt": end_date}}}
        else:
            print(f"Error: freshness must be pd/pw/pm/py or match YYYY-MM-DDtoYYYY-MM-DD")
            sys.exit(1)

    # ── 构建请求体 ───────────────────────────────────────────────────
    # cardLimit=0 时：top_k=count
    # cardLimit>0 时：加大 top_k=count+card_limit，确保截断后 web 结果够 count 条
    #   （cardLimit 触发 aladdin 混入，top_k 够大则 aladdin 不影响网页结果数量）
    web_top_k = count if card_limit == 0 else min(count + card_limit, 50)

    request_body = {
        "messages": [{"content": params["query"], "role": "user"}],
        "search_source": "baidu_search_v2",
        "resource_type_filter": [{"type": "web", "top_k": web_top_k}],
    }
    if card_limit > 0:
        request_body["cardLimit"] = card_limit
    if search_filter:
        request_body["search_filter"] = search_filter

    try:
        raw_result = baidu_search(api_key, request_body)

        # 分类：阿拉丁卡由 is_aladdin=True 标识（此字段始终存在，非 cardLimit 开关）
        # card_limit > 0 → 提取阿拉丁卡；否则丢弃
        aladdin_cards = []
        web_results = []

        for item in raw_result.get("references", []):
            if item.get("is_aladdin") is True:
                if card_limit > 0:
                    aladdin_cards.append({
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "date": item.get("date"),
                        "content": item.get("content"),
                        "website": item.get("website"),
                    })
                # 阿拉丁卡始终不进 web_results
            else:
                clean = {k: v for k, v in item.items() if k not in ("snippet",)}
                web_results.append(clean)

        # 输出：网页结果截取到 count 条
        web_results = web_results[:count]

        output = {
            "results": web_results,
            "meta": {
                "query": params["query"],
                "total_results": len(web_results),
                "count": count,
            }
        }
        if card_limit > 0:
            output["aladdin_cards"] = aladdin_cards if aladdin_cards else None
            output["meta"]["aladdin_card_count"] = len(aladdin_cards)
            output["meta"]["card_limit"] = card_limit
            # 清除 None
            output = {k: v for k, v in output.items() if v is not None}

        print(json.dumps(output, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
