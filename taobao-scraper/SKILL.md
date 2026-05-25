---
name: taobao-scraper
description: 淘宝/天猫商品搜索与详情页爬取技能。使用 nodriver（反检测浏览器自动化）绕过反爬，支持关键词搜索和商品链接详情抓取。触发词：淘宝搜索、淘宝爬取、淘宝商品、天猫商品、抓取淘宝。
---

# 淘宝爬取（nodriver 反检测浏览器）

使用 nodriver 直连 Chrome DevTools，绕过淘宝多层反爬机制。

## 核心原理

nodriver 不走 WebDriver/Playwright 中间层，WebSocket 直连 Chrome，`navigator.webdriver` 默认 `false`，通过淘宝第1层反爬检测。

## 前置依赖

- nodriver：`/root/.openclaw/workspace/venvs/nodriver-env/bin/python3`
- Chromium：系统已安装
- 登录态：首次需扫码，之后自动复用

## 使用方法

```bash
PYTHON=/root/.openclaw/workspace/venvs/nodriver-env/bin/python3

# 首次登录（截取二维码，等待扫码）
$PYTHON ~/.openclaw/workspace/skills/taobao-scraper/scripts/scrape.py --login

# 搜索商品
$PYTHON ~/.openclaw/workspace/skills/taobao-scraper/scripts/scrape.py --search "8600t"

# 商品详情页（支持短链）
$PYTHON ~/.openclaw/workspace/skills/taobao-scraper/scripts/scrape.py --url "https://e.tb.cn/h.xxx?tk=xxx"

# 搜索 + 保存截图
$PYTHON ~/.openclaw/workspace/skills/taobao-scraper/scripts/scrape.py --search "8600t" --screenshot /tmp/result.png

# 搜索 + 保存文本
$PYTHON ~/.openclaw/workspace/skills/taobao-scraper/scripts/scrape.py --search "8600t" --output /tmp/result.txt
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `--login` | 首次扫码登录模式，截取二维码并等待扫码 |
| `--search KEYWORD` | 搜索关键词 |
| `--url URL` | 商品详情页链接（支持短链 e.tb.cn） |
| `--screenshot PATH` | 保存截图到指定路径 |
| `--output PATH` | 保存文本到指定路径（默认输出到 stdout） |
| `--profile DIR` | 自定义 cookie 持久化目录（默认 taobao_profile） |
| `--wait SECONDS` | 页面等待时间（默认 10 秒） |

## 执行流程

```
启动浏览器（固定 user_data_dir）
    ↓
检查登录态（cookie 中有 cookie1/unb？）
    ├─ 有 → 跳过登录
    └─ 无 → 打开登录页 → 截取二维码 → 等待扫码
    ↓
访问目标页面（搜索/商品详情）
    ↓
处理"确认登录"弹窗（自动点击"快速进入"）
    ↓
等待 JS 渲染（默认 10 秒）
    ↓
滚动触发懒加载（5 次，每次 500px）
    ↓
提取文本 + 截图
    ↓
输出结果
```

## 淘宝反爬机制

| 层级 | 检测内容 | 应对方式 |
|------|---------|---------|
| 1 | navigator.webdriver | nodriver 默认 false |
| 2 | 异常流量/验证码 | 持久化 user_data_dir |
| 3 | 搜索 API 签名验证 | 登录态获取 _m_h5_tk |
| 4 | 登录态要求 | 扫码登录 + cookie 持久化 |
| 5 | "确认登录"弹窗 | 自动点击"快速进入" |

## 核心铁律

1. **同一实例内完成全流程**：登录→搜索→商品详情，不能重启浏览器
2. **固定 user_data_dir**：登录一次长期复用，不删除目录
3. **重启后自动处理弹窗**：点击"快速进入"恢复登录态
4. **等待不能省**：JS 渲染需要 8-10 秒
5. **短链需等待跳转**：e.tb.cn 会跳转到 detail.tmall.com

## cookie 持久化目录

默认：`/root/.openclaw/workspace/taobao_profile`

首次登录后，cookie 自动保存到此目录。后续启动浏览器时自动加载，无需重复登录。

cookie 有效期约 30 天（淘宝标准），过期后需重新扫码登录。

## 天猫支持

天猫和淘宝共用同一套阿里账号体系，登录态通用。

| 链接类型 | 示例 | 处理方式 |
|----------|------|----------|
| 淘宝短链 | `e.tb.cn/h.xxx` | 直接使用，自动跳转 |
| 天猫短链（手机） | `m.tb.cn/h.xxx` | 需转换为桌面版URL（见下方） |
| 天猫桌面版 | `detail.tmall.com/item.htm?id=xxx` | 直接使用 |

### 手机天猫链接处理

手机天猫链接 `m.tb.cn` 会跳转到 `tmallx.tmall.com` 移动版页面（Weex渲染），文本提取为空。

解决方法：从跳转URL中提取商品ID，转换为桌面版URL：

```
原始: https://m.tb.cn/h.ReaWCpw?tk=xxx
跳转: https://tmallx.tmall.com/...?id=711000627403&...
转换: https://detail.tmall.com/item.htm?id=711000627403
```

脚本已内置此转换逻辑（自动从移动版URL提取ID，转为桌面版访问）。

## 已知问题

- headless 模式下偶发验证码（概率低，用持久化目录可避免）
- 淘宝/天猫页面结构可能变化，选择器需定期检查
- 商品详情页的价格可能需要滚动到特定位置才渲染
- 手机天猫链接（m.tb.cn）需转换为桌面版，移动版页面无法提取文本
