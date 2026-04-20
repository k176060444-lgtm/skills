#!/usr/bin/env python3
"""和风天气 QWeather API 调用脚本"""
import sys, urllib.request, gzip, json, datetime, urllib.parse, re, os

API_HOST = os.environ.get("QWEATHER_API_HOST", "")
API_KEY  = os.environ.get("QWEATHER_API_KEY",  "")
DEFAULT_CITY = "101210101"

ENDPOINTS = {
    "now":      "/v7/weather/now",
    "7d":       "/v7/weather/7d",
    "24h":      "/v7/weather/24h",
    "indices":  "/v7/indices/1d?type=1",
    "warning":  "/v7/warning/now",
    "indices3": "/v7/indices/1d?type=2,3,8",
    "indices3d": "/v7/indices/3d?type=2,3,8",
}

ICON_MAP = {
    "100":"☀️","101":"☁️","102":"⛅","103":"☁️","104":"☁️",
    "200":"💨","300":"🌧️","301":"🌧️","302":"🌧️","303":"⛈️","304":"⛈️",
    "305":"🌧️","306":"🌧️","307":"⛈️","308":"⛈️","309":"🌧️",
    "310":"🌧️","311":"🌧️","312":"🌧️","313":"🌨️",
    "400":"❄️","401":"❄️","402":"❄️","403":"❄️","404":"❄️","405":"❄️","406":"🌨️","407":"🌨️",
    "500":"🌫️","501":"🌫️","502":"😷","503":"😷",
}

INDICES_NAMES = {
    "1":"运动","2":"穿衣","3":"感冒","4":"过敏","5":"紫外线",
    "6":"防晒","7":"空气污染扩散","8":"感冒","9":"空调",
    "10":"心情","11":"太阳","12":"被子","13":"换季","14":"钓鱼","15":"旅游","16":"交通",
}

KEY_INDICES_NAMES = {"8":"舒适度指数","3":"穿衣指数","2":"洗车指数"}


