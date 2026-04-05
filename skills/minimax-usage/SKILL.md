---
name: minimax-usage
description: Monitor Minimax Coding Plan usage to stay within API limits. Fetches current usage stats and provides status alerts.
metadata: {"clawdbot":{"emoji":"📊"}}
---

# Minimax Usage Skill

Monitor Minimax Coding Plan usage to stay within limits.

## ⚠️ 重要字段说明（经验教训）

- `current_interval_usage_count` = **剩余配额**（不是已用量！！）
- 已用量 = `current_interval_total_count` - `current_interval_usage_count`
- 刷新时间窗口：**20:00 → 次日 00:00（UTC+8）**，刷新时间 = 次日 00:00

## Setup

Create a `.env` file in `~/.openclaw/` with:

```bash
MINIMAX_API_KEY=your_api_key_here
MINIMAX_CODING_GROUP_ID=2029851692941451645
```

⚠️ API Key 域名是 `www.minimaxi.com`，不是 `platform.minimax.io`

## Usage

```bash
bash ~/.openclaw/workspace/skills/minimax-usage/minimax-usage.sh
```

## Output Example

```
🔍 Checking Minimax Coding Plan usage...
✅ Usage retrieved successfully:

📊 Coding Plan Status (MiniMax-M*):
   已用:      98 / 600 prompts (16%)
   剩余:      502 prompts
   刷新倒计时: 约 1h 8m
   窗口时间:   20:00 → 次日 00:00（UTC+8）

   💡 刷新时间 = 次日 00:00，不是当天 20:00

💚 GREEN: 16% used. Plenty of buffer.
```

## API Details

**Endpoint:**
```
GET https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains?GroupId={GROUP_ID}
```

**Required Headers:**
```
Authorization: Bearer {MINIMAX_API_KEY}
Content-Type: application/json
```

## Limits

| Metric | Value |
|--------|-------|
| 刷新时间窗口 | 20:00 → 次日 00:00（UTC+8） |
| Max target | 60% usage |
| 1 prompt ≈ | 15 model calls |

## Notes

- Coding Plan API key is **exclusive** to this plan (not interchangeable with standard API keys)
- `current_interval_usage_count` 字段含义是**剩余配额**，查询结果必须用 `总配额 - usage_count` 计算已用量
- 进度条显示的"X小时"是窗口总时长，不是刷新倒计时
- API域名必须用 `www.minimaxi.com`，用错域名会返回 401/403/404
