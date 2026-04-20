---
name: baidu-search
description: Search the web using Baidu AI Search Engine (BDSE). Use for live information, documentation, or research topics.
metadata: { "openclaw": { "emoji": "🔍︎",  "requires": { "bins": ["python3"], "env":["BAIDU_API_KEY"]},"primaryEnv":"BAIDU_API_KEY" } }
---

# Baidu Search

Search the web via Baidu AI Search API.

## Prerequisites

### API Key Configuration
This skill requires a **BAIDU_API_KEY** to be configured in OpenClaw.

If you don't have an API key yet, please visit:
**https://console.bce.baidu.com/ai-search/qianfan/ais/console/apiKey**

For detailed setup instructions, see:
[references/apikey-fetch.md](references/apikey-fetch.md)

## Usage

```bash
python3 skills/baidu-search/scripts/search.py '<JSON>'
```

## Request Parameters

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| query | str | yes | - | Search query |
| count | int | no | 10 | Number of web results to return, range 1-50 |
| freshness | str | no | null | Time range filter (see below) |
| card_limit | int | no | 0 | Max Aladdin cards to return (0=disabled, 1-20). When >0, results include `aladdin_cards` array alongside `results` |

### freshness 参数格式

| 值 | 含义 |
|---|---|
| `pd` | 最近 24 小时 |
| `pw` | 最近 7 天 |
| `pm` | 最近 31 天 |
| `py` | 最近 364 天 |
| `YYYY-MM-DDtoYYYY-MM-DD` | 自定义范围，如 `2025-01-01to2025-06-30` |

## Output Format

```json
{
  "results": [...],           // 普通网页搜索结果
  "aladdin_cards": [...],    // 阿拉丁卡数组（仅当 card_limit > 0 时有）
  "meta": {
    "query": "...",
    "total_results": 10,
    "aladdin_card_count": 2,
    "count": 10,
    "card_limit": 5
  }
}
```

## Examples

### 基础搜索
```bash
python3 scripts/search.py '{"query":"人工智能"}'
```

### 搜索 + 返回阿拉丁卡（最多5条）
当查询词条在百度知识图谱中有对应数据时，`aladdin_cards` 数组会包含知识卡片、问答卡片等结构化内容。
```bash
python3 scripts/search.py '{"query":"小米15配置", "card_limit": 5}'
```

### 限定时间范围
```bash
python3 scripts/search.py '{"query":"杭州天气", "freshness": "pw"}'
python3 scripts/search.py '{"query":"最新新闻", "freshness": "2026-03-01to2026-04-19"}'
```

### 指定结果数量
```bash
python3 scripts/search.py '{"query":"旅游景点", "count": 20}'
```

## 阿拉丁卡说明（card_limit 参数）

**阿拉丁卡（Aladdin Card）** 是百度搜索结果页中的富内容信息卡片（知识卡片、问答卡片、商品卡片等），只有查询词条在百度知识图谱中有结构化数据时才会返回。

**使用方式：** 传入 `card_limit` 参数（1-20），主搜索结果中会同时包含 `aladdin_cards` 数组。

> 注意：阿拉丁卡独立接口（`POST /aladdin_card`）为 beta 状态，需单独开通。本 skill 通过 `card_limit` 参数在主搜索接口中附带阿拉丁卡数据，兼容性更好。

## Current Status

Fully functional — supports card_limit (0=off, 1-20=Aladdin cards), freshness, and count.