def fetch(endpoint):
    if "location=" in endpoint:
        idx = endpoint.index("location=")
        prefix = endpoint[:idx]
        rest = endpoint[idx + len("location="):]
        amp = rest.index("&") if "&" in rest else len(rest)
        loc = rest[:amp]
        suffix = rest[amp:]
        endpoint = prefix + "location=" + urllib.parse.quote(loc) + suffix
    sep = "&" if "?" in endpoint else "?"
    url = "https://{0}{1}{2}key={3}".format(API_HOST, endpoint, sep, API_KEY)
    req = urllib.request.Request(url)
    req.add_header("Accept-Encoding","gzip")
    req.add_header("User-Agent","Mozilla/5.0")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(gzip.decompress(r.read()).decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def fetch_direct(url):
    req = urllib.request.Request(url)
    req.add_header("Accept-Encoding","gzip")
    req.add_header("User-Agent","Mozilla/5.0")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(gzip.decompress(r.read()).decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def fetch_air(lat="30.25", lon="120.15"):
    url = "https://{}/airquality/v1/current/{}/{}/?key={}".format(API_HOST, lat, lon, API_KEY)
    return fetch_direct(url)


def fetch_air_daily(lat="30.25", lon="120.15"):
    """空气质量每日预报（未来3天）"""
    url = "https://{}/airquality/v1/daily/{}/{}/?key={}".format(API_HOST, lat, lon, API_KEY)
    return fetch_direct(url)


def format_air_for_date(data, target_date_str):
    """获取指定日期的空气质量，供weather/tomorrow命令内联使用"""
    if "error" in data: return None
    days = data.get("days", [])
    for d in days:
        start = d.get("forecastStartTime", "")[:10]
        if start == target_date_str:
            indexes = d.get("indexes", [])
            for idx in indexes:
                if idx.get("code") == "cn-mee":
                    aqi = idx.get("aqi", "N/A")
                    cat = idx.get("category", "")
                    effect = idx.get("health", {}).get("effect", "")
                    return "空气质量：AQI " + str(aqi) + " " + cat + "\n  " + effect
            break
    return None


def fetch_warning2(lat="30.25", lon="120.15"):
    url = "https://{}/weatheralert/v1/current/{}/{}/?key={}".format(API_HOST, lat, lon, API_KEY)
    return fetch_direct(url)


def fetch_geo(location, rng="cn", num=3):
    params = urllib.parse.urlencode({"location":location,"range":rng,"number":num,"key":API_KEY})
    url = "https://{}/geo/v2/city/lookup?{}".format(API_HOST, params)
    return fetch_direct(url)


def fetch_usage():
    url = "https://{}/metrics/v1/stats?key={}".format(API_HOST, API_KEY)
    return fetch_direct(url)


def format_now(data, daily_7d=None):
    if "error" in data: return "FAIL: " + data["error"]
    if data.get("code") != "200": return "FAIL: " + data.get("code","") + " " + data.get("message","")
    now = data["now"]
    upd = data.get("updateTime","")[11:16]
    tr = ""
    if daily_7d and daily_7d.get("code") == "200":
        t = daily_7d.get("daily",[{}])[0]
        mn, mx = t.get("tempMin",""), t.get("tempMax","")
        if mn and mx: tr = "<b>" + mn + "~" + mx + "°C</b>"
    if not tr: tr = "<b>" + now.get("temp","") + "°C</b>"
    return "hangzhou实时天气（" + upd + "）\n天气: " + now.get("text","") + "  " + tr + "（体感 <b>" + now.get("feelsLike","") + "°C</b>）\n风向: " + now.get("windDir","") + " " + now.get("windScale","") + "级（" + now.get("windSpeed","") + "km/h）\n湿度: " + now.get("humidity","") + "%\n降水: " + now.get("precip","") + "mm\n气压: " + now.get("pressure","") + "hPa\n能见度: " + now.get("vis","") + "km"


def format_7d(data):
    if "error" in data: return "FAIL: " + data["error"]
    if data.get("code") != "200": return "FAIL: " + data.get("code","") + " " + data.get("message","")
    upd = data.get("updateTime","")[11:16]
    daily = data.get("daily",[])
    wm = ["周一","周二","周三","周四","周五","周六","周日"]
    lines = ["7天预报（" + upd + "）", ""]
    for i, d in enumerate(daily[:7]):
        fx = d.get("fxDate","")
        icon = ICON_MAP.get(d.get("iconDay",""), d.get("textDay",""))
        label = fx[5:].replace("-","月") + "日 " + wm[datetime.date.fromisoformat(fx).weekday()] if fx else str(i)
        lines.append(label + " " + icon + " " + d.get("textDay","") + " <b>" + d.get("tempMin","") + "~" + d.get("tempMax","") + "°C</b> " + d.get("windDirDay","") + d.get("windScaleDay","") + "级 " + d.get("precip","") + "mm")
    return "\n".join(lines)


def format_24h(data):
    if "error" in data: return "FAIL: " + data["error"]
    if data.get("code") != "200": return "FAIL: " + data.get("code","") + " " + data.get("message","")
    upd = data.get("updateTime","")[11:16]
    hourly = data.get("hourly", [])
    lines = ["逐小时预报（" + upd + "）", "", "| 时间 | 天气 | 温度 | 降水 |", "|------|------|------|------|"]
    for h in hourly[:24]:
        fx = h.get("fxTime","")[11:16]
        icon = ICON_MAP.get(h.get("icon",""), h.get("text",""))
        lines.append("| " + fx + " | " + icon + " | <b>" + h.get("temp","") + "°C</b> | " + h.get("precip","0") + "mm |")
    return "\n".join(lines)


def format_air(data):
    if "error" in data: return "FAIL: " + data["error"]
    idxs = data.get("indexes", [])
    pups = data.get("pollutants", [])
    res = []
    for x in idxs:
        if x.get("code") == "cn-mee":
            res.append("空气质量：" + str(x.get("aqi","N/A")) + " " + str(x.get("category","")))
            res.append("  " + x.get("health",{}).get("effect",""))
    for p in pups:
        if p.get("code") == "pm2p5":
            v = p.get("concentration",{}).get("value","N/A")
            u = p.get("concentration",{}).get("unit","")
            aq = (p.get("subIndexes",[{}])[0].get("aqi","N/A") if p.get("subIndexes") else "N/A")
            res.append("  PM2.5：" + str(v) + u + "（AQI " + str(aq) + "）")
            break
    return "\n".join(res)


def format_indices3d(data, target_date=None):
    """格式化3天指数预报，可指定日期或默认今天"""
    if "error" in data: return "FAIL: " + str(data["error"])
    if data.get("code") != "200": return "FAIL: " + data.get("code","") + " " + data.get("message","")
    order = ["8", "3", "2"]
    daily = data.get("daily", [])
    idxd = {d.get("date",""): d for d in daily}

    if target_date:
        # 指定日期的指数
        lines = []
        for t in order:
            for d in daily:
                if d.get("date") == target_date and d.get("type") == t:
                    nm = KEY_INDICES_NAMES.get(t, d.get("name","未知"))
                    lv = d.get("level","")
                    cat = d.get("category","")
                    txt = d.get("text","").split("。")[0] + "。"
                    lines.append("| " + nm + " | " + lv + "级 " + cat + " | " + txt + " |")
                    break
        return lines
    else:
        # 全部3天概览（用于today推送）
        today = datetime.date.today().strftime("%Y-%m-%d")
        lines = ["天气指数（3天）", ""]
        for date_key in [today]:
            day_lines = []
            for t in order:
                for d in daily:
                    if d.get("date") == date_key and d.get("type") == t:
                        nm = KEY_INDICES_NAMES.get(t, d.get("name","未知"))
                        lv = d.get("level","")
                        cat = d.get("category","")
                        txt = d.get("text","").split("。")[0] + "。"
                        day_lines.append("| " + nm + " | " + lv + "级 " + cat + " | " + txt + " |")
                        break
            if day_lines:
                lines.extend(day_lines)
        return lines


def format_indices_for_date(data, target_date):
    """获取指定日期的指数列表（供weather命令内联使用）"""
    if "error" in data: return []
    if data.get("code") != "200": return []
    order = ["8", "3", "2"]
    daily = data.get("daily", [])
    lines = []
    for t in order:
        for d in daily:
            if d.get("date") == target_date and d.get("type") == t:
                nm = KEY_INDICES_NAMES.get(t, d.get("name","未知"))
                lv = d.get("level","")
                cat = d.get("category","")
                txt = d.get("text","").split("。")[0] + "。"
                lines.append("| " + nm + " | " + lv + "级 " + cat + " | " + txt + " |")
                break
    return lines


def format_warning(data):
    if "error" in data: return "FAIL: " + data["error"]
    if data.get("code") != "200": return "FAIL: " + data.get("code","") + " " + data.get("message","")
    upd = data.get("updateTime","")[11:16]
    warns = data.get("warning", [])
    if not warns: return "当前无预警（" + upd + "）"
    lines = ["灾害预警（" + upd + "）", ""]
    for w in warns: lines.append("[" + w.get("level","") + w.get("typeName","") + "] " + w.get("text",""))
    return "\n".join(lines)


def format_warning2(data):
    if "error" in data: return "FAIL: " + str(data["error"])
    if data.get("zeroResult") == True or not data.get("alerts"): return "当前无预警"
    lines = []
    for a in data.get("alerts", []):
        sev = a.get("severity","").upper()
        evt = a.get("eventType",{}).get("name","")
        hl = a.get("headline","")
        ins = a.get("instruction","").split("\n")[0] if a.get("instruction") else ""
        snd = a.get("senderName","")
        exp = a.get("expireTime","")[:10] if a.get("expireTime") else ""
        lines.append("[" + sev + "]" + evt)
        lines.append(hl)
        if ins: lines.append(ins)
        lines.append("来源：" + snd + " | 失效：" + exp)
        lines.append("")
    return "\n".join(lines)


def format_geo(data):
    if "error" in data: return "FAIL: " + str(data["error"])
    if data.get("code") != "200": return "FAIL: " + data.get("code","") + " " + data.get("message","")
    locs = data.get("location", [])
    if not locs: return "未找到该城市"
    lines = []
    for loc in locs:
        nm = loc.get("name","")
        cid = loc.get("id","")
        lat = loc.get("lat","")
        lon = loc.get("lon","")
        adm = loc.get("adm2","") or loc.get("adm1","")
        cty = loc.get("type","")
        lines.append(nm + " (" + cty + ") ID:" + cid + " 坐标:" + lat + "," + lon + " 行政区:" + adm)
    return "\n".join(lines)


def format_usage(data):
    if "error" in data: return "FAIL: " + data["error"]
    as_of = data.get("metadata",{}).get("asOf") or data.get("asOf","")
    if as_of:
        dt = datetime.datetime.strptime(as_of, "%Y-%m-%dT%H:%MZ")
        bj = dt + datetime.timedelta(hours=8)
        cur_h = dt.hour
    else:
        bj = datetime.datetime.now()
        cur_h = (bj - datetime.timedelta(hours=8)).hour
    bj_today = list(range(16,24)) + list(range(0,cur_h+1))
    lines = ["QWeather API 用量统计 截止:" + bj.strftime("%Y-%m-%d %H:%M") + "北京时间", ""]
    total = 0
    for item in data.get("success",[]):
        hrs = item["hours"]
        today = sum(hrs[i] for i in bj_today)
        total += today
        lines.append("OK " + item["api"] + ": 今日" + str(today) + "次")
    lines.append("")
    for item in data.get("errors",[]):
        hrs = item["hours"]
        today = sum(hrs[i] for i in bj_today)
        if today > 0: lines.append("ERR " + item["api"] + ": 今日失败" + str(today) + "次")
    lines.extend(["", "今日已用:" + str(total) + "/1000次", "剩余:" + str(max(0,1000-total)) + "次"])
    return "\n".join(lines)


def format_full():
    """输出完整正确格式的天气推送（2026-04-20确认版）"""
    import re
    loc = DEFAULT_CITY
    d7    = fetch("/v7/weather/7d?location=" + loc)
    nw    = fetch("/v7/weather/now?location=" + loc)
    idx3d = fetch("/v7/indices/3d?location=" + loc + "&type=2,3,8")
    ar    = fetch_air_daily()
    w2    = fetch_warning2()
    today = datetime.date.today().strftime("%Y-%m-%d")

    now_data = nw.get("now", {}) if nw.get("code") == "200" else {}
    daily0   = (d7.get("daily", [])[0] if d7.get("code") == "200" else {})
    temp_min = daily0.get("tempMin", "")
    temp_max = daily0.get("tempMax", "")
    icon_now = ICON_MAP.get(now_data.get("icon", ""), now_data.get("text", ""))

    ar_today = format_air_for_date(ar, today)
    aqi_val, aqi_cat, pm25_val = "N/A", "", "N/A"
    if ar_today:
        m = re.search(r"AQI\s+(\d+)\s+(\S+)", ar_today)
        if m: aqi_val, aqi_cat = m.group(1), m.group(2)
        m2 = re.search(r"PM2\.5：([\d.]+)", ar_today)
        if m2: pm25_val = m2.group(1)

    idx_lines = format_indices_for_date(idx3d, today)
    w2_txt    = format_warning2(w2)

    wm = ["周一","周二","周三","周四","周五","周六","周日"]
    fc_lines = []
    for d in (d7.get("daily", []) if d7.get("code") == "200" else [])[1:4]:
        fx    = d.get("fxDate", "")
        label = fx[5:].lstrip('0').replace("-","月") + "日 " + wm[datetime.date.fromisoformat(fx).weekday()] if fx else ""
        icon  = ICON_MAP.get(d.get("iconDay",""), d.get("textDay",""))
        fc_lines.append(
            "| " + label + " | " + icon + " " + d.get("textDay","")
            + " | " + d.get("tempMin","") + "~" + d.get("tempMax","") + "°C"
            + " | " + d.get("windDirDay","") + d.get("windScaleDay","") + "级 |")

    now_str = (
        "天气：" + icon_now + " " + now_data.get("text","") + "\n"
        "气温：**" + temp_min + "~" + temp_max + "°C**（体感" + now_data.get("feelsLike","") + "°C）\n"
        "湿度：" + now_data.get("humidity","") + "%\n"
        "风力：" + now_data.get("windDir","") + now_data.get("windScale","") + "级（" + now_data.get("windSpeed","") + "km/h）"
    )

    out = []
    out.append("**杭州天气 · " + datetime.datetime.now().strftime("%Y年%-m月%-d日 %H:%M") + "**")
    out.append("**数据来源** QWeather（和风天气）")
    out.append("")
    out.append("**今日概况**")
    out.append(now_str)
    out.append("")
    out.append("🌿 **空气质量**")
    out.append("**AQI " + aqi_val + " " + aqi_cat + "**")
    out.append("PM2.5 " + (pm25_val if pm25_val != "N/A" else "N/A ") + "μg/m³")
    out.append("")
    out.append("📊 **天气指数**")
    out.append("| 指数 | 等级 | 建议 |")
    out.append("|------|------|------|")
    out.extend(idx_lines)
    out.append("")
    out.append("⚠️ **天气预警**")
    out.append(w2_txt)
    out.append("")
    out.append("📅 **未来3天预报**")
    out.append("| 日期 | 天气 | 温度 | 风力 |")
    out.append("|------|------|------|------|")
    out.extend(fc_lines)
    return "\n".join(out)

HELP_API_LIST = "now | 7d | 24h | indices | indices3 | indices3d | air | warning | warning2 | geo | usage | weather | tomorrow | aftertomorrow | fmt"

def main():
    if len(sys.argv) < 2:
        print("用法: python3 qweather.py <接口> [参数]")
        print("接口: " + HELP_API_LIST)
        print("默认城市: " + DEFAULT_CITY + " (杭州)")
        sys.exit(1)

    t = sys.argv[1].lower()

    if t == "usage":
        print("查询用量...", flush=True)
        print(format_usage(fetch_usage()))
        return
    if t == "geo":
        city = sys.argv[2] if len(sys.argv) > 2 else "杭州"
        print("查询城市 " + city + "...", flush=True)
        print(format_geo(fetch_geo(city)))
        return
    if t == "air":
        lat = sys.argv[2] if len(sys.argv) > 2 else "30.25"
        lon = sys.argv[3] if len(sys.argv) > 3 else "120.15"
        print("获取空气质量 " + lat + "," + lon + "...", flush=True)
        print(format_air(fetch_air(lat, lon)))
        return
    if t == "warning2":
        lat = sys.argv[2] if len(sys.argv) > 2 else "30.25"
        lon = sys.argv[3] if len(sys.argv) > 3 else "120.15"
        print("获取预警 " + lat + "," + lon + "...", flush=True)
        print(format_warning2(fetch_warning2(lat, lon)))
        return
    if t == "weather":
        loc = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CITY
        print("获取 " + loc + " 7d...", flush=True)
        d7 = fetch("/v7/weather/7d?location=" + loc)
        print("获取 " + loc + " now...", flush=True)
        nw = fetch("/v7/weather/now?location=" + loc)
        print("获取 " + loc + " indices3d...", flush=True)
        idx3d = fetch("/v7/indices/3d?location=" + loc + "&type=2,3,8")
        print("获取 " + loc + " air daily...", flush=True)
        ar = fetch_air_daily()
        print("获取 " + loc + " warning2...", flush=True)
        w2 = fetch_warning2()
        today = datetime.date.today().strftime("%Y-%m-%d")
        # 空气质量日报forecastStartTime是UTC，days[0]对应北京当天夜里(=API日期+1)
        air_today = format_air_for_date(ar, today)
        print(format_now(nw, d7))
        print()
        print(format_7d(d7))
        print()
        air_today = format_air_for_date(ar, (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
        print(air_today if air_today else "空气质量：暂无数据")
        print()
        print("天气指数", "", "| 指数 | 等级 | 建议 |", "|------|------|------|", "\n".join(format_indices_for_date(idx3d, today)), sep="\n")
        print()
        print(format_warning2(w2))
        return
    if t == "fmt":
        print(format_full())
        return
    if t == "tomorrow":
        loc = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CITY
        tomorrow_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        print("获取 " + loc + " 7d...", flush=True)
        d7 = fetch("/v7/weather/7d?location=" + loc)
        print("获取 " + loc + " indices3d...", flush=True)
        idx3d = fetch("/v7/indices/3d?location=" + loc + "&type=2,3,8")
        print("获取 " + loc + " air daily...", flush=True)
        ar = fetch_air_daily()
        print("获取 " + loc + " warning2...", flush=True)
        w2 = fetch_warning2()
        # 格式化明天天气
        daily = d7.get("daily", []) if d7.get("code") == "200" else []
        wm = ["周一","周二","周三","周四","周五","周六","周日"]
        tomorrow_entry = None
        for d in daily:
            if d.get("fxDate","") == tomorrow_date:
                tomorrow_entry = d
                break
        if tomorrow_entry:
            fx = tomorrow_entry.get("fxDate","")
            icon = ICON_MAP.get(tomorrow_entry.get("iconDay",""), tomorrow_entry.get("textDay",""))
            label = fx[5:].replace("-","月") + "日 " + wm[datetime.date.fromisoformat(fx).weekday()] if fx else ""
            print("杭州天气 · " + label)
            print("数据来源：QWeather（和风天气）")
            print()
            print("明日概况：" + icon + " " + tomorrow_entry.get("textDay","") + "，<b>" + tomorrow_entry.get("tempMin","") + "~" + tomorrow_entry.get("tempMax","") + "°C</b>，" + tomorrow_entry.get("windDirDay","") + tomorrow_entry.get("windScaleDay","") + "级")
        else:
            print("无法获取明日天气数据")
            return
        print()
        air_tomorrow = format_air_for_date(ar, tomorrow_date)
        print(air_tomorrow if air_tomorrow else "空气质量：暂无数据")
        print()
        print("天气指数", "", "| 指数 | 等级 | 建议 |", "|------|------|------|", "\n".join(format_indices_for_date(idx3d, tomorrow_date)), sep="\n")
        print()
        print(format_warning2(w2))
        return
    if t == "aftertomorrow":
        loc = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CITY
        after_date = (datetime.date.today() + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        print("获取 " + loc + " 7d...", flush=True)
        d7 = fetch("/v7/weather/7d?location=" + loc)
        print("获取 " + loc + " indices3d...", flush=True)
        idx3d = fetch("/v7/indices/3d?location=" + loc + "&type=2,3,8")
        print("获取 " + loc + " air daily...", flush=True)
        ar = fetch_air_daily()
        print("获取 " + loc + " warning2...", flush=True)
        w2 = fetch_warning2()
        # 格式化后天天气
        daily = d7.get("daily", []) if d7.get("code") == "200" else []
        wm = ["周一","周二","周三","周四","周五","周六","周日"]
        after_entry = None
        for d in daily:
            if d.get("fxDate","") == after_date:
                after_entry = d
                break
        if after_entry:
            fx = after_entry.get("fxDate","")
            icon = ICON_MAP.get(after_entry.get("iconDay",""), after_entry.get("textDay",""))
            label = fx[5:].replace("-","月") + "日 " + wm[datetime.date.fromisoformat(fx).weekday()] if fx else ""
            print("杭州天气 · " + label)
            print("数据来源：QWeather（和风天气）")
            print()
            print("概况：" + icon + " " + after_entry.get("textDay","") + "，<b>" + after_entry.get("tempMin","") + "~" + after_entry.get("tempMax","") + "°C</b>，" + after_entry.get("windDirDay","") + after_entry.get("windScaleDay","") + "级")
        else:
            print("无法获取后天天气数据")
            return
        print()
        air_after = format_air_for_date(ar, after_date)
        print(air_after if air_after else "空气质量：暂无预报")
        print()
        print("天气指数", "", "| 指数 | 等级 | 建议 |", "|------|------|------|", "\n".join(format_indices_for_date(idx3d, after_date)), sep="\n")
        print()
        print(format_warning2(w2))
        return
    if t not in ENDPOINTS:
        print("未知接口: " + t)
        print("可用: " + HELP_API_LIST)
        sys.exit(1)

    loc = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CITY
    ep = ENDPOINTS[t]
    print("获取 " + loc + " " + t + "...", flush=True)
    data = fetch(ep + ("&" if "?" in ep else "?") + "location=" + loc)

    if t == "now": print(format_now(data))
    elif t == "7d": print(format_7d(data))
    elif t == "24h": print(format_24h(data))
    elif t == "indices": print("生活指数（需配合城市代码使用）")
    elif t == "indices3": print(format_indices3(data))
    elif t == "indices3d": print("\n".join(format_indices3d(data)))
    elif t == "warning": print(format_warning(data))
    else: print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
