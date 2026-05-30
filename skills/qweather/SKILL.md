---
name: qweather
description: 和风天气 QWeather API 调用。当用户查询天气、获取天气预报（今日/7天/24小时）、空气质量、天气指数等与天气相关请求时使用此技能。支持城市代码/城市名/经纬度定位。注意：仅在用户明确要求使用和风天气或需要免费API天气数据时使用，否则默认用 agent-browser + weather.com.cn。
---

# 和风天气 QWeather API

## 快速使用

```bash
# 实时天气（默认杭州）
python3 ~/.openclaw/workspace/skills/qweather/scripts/qweather.py now

# 7天预报
python3 ~/.openclaw/workspace/skills/qweather/scripts/qweather.py 7d

# 24小时逐时
python3 ~/.openclaw/workspace/skills/qweather/scripts/qweather.py 24h

# 生活指数
python3 ~/.openclaw/workspace/skills/qweather/scripts/qweather.py indices

# 灾害预警
python3 ~/.openclaw/workspace/skills/qweather/scripts/qweather.py warning

# API 用量查询
python3 ~/.openclaw/workspace/skills/qweather/scripts/qweather.py usage

# 指定城市（城市代码）
python3 ~/.openclaw/workspace/skills/qweather/scripts/qweather.py now 101210101
```

## 支持接口

| 接口 | 说明 | 示例 |
|------|------|------|
| `now` | 实时天气 | 温度/风力/湿度/降水等 |
| `7d` | 7天预报 | 每日高低温/天气/风力 |
| `24h` | 24小时逐时 | 每小时温度/天气 |
| `indices` | 生活指数 | 穿衣/紫外线/运动等 |
| `warning` | 灾害预警 | 蓝/黄/橙/红色预警 |
| `usage` | API用量统计 | 今日已用/剩余额度 |

## 常用城市代码

| 城市 | 代码 |
|------|------|
| 杭州 | 101210101 |
| 上海 | 101020100 |
| 北京 | 101010100 |
| 深圳 | 101280601 |
| 广州 | 101280101 |
| 成都 | 101270101 |
| 南京 | 101190101 |
| 苏州 | 101190401 |
| 宁波 | 101210401 |
| 厦门 | 101230201 |

其他城市代码查询：https://dev.qweather.com/docs/api/geo/

## API 配置

- **Host**: `na6heya3mr.re.qweatherapi.com`
- **Key**: `2e5290bfa33242d2bf74ab196aae6e19`
- **协议**: HTTPS + Gzip压缩
- **用量查询**: `GET /metrics/v1/stats?key=<KEY>`（用 query 参数，不用 Authorization header）

## 天气推送格式规范

### 推送结构（7个部分，严格按顺序）

1. **标题栏**：杭州天气 · {月}{日} {星期几}
2. **今日概况**：天气/气温/湿度/风力（每项单独换行）
3. **空气质量**：AQI + PM2.5（按等级着色）
4. **天气指数**：Markdown 表格（舒适度/穿衣/洗车）
5. **天气预警**：有无预警
6. **未来3天预报**：Markdown 表格
7. **小贴士**：可选，简短实用建议

### 日期格式
- 格式：`{月}{日} {星期几}`，例如 `05月29日 周五`
- 禁止使用"今天/明天/后天"

### 温度颜色
- 今日/明日温度：钴蓝色加粗 `<font color="#1E90FF"><b>20~28°C</b></font>`
- 未来3天温度：普通文本，不加粗不加颜色

### 空气质量颜色
- 优 → 翡翠亮加粗 `<font color="#50FA7B"><b>AQI XX 优</b></font>`
- 良 → 普通文本，不加粗不加色
- 轻度污染 → 橙色加粗 `<font color="#FFA500"><b>轻度污染</b></font>`
- 中度污染 → 橙红加粗 `<font color="#FF6347"><b>中度污染</b></font>`
- 重度污染 → 红色加粗 `<font color="#FF0000"><b>重度污染</b></font>`
- 严重污染 → 深红加粗 `<font color="#CC0000"><b>严重污染</b></font>`

### 天气 Emoji 对照
| 天气 | Emoji |
|------|-------|
| 晴 | ☀️ |
| 多云 | ⛅ |
| 阴天 | 🌥️ |
| 小雨 | 🌧️ |
| 中雨 | 🌧️ |
| 大雨 | 🌧️ |
| 雷阵雨 | ⛈️ |
| 雾 | 🌫️ |

### 格式铁律
1. 指数必须用 Markdown 表格，禁止竖线分隔
2. 未来3天必须用 Markdown 表格，禁止竖线分隔
3. 今日概况每项单独换行
4. 禁止使用 HTML 标签（手机 QQ 不支持渲染，颜色标签仅电脑端可见）

## 注意事项

- 免费版每日 1000 次调用额度，非商业使用
- 返回数据需注明来源：QWeather（和风天气）
- Key 有域名/IP安全限制，如更换服务器需更新白名单
- 实时天气更新延迟约 5-10 分钟
- 用量统计接口（usage）使用 `?key=` query 参数，不是 Bearer Token
