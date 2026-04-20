---
name: xianyu-scraper
description: 高反爬网站 Playwright 爬取技能。收到闲鱼/淘宝/拼多多等链接后，使用此技能绕过检测并提取页面内容。
---

# 高反爬网站 Playwright 爬取

遇到高反爬网站时，使用 Playwright + 最简反检测脚本绕过自动化检测。

## 核心原则

**只用最简反检测脚本，不要加任何额外伪造代码！**

- UA/locale/timezone 正常设置即可
- **核心反检测只有一行**：`delete navigator.__proto__.webdriver;`
- 关键参数：`--disable-blink-features=AutomationControlled`

**禁止使用的复杂伪造（会导致 React 报错 `a.addEventListener is not a function`）：**
- `window.chrome = {...}` （伪造 Chrome 对象）
- `navigator.plugins = [...]` （伪造插件列表）
- `navigator.mimeTypes = [...]` （伪造 MIME 类型）
- `navigator.connection = {...}` （伪造网络信息）

## 使用方法

```bash
python3 ~/.openclaw/workspace/skills/xianyu-scraper/scripts/scrape.py '<URL>'
python3 ~/.openclaw/workspace/skills/xianyu-scraper/scripts/scrape.py '<URL>' --scroll 10 --output /tmp/result.txt
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `url` | （必填） | 目标 URL |
| `--scroll` | 10 | 滚动次数，模拟人类浏览 |
| `--timeout` | 35000 | 超时毫秒 |
| `--output` / `-o` | （打印到stdout） | 输出文件路径 |

## 执行示例

```bash
# 闲鱼商品
python3 ~/.openclaw/workspace/skills/xianyu-scraper/scripts/scrape.py 'https://m.tb.cn/h.xxx?tk=xxxx'

# 保存到文件
python3 ~/.openclaw/workspace/skills/xianyu-scraper/scripts/scrape.py 'https://m.tb.cn/h.xxx' -o /tmp/xianyu.txt
```

## 依赖安装

```bash
pip install playwright
playwright install chromium
```

## 已知有效网站

| 网站 | 状态 | 备注 |
|------|------|------|
| 闲鱼 (goofish.com) | ✅ | 直接访问商品详情 |
| 淘宝 (taobao.com) | ✅ | 同理 |
| m.tb.cn 短链 | ✅ | Playwright 自动跳转 |

## 常见问题

**Q: 仍然被检测为机器人？**
A: 检查是否用了复杂伪造脚本，删掉所有伪造代码，只保留最简一行。

**Q: 页面显示登录墙但内容在下方？**
A: 登录墙只是遮罩，商品内容在页面 DOM 里仍然存在；用逐步滚动探索。
