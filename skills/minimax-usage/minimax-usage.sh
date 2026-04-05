#!/bin/bash
# Minimax Coding Plan Usage Check
# Usage: ./minimax-usage.sh
# Requires: MINIMAX_API_KEY and MINIMAX_CODING_GROUP_ID in .env
#
# ⚠️ 重要字段说明（经验教训，禁止混淆）：
# - current_interval_usage_count = 剩余配额（不是已用量！！）
# - 已用量 = current_interval_total_count - current_interval_usage_count
# - 刷新时间窗口：20:00 → 次日 00:00（UTC+8），不是当天20:00

source "$(dirname "$0")/../../.env"

API_KEY="${MINIMAX_API_KEY}"
GROUP_ID="${MINIMAX_CODING_GROUP_ID:-2029851692941451645}"

if [ -z "$API_KEY" ]; then
  echo "❌ Error: MINIMAX_API_KEY not found in .env"
  exit 1
fi

echo "🔍 Checking Minimax Coding Plan usage..."

# ⚠️ 正确域名是 www.minimaxi.com，不是 platform.minimax.io
RESPONSE=$(curl -s "https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains?GroupId=${GROUP_ID}" \
  --header "Authorization: Bearer $API_KEY" \
  --header "Content-Type: application/json" \
  --write-out "\nHTTP_STATUS:%{http_code}")

STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_STATUS")

if [ "$STATUS" = "200" ]; then
  ERROR_CODE=$(echo "$BODY" | jq -r '.base_resp.status_code' 2>/dev/null)

  if [ "$ERROR_CODE" != "0" ]; then
    echo "❌ API Error: $(echo "$BODY" | jq -r '.base_resp.status_msg' 2>/dev/null)"
    exit 1
  fi

  # ⚠️ current_interval_usage_count 在这里实为"剩余配额"，不是"已用量"
  TOTAL=$(echo "$BODY" | jq -r '.model_remains[0].current_interval_total_count' 2>/dev/null)
  USAGE_COUNT=$(echo "$BODY" | jq -r '.model_remains[0].current_interval_usage_count' 2>/dev/null)
  REMAINS_TIME=$(echo "$BODY" | jq -r '.model_remains[0].remains_time' 2>/dev/null)
  END_TIME=$(echo "$BODY" | jq -r '.model_remains[0].end_time' 2>/dev/null)
  MODEL=$(echo "$BODY" | jq -r '.model_remains[0].model_name' 2>/dev/null)

  if [ "$TOTAL" != "null" ] && [ "$USAGE_COUNT" != "null" ]; then
    # 正确计算：已用量 = 总配额 - usage_count（剩余）
    USED=$((TOTAL - USAGE_COUNT))
    PERCENT=$((USED * 100 / TOTAL))

    # remains_time 是毫秒，表示当前窗口剩余时间（约值，有数秒误差）
    REMAINS_MS=$((REMAINS_TIME / 1000))
    REMAINS_HOURS=$((REMAINS_MS / 3600))
    REMAINS_MINUTES=$(((REMAINS_MS % 3600) / 60))
    REMAINS_SECONDS=$((REMAINS_MS % 60))

    # end_time 是 Unix 毫秒时间戳，动态计算实际刷新时间
    if [ "$END_TIME" != "null" ] && [ "$END_TIME" != "0" ]; then
      END_DATE=$(date -d "@$((END_TIME / 1000))" "+%Y-%m-%d %H:%M" 2>/dev/null || date -r "$((END_TIME / 1000))" "+%Y-%m-%d %H:%M" 2>/dev/null)
      RESET_INFO="刷新时间: ${END_DATE}（约 ${REMAINS_HOURS}h ${REMAINS_MINUTES}m ${REMAINS_SECONDS}s 后）"
    else
      RESET_INFO="刷新倒计时: 约 ${REMAINS_HOURS}h ${REMAINS_MINUTES}m ${REMAINS_SECONDS}s"
    fi

    # 刷新时间 = 次日 00:00（UTC+8），不是当天20:00
    # 窗口时长为5小时（20:00 → 00:00）

    echo "✅ Usage retrieved successfully:"
    echo ""
    echo "📊 Coding Plan Status (${MODEL}):"
    echo "   已用:      ${USED} / ${TOTAL} prompts (${PERCENT}%)"
    echo "   剩余:      ${USAGE_COUNT} prompts"
    echo "   ${RESET_INFO}"

    if [ "$PERCENT" -gt 90 ]; then
      echo ""
      echo "🚨 CRITICAL: ${PERCENT}% used! Stop all AI work immediately."
    elif [ "$PERCENT" -gt 75 ]; then
      echo ""
      echo "⚠️  WARNING: ${PERCENT}% used. Approaching limit."
    elif [ "$PERCENT" -gt 60 ]; then
      echo ""
      echo "⚠️  CAUTION: ${PERCENT}% used. Target is 60%."
    else
      echo ""
      echo "💚 GREEN: ${PERCENT}% used. Plenty of buffer."
    fi
  else
    echo "⚠️  Could not parse usage data"
    echo "Raw: $BODY"
  fi

elif [ "$STATUS" = "401" ] || [ "$STATUS" = "403" ]; then
  echo "❌ Authorization failed. Check API key."
elif [ "$STATUS" = "500" ] || [ "$STATUS" = "502" ]; then
  echo "⚠️  Server error. Try again later."
else
  echo "❌ Error (HTTP $STATUS)"
  echo "Response: $BODY"
fi
