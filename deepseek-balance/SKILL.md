---
name: deepseek-balance
description: |
  查询 DeepSeek 账户余额。当用户提到"查询 DeepSeek 余额"、"DeepSeek 还剩多少钱"、
  "查一下 DeepSeek 账户"时使用此 skill。
  也用于心跳例行检查中定期查询 DeepSeek 账户余额状态。
---

# DeepSeek 余额查询

## 环境变量

- `DEEPSEEK_API_KEY` — DeepSeek API Key（从环境变量 `DEEPSEEK_API_KEY` 读取，**禁止硬编码**）

## 查询命令

```bash
# 从环境变量读取 key
curl -s -X GET 'https://api.deepseek.com/user/balance' \
  -H 'Accept: application/json' \
  -H "Authorization: Bearer ${DEEPSEEK_API_KEY}"
```

## 响应解析

```json
{
  "is_available": true,
  "balance_infos": [
    {
      "currency": "CNY",
      "total_balance": "69.77",
      "granted_balance": "0.00",
      "topped_up_balance": "69.77"
    }
  ]
}
```

## 输出格式

查询后向用户汇报：
- 状态（是否可用）
- 货币单位
- 总余额
- 赠送余额
- 充值余额

## 调用时机

- 用户明确要求查询 DeepSeek 余额时
- 心跳检查中定期查看 DeepSeek 余额状态时

## 注意事项

- 不需要二次确认，纯查询操作，直接执行
- **禁止硬编码 API Key**，始终从环境变量 `DEEPSEEK_API_KEY` 读取
- 接口免费，无调用次数限制