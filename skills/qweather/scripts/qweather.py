#!/usr/bin/env python3
"""
和风天气 QWeather API 调用脚本
"""
import sys
import requests
import json
from datetime import datetime, timedelta

# API配置
HOST = "na6heya3mr.re.qweatherapi.com"
KEY = "2e5290bfa33242d2bf74ab196aae6e19"
CITY_CODE = "101210101"  # 杭州
LAT, LON = "30.2741", "120.1551"  # 杭州坐标

def get_now():
    """实时天气"""
    url = f"https://{HOST}/v7/weather/now?location={CITY_CODE}&key={KEY}"
    r = requests.get(url, timeout=10)
    return r.json()

def get_7d():
    """7天预报"""
    url = f"https://{HOST}/v7/weather/7d?location={CITY_CODE}&key={KEY}"
    r = requests.get(url, timeout=10)
    return r.json()

def get_24h():
    """24小时逐时预报"""
    url = f"https://{HOST}/v7/weather/24h?location={CITY_CODE}&key={KEY}"
    r = requests.get(url, timeout=10)
    return r.json()

def get_air():
    """空气质量"""
    url = f"https://{HOST}/airquality/v1/current/{LAT}/{LON}?key={KEY}"
    r = requests.get(url, timeout=10)
    return r.json()

def get_warning():
    """天气预警"""
    url = f"https://{HOST}/weatheralert/v1/current/{LAT}/{LON}?key={KEY}"
    r = requests.get(url, timeout=10)
    return r.json()

def get_indices():
    """天气指数"""
    # 使用关键指数类型：舒适度(comf)、穿衣(drsg)、洗车(cw)
    url = f"https://{HOST}/v7/indices/3d?location={CITY_CODE}&key={KEY}&type=1,3,9"
    r = requests.get(url, timeout=10)
    return r.json()

def get_usage():
    """API用量统计"""
    url = f"https://{HOST}/metrics/v1/stats?key={KEY}"
    r = requests.get(url, timeout=10)
    return r.json()

def get_geo(city):
    """城市查询"""
    url = f"https://{HOST}/geo/v2/city/lookup?location={city}&key={KEY}"
    r = requests.get(url, timeout=10)
    return r.json()

def format_weather():
    """组合天气输出"""
    now = get_now()
    d7 = get_7d()
    
    if now.get("code") != "200" or d7.get("code") != "200":
        print("API请求失败")
        return
    
    now_data = now["now"]
    daily = d7["daily"][0]
    
    print(f"实时天气：{now_data['text']} {now_data['temp']}°C")
    print(f"今日气温：{daily['tempMin']}~{daily['tempMax']}°C")
    print(f"湿度：{now_data['humidity']}%")
    print(f"风力：{now_data['windDir']}{now_data['windScale']}级")
    print(f"\n7天预报：")
    for d in d7["daily"][:7]:
        print(f"  {d['fxDate']} {d['textDay']} {d['tempMin']}~{d['tempMax']}°C {d['windDirDay']}{d['windScaleDay']}级")

def format_now():
    """格式化实时天气"""
    now = get_now()
    if now.get("code") != "200":
        print("API请求失败")
        return
    
    data = now["now"]
    print(f"天气：{data['text']}")
    print(f"气温：<font color='FF6B6B'>{data['temp']}°C</font>")
    print(f"体感：<font color='FF6B6B'>{data['feelsLike']}°C</font>")
    print(f"湿度：{data['humidity']}%")
    print(f"风力：{data['windDir']}{data['windScale']}级")

def format_7d():
    """格式化7天预报"""
    d7 = get_7d()
    if d7.get("code") != "200":
        print("API请求失败")
        return
    
    for d in d7["daily"][:7]:
        date_obj = datetime.strptime(d['fxDate'], '%Y-%m-%d')
        weekday = ['周一','周二','周三','周四','周五','周六','周日'][date_obj.weekday()]
        print(f"{d['fxDate']} {weekday} | {d['textDay']} | <font color='FF6B6B'>{d['tempMin']}~{d['tempMax']}°C</font> | {d['windDirDay']}{d['windScaleDay']}级")

def format_24h():
    """格式化24小时逐时"""
    h24 = get_24h()
    if h24.get("code") != "200":
        print("API请求失败")
        return
    
    for h in h24["hourly"][:24]:
        time_str = h['fxTime'][11:16]
        print(f"{time_str} | {h['text']} | <font color='FF6B6B'>{h['temp']}°C</font> | {h['windDir']}{h['windScale']}级")

def format_air():
    """格式化空气质量"""
    air = get_air()
    if "indexes" not in air:
        print("空气质量数据获取失败")
        return
    
    aqi = air["indexes"][0]
    pm2p5 = next((p for p in air.get("pollutants", []) if p["code"] == "pm2p5"), None)
    print(f"🌿 空气质量：AQI {aqi['aqi']} {aqi['category']}")
    if pm2p5:
        print(f"   PM2.5：{pm2p5['concentration']['value']} μg/m³")

def format_warning():
    """格式化天气预警"""
    w = get_warning()
    if "alerts" not in w:
        print("预警数据获取失败")
        return
    
    warnings = w.get("alerts", [])
    if not warnings:
        print("⚠️ 天气预警：当前无预警")
    else:
        for warn in warnings:
            print(f"⚠️ {warn.get('typeName', warn.get('type', ''))} {warn.get('level', '')}预警")
            print(f"   {warn.get('text', '')}")

def format_indices():
    """格式化天气指数"""
    idx = get_indices()
    if idx.get("code") != "200":
        print(f"指数数据获取失败: {idx.get('code')}")
        return
    
    # Group by date
    by_date = {}
    for item in idx.get("daily", []):
        date = item['date']
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(item)
    
    for date, items in sorted(by_date.items()):
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        weekday = ['周一','周二','周三','周四','周五','周六','周日'][date_obj.weekday()]
        print(f"\n【{date} {weekday}】")
        for i in items:
            print(f"  {i['name']}：{i['category']} - {i['text']}")

def format_usage():
    """格式化用量统计"""
    u = get_usage()
    if u.get("code") != "200":
        print("用量统计获取失败")
        return
    
    print(f"今日已用：{u.get('today', 'N/A')} 次")
    print(f"剩余额度：{u.get('remaining', 'N/A')} 次")

def main():
    if len(sys.argv) < 2:
        print("用法: python3 qweather.py <command>")
        print("命令: weather, now, 7d, 24h, air, warning2, indices3, indices, geo <city>, usage")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "weather":
        format_weather()
    elif cmd == "now":
        format_now()
    elif cmd == "7d":
        format_7d()
    elif cmd == "24h":
        format_24h()
    elif cmd == "air":
        format_air()
    elif cmd == "warning2":
        format_warning()
    elif cmd == "indices3":
        format_indices()
    elif cmd == "indices":
        format_indices()
    elif cmd == "geo":
        if len(sys.argv) < 3:
            print("用法: python3 qweather.py geo <城市名>")
            return
        result = get_geo(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif cmd == "usage":
        format_usage()
    else:
        print(f"未知命令: {cmd}")
        print("可用命令: weather, now, 7d, 24h, air, warning2, indices3, indices, geo, usage")

if __name__ == "__main__":
    main()
