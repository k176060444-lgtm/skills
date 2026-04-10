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

**第1部分 - 标题**
```
杭州天气 · Y年M月D日 HH:mm
数据来源：QWeather（和风天气）
```

**第2部分 - 今日概况**（直接段落，无列表符号）
```
天气：
气温：必须显示范围（最低~最高°C，如16~22°C）
湿度：
风力：
```

**第3部分 - 空气质量**
```
🌿 空气质量：AQI数值 等级
   PM2.5：浓度（AQI 数值）
```

**第4部分 - 天气指数**（Markdown表格）
```
📊 天气指数

| 指数 | 等级 | 建议 |
|------|------|------|
| 舒适度指数 | 1级 舒适 | 白天不太热也不太冷… |
| 穿衣指数 | 4级 较舒适 | 建议着薄外套… |
| 洗车指数 | 2级 较适宜 | 较适宜洗车… |
```

**第5部分 - 天气预警**
```
⚠️ 天气预警：当前无预警
（有预警时显示详情）
```

**第6部分 - 未来3天预报**（Markdown表格）
```
📅 未来3天预报

| 日期 | 天气 | 温度 | 风力 |
|------|------|------|------|
| 04月09日 周四 | ☁️多云 | 20~31°C | 西南风1-3级 |
| 04月10日 周五 | ☁️多云 | 18~27°C | 东北风1-3级 |
| 04月11日 周六 | ⛈️大雨 | 13~17°C | 东风1-3级 |
```

### 日期格式说明
- 今日预报：从weather命令的7天预报取第1天
- 未来3天：从weather命令的7天预报取第2-4天
- 日期格式：04月10日 周五（几月几日 周几）

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
