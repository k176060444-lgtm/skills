---
name: qweather
description: 和风天气 QWeather API 调用。当用户查询天气、获取天气预报（今日/7天/24小时）、空气质量、天气预警、天气指数、城市查询等与天气相关请求时使用此技能。
---

# 和风天气 QWeather API

## 快速使用

```bash
# 组合命令（推荐）：实时天气 + 今日温度范围 + 7天预报
python3 ~/.openclaw/workspace/skills/qweather/scripts/qweather.py weather

# 实时天气（需配合7d获取温度范围）
python3 ~/.openclaw/workspace/skills/qweather/scripts/qweather.py now

# 7天预报
python3 ~/.openclaw/workspace/skills/qweather/scripts/qweather.py 7d

# 24小时逐时预报
python3 ~/.openclaw/workspace/skills/qweather/scripts/qweather.py 24h

# 空气质量（AQI + PM2.5）
python3 ~/.openclaw/workspace/skills/qweather/scripts/qweather.py air

# 天气预警
python3 ~/.openclaw/workspace/skills/qweather/scripts/qweather.py warning2

# 天气指数（舒适度、穿衣、洗车）
python3 ~/.openclaw/workspace/skills/qweather/scripts/qweather.py indices3

# 城市查询（返回城市ID和坐标）
python3 ~/.openclaw/workspace/skills/qweather/scripts/qweather.py geo 北京

# API用量统计
python3 ~/.openclaw/workspace/skills/qweather/scripts/qweather.py usage
```

## 支持接口

| 接口 | 说明 | 输出内容 |
|------|------|---------|
| `weather` | 组合命令 | 实时天气（含今日温度范围）+ 7天预报 |
| `now` | 实时天气 | 温度/风力/湿度等（单一温度） |
| `7d` | 7天预报 | 每日高低温/天气/风力 |
| `24h` | 24小时逐时 | 每小时天气/温度/降水 |
| `air` | 空气质量 | AQI/PM2.5 |
| `warning2` | 天气预警 | 预警类型/级别/防御指南 |
| `indices3` | 关键指数 | 舒适度指数、穿衣指数、洗车指数 |
| `indices` | 全部生活指数 | 16种生活指数 |
| `geo` | 城市查询 | 城市ID和坐标 |
| `usage` | API用量统计 | 今日已用/剩余额度 |

## 推送天气标准格式

用户要求推送天气时，严格按以下格式输出：

**第1部分 - 标题栏**
```
杭州天气 · {月}{日} {星期几}
数据来源：QWeather（和风天气）
```

**第2部分 - 今日概况**（每项单独换行）
```
天气：{emoji}{天气描述}
气温：<font color="#1E90FF"><b>{最低}~{最高}°C</b></font>（体感 {XX}°C）
湿度：{XX}%
风力：{风向} {级别}（{XX}km/h）
```

**第3部分 - 空气质量**（"空气质量："保持原样，后面内容按等级着色加粗）
```
空气质量：<font color="#50FA7B"><b>AQI {XX} 优，PM2.5 {XX}μg/m³</b></font>
```
颜色规则：
- 优 → 翡翠亮加粗 `#50FA7B`
- 良 → 普通文本，不加粗不加色
- 轻度污染 → 橙色加粗 `#FFA500`
- 中度污染 → 橙红加粗 `#FF6347`
- 重度污染 → 红色加粗 `#FF0000`
- 严重污染 → 深红加粗 `#CC0000`

**第4部分 - 天气指数**（必须用Markdown表格，禁止竖线分隔）
```
| 指数 | 等级 | 建议 |
|------|------|------|
| 舒适度指数 | {等级} | {建议} |
| 穿衣指数 | {等级} | {建议} |
| 洗车指数 | {等级} | {建议} |
```

**第5部分 - 天气预警**
```
当前无预警。
（有预警时显示详情）
```

**第6部分 - 未来3天预报**（必须用Markdown表格，从明天起连续3天，温度用普通文本，不加颜色不加粗）
```
| 日期 | 天气 | 温度 | 风力 |
|------|------|------|------|
| {月}{日} {星期几} | {emoji}{天气} | {温度范围} | {风力} |
| {月}{日} {星期几} | {emoji}{天气} | {温度范围} | {风力} |
| {月}{日} {星期几} | {emoji}{天气} | {温度范围} | {风力} |
```

**第7部分 - 小贴士**（可选，根据天气情况给出简短实用建议）

### 日期格式说明
- 日期格式：{月}{日} {星期几}，例如"05月29日 周五"，不用"今天/明天/后天"
- 今日预报：从weather命令的7天预报取第1天
- 未来3天：从weather命令的7天预报取第2-4天

### 天气 Emoji 对照表
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
1. 今日气温用加粗+钴蓝色：`<font color="#1E90FF"><b>19~29°C</b></font>`
2. 未来3天预报的温度用普通文本，不加粗、不加颜色
3. 指数必须用Markdown表格，禁止竖线分隔
4. 未来3天必须用Markdown表格，禁止竖线分隔
5. 今日概况每项单独换行
6. "空气质量："保持原样，后面内容按等级着色加粗

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

其他城市：`python3 qweather.py geo <城市名>`

## API配置

- **Host**: `na6heya3mr.re.qweatherapi.com`
- **Key**: `2e5290bfa33242d2bf74ab196aae6e19`
- **免费额度**: 每日1000次
- **天气预警API**: `/weatheralert/v1/current/{lat}/{lon}?key=` （无需JWT）
- **空气质量API**: `/airquality/v1/current/{lat}/{lon}?key=` （无需JWT）
- **用量查询**: `/metrics/v1/stats?key=` （用query参数，非Bearer Token）
