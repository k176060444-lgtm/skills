---
name: taobao-scraper
description: 淘宝/天猫商品爬取技能。用于抓取淘宝、天猫商品详情页信息，支持PC端链接和手机端分享短链。需登录淘宝账号才能获取商品详情。
---

# 淘宝/天猫商品爬取

## 链接类型

| 类型 | URL 格式 | 页面版本 |
|------|---------|---------|
| PC 端链接 | `https://detail.tmall.com/item.htm?id=XXX` | PC 版 |
| 手机分享链接 | `https://e.tb.cn/h.XXXXX` | H5 移动版 |

两种链接**都需要登录**才能看商品详情，登录态 session 共用。

## 工具优先级

1. **agent-browser**（首选，有 Accessibility Tree，支持截图）
2. **Playwright**（备选，反检测更强时用）
3. **nodriver**（终极方案，agent-browser 被识别时用）

## 标准流程

### 情况 A：有登录态 session

```bash
# 直接访问商品页
agent-browser navigate "<商品URL>"

# 提取商品信息
agent-browser snapshot

# 截图辅助分析
agent-browser screenshot /tmp/taobao_product.png
```

### 情况 B：无登录态 session（首次访问 / session 过期）

```bash
# 1. 打开淘宝登录页
agent-browser navigate "https://login.taobao.com/member/login.jhtml"

# 2. 截图二维码
agent-browser screenshot /tmp/taobao_qr.png

# 3. 复制到 QQ 媒体目录
cp /tmp/taobao_qr.png ~/.openclaw/media/qqbot/taobao_qr.png

# 4. 用 qqmedia 标签发送给用户
# <qqmedia>/root/.openclaw/media/qqbot/taobao_qr.png</qqmedia>

# 5. 用户扫码后检测 URL 跳转
agent-browser snapshot
# 成功标志：URL 从 login 页面跳转到 i.taobao.com

# 6. 登录成功后访问目标商品页
agent-browser navigate "<商品URL>"

# 7. 提取信息 + 截图
agent-browser snapshot
agent-browser screenshot /tmp/taobao_product.png
```

## 信息提取

登录成功后，用 `agent-browser snapshot` 获取页面内容，关注以下信息：

- **商品标题**：页面顶部大标题
- **价格**：¥ 开头的数字
- **店铺名称**：店铺信息区域
- **商品规格**：SKU 选项（颜色、版本、容量等）
- **用户评价**：评价内容和评分
- **优惠信息**：券、立减、补贴等

## 关键经验

1. **二维码会过期** — 每次截图都是新二维码，要尽快发送给用户扫码
2. **session 保持** — agent-browser 的登录态在整个会话期间有效，扫一次码后可多次访问不同商品
3. **短链自动跳转** — `e.tb.cn` 短链会自动重定向到商品详情页，无需手动解析
4. **两种链接都需登录** — 不要以为短链就能免登录访问
5. **cookie 持久化** — 目前 session 仅在 agent-browser 进程存活期间有效，重启后需重新登录
6. **发送图片用 qqmedia** — QQ Bot 发送图片必须用 `<qqmedia>` 标签，文件放在 `~/.openclaw/media/qqbot/` 目录

## 禁止事项

- 不得在未获取登录态时直接尝试访问商品页（会跳转到登录页）
- 不得发送过期的二维码给用户
- 不得在 session 失效后继续尝试访问（应重新登录）
- 不得使用旧的/记忆中的脚本，严格按本 SKILL.md 执行

## 相关技能

- `xianyu-scraper` — 闲鱼商品爬取（反检测更复杂）
