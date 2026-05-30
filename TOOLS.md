# TOOLS.md - Local Notes

## 🖥️ OpenClaw Gateway 管理命令

**用户手动重启 Gateway**：
```bash
systemctl restart openclaw-gateway
```

**AI 重启 Gateway（在 Gateway 进程内部执行时，禁止直接用 restart）**：
```bash
# 正确方式：通过 systemd-run 脱离 Gateway 进程上下文
systemd-run --unit=gateway-restart --on-active=3s systemctl restart openclaw-gateway

# 备用方式：nohup 延迟执行
nohup bash -c "sleep 3; systemctl restart openclaw-gateway" &
```

**查看状态**：
```bash
systemctl status openclaw-gateway
openclaw status
```

**服务名**：`openclaw-gateway.service`（systemd 注册名）

**⚠️ AI 执行环境警告**：
- 用户 SSH 手动重启：直接执行 `systemctl restart openclaw-gateway` 完全正常，不受影响
- AI 在 Gateway 进程内部：禁止直接执行 `systemctl restart`（会导致自杀 loop）
  - 原因：Gateway 收到 SIGTERM 后要等 AI 子进程结束才退出，systemd 以为停了就开始新进程，新进程发现端口被占退出 78，Restart=always 触发死循环
  - 正确方式：通过 `systemd-run` 或 `nohup` 在独立上下文中执行

---

## Minimax 用量查询

**正确方式（mmx CLI，不需要 API Key）：**
```bash
mmx quota show
```

**⚠️ 字段含义（必须严格遵守，禁止凭直觉解读）：**
- `current_interval_total_count` = 当前时间窗口**总配额**
- `current_interval_usage_count` = 当前时间窗口**剩余配额**（⚠️ 注意：字段名虽含"usage"，但在此接口中实际代表剩余配额！）
- **已用量 = 总配额 - usage_count**
- 当 `total_count = 0` 且 `weekly_total_count = 0` 时 = **无限制**

**示例解读：**
```
窗口总配额: 600 条（来自 current_interval_total_count）
已用量: 总配额 - usage_count
剩余配额: usage_count 条（⚠️ 字段名虽含 usage，实际是剩余量）
```

**⚠️ 铁律**：每次用量查询，必须先引用此字段说明再解读数据，绝对禁止凭直觉直接报。

## Minimax 图像生成（文生图）

**API 端点**：`POST https://api.minimaxi.com/v1/image_generation`

**Key**：付费 Key 从 `~/.openclaw/.env` 中读取 `MINIMAX_PAY_API_KEY`

**🔒 铁律：使用付费 Key 必须获得用户二次确认，绝不能私自调用**
- 收到生图请求 → 汇报计划 → 等用户说"可以" → 才执行
- 执行后汇报结果

**调用方法（curl 直调，不走 mmx CLI）**：
```bash
curl -s -X POST "https://api.minimaxi.com/v1/image_generation" \
  -H "Authorization: Bearer $MINIMAX_PAY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "image-01",
    "prompt": "你的提示词",
    "aspect_ratio": "16:9",
    "response_format": "base64",
    "n": 1
  }' | python3 -c "
import sys, json, base64
d = json.load(sys.stdin)
b64 = d['data']['image_base64'][0]
img = base64.b64decode(b64)
with open('/tmp/output.jpg', 'wb') as f:
    f.write(img)
print('Done,', len(img), 'bytes')
"
```

**参数说明**：
- `model`：必填，`image-01`（或 `image-01-live`）
- `prompt`：最长 1500 字符
- `aspect_ratio`：1:1 / 16:9 / 4:3 / 3:2 / 2:3 / 3:4 / 9:16 / 21:9
- `response_format`：必填 `base64`（url 格式的 OSS 链接国内会 403）
- `n`：1~9，默认 1

**mmx CLI 不可用原因**：`mmx` CLI 是专为 Token Plan 套餐设计的客户端，会自动检查账户套餐等级（需 Plus 或以上）才能调用 `image-01`。但直接 curl 调用 API 不经过 mmx CLI 的套餐等级检查，可以正常出图。两者用的是同一个模型和 Key，只是访问路径不同。

---

## mota 生图（ModelScope 文生图）
**触发词**：mota生图、生成图片、画一张
**技能**：`modelscope-image-gen`
**脚本**：`python3 ~/.openclaw/workspace/skills/modelscope-image-gen/scripts/generate.py --prompt "提示词" --output /tmp/xxx.png`
**模型**：Qwen/Qwen-Image-2512
**Key**：已内置在脚本中，直接用即可

## Minimax 网络搜索

**搜索命令（使用 mmx CLI）：**
```bash
mmx search query --q "<搜索内容>"
```

**示例：**
```bash
mmx search query --q "今日要闻"
mmx search query --q "杭州天气"
```

**注意**：
- `mmx search query` 直接调用 MiniMax 搜索 API，稳定快速
- 不再依赖 minimax-web-search 技能（MCP 架构不稳定）

## Minimax 图像理解

**使用 mmx CLI：**
```bash
mmx vision describe --image <图片路径> --prompt "<提示词>"
```

**示例：**
```bash
mmx vision describe --image /root/photo.png --prompt "描述这张图片"
```

**备选方案（内置 image 工具）：**
- 直接发图片给马蹄，自动调用内置 image 工具
- 内置工具直接走 API，无需额外进程

## Minimax 音乐生成

```bash
mmx music generate --prompt "<提示词>"
```

## Minimax 视频生成

```bash
mmx video generate --prompt "<提示词>"
```

## Prompt Enhancer 技能

**功能**：将粗糙输入优化为结构化 Prompt

**触发方式**：消息前加 `p:` 或 `p-`

**示例**：
```
p:帮我写一个Python脚本
p-解释一下量子计算

## 图片理解首选方案（按稳定性排序）

1. **`mmx vision describe`** - mmx CLI，最稳定 ✅
2. **直接发图给我** - 内置 image 工具，自动触发
3. **其他方式** - 不推荐

## 搜索工具（2026-05-25 更新）

### 国内搜索
| 类型 | 工具 | 备注 |
|------|------|------|
| 主力 | `baidu-search` | 中文主力 |
| 主力 | `tinyfish` | 中文也能搜 |
| 备选补充 | `mmx search` | MiniMax 全家桶 |

### 国外搜索
| 类型 | 工具 | 备注 |
|------|------|------|
| 主力 | `tinyfish` | 境外主力 |
| 备选补充 | `duckduckgo-search` | 依赖境外代理出口 |
| 备选补充 | `mmx search` | MiniMax |

### 全网搜索原则
收到未知问题需要查信息时，按地域选主引擎，同时启动其他工具：
- 国内 → baidu-search + tinyfish（双主力）+ mmx（备选补充）
- 境外 → tinyfish（主力）+ duckduckgo-search + mmx search（备选补充）

> ⚠️ 原 baidu-ai-search 和 minimax-web-search 已废弃。

## 通用信息爬取工作流

**核心原则：收到任何需要从网页获取信息的任务，必须穷举所有工具直到成功，绝不放弃。**

### 一、工具特性与适用场景

#### 网页抓取工具（按能力递增）
| 工具 | 能力 | 适用场景 |
|------|------|----------|
| `web_fetch` | 纯 HTTP 请求，只能抓静态 HTML | 博客、文档、新闻、Wiki 等静态页面 |
| `exec curl` | 拿原始 HTML，能提取页面嵌入的 JSON 数据 | 检查页面是否有隐藏数据（如 __ICE_PAGE_PROPS__）|
| `agent-browser` | 无头浏览器，有 Accessibility Tree，支持点击/填表 | SPA/React/Vue 渲染页面、站内搜索、需要交互的场景 |
| `Playwright` | 模拟真人浏览器，支持真实 UA/viewport/滚动 | 需要登录态、动态加载、需要模拟人类行为的页面 |
| `nodriver` | 反检测浏览器，navigator.webdriver=false | 淘宝/闲鱼等有反爬检测的网站，Playwright 被识别时的终极方案 |

#### 搜索工具（按地域分）
| 工具 | 适用地域 | 特点 |
|------|---------|------|
| `baidu-search` | 🇨🇳 国内 | 百度 AI 搜索，中文信息最全、支持阿拉丁卡 |
| `tinyfish` | 🇨🇳 国内 / 🌍 境外 | 中文也能搜；境外搜索主力 |
| `duckduckgo-search` | 🌍 境外 | 境外备选补充，依赖境外代理出口 |
| `mmx search` | 🇨🇳 国内 / 🌍 境外 | 备选补充 |

### 二、决策逻辑

**情况 A：我有目标 URL**
- 静态页面 → web_fetch
- JS 渲染页面 → curl 检查嵌入 JSON → agent-browser
- 需要登录/动态加载 → Playwright
- 高反爬网站 → nodriver

**情况 B：我不知道 URL / 404 了**
- 国内信息 → baidu-search + tinyfish（双主力）+ mmx（备选补充）
- 境外信息 → tinyfish（主力）+ duckduckgo-search + mmx（备选补充）
- 站内搜索 → agent-browser 打开网站搜索框

**情况 C：以上全部失败**
- 截图 + 视觉识别

### 三、核心原则

1. 第一步永远是爬取链接内容，不是搜索替代信息
2. 爬取优先级高于搜索
3. 绝不说"访问不了"、"爬不到"、"无法读取"
4. 同一信息在不同平台可能不同，必须确认用户要哪个源
5. 输出时标注数据来源、时效性

### 四、已验证的成功经验
- **Playwright 闲鱼**：真实 Windows UA + zh-CN locale + 1280x800 viewport → goto → networkidle → 滚动 → inner_text，成功提取 22 个套餐配置和价格
- **百炼定价页**：ICE SSR 渲染，内容嵌在 `__ICE_PAGE_PROPS__` JSON 里，用正则提取后解析
- **agent-browser 站内搜索**：导航到首页 → 搜索框输入关键词 → 点击搜索结果链接，找到隐藏的文档页

## 注意事项

- 环境变量 MINIMAX_API_KEY 已配置在 ~/.openclaw/.env
- `mmx` CLI 路径：`/root/.local/bin/mmx`
- 所有 MiniMax 功能优先使用 `mmx` CLI，更稳定
- prompt-enhancer 技能已安装，触发前缀：`p:` 或 `p-`

## 工具与技能标注规矩（行为规范索引）

规范位置：详见 AGENTS.md「行为规范（铁律）」章节

| 调用类型 | 正确标注 |
|---------|---------|
| exec / 系统内置命令 / web_fetch / web_search / read / write 等所有内置工具 | 【Tool：系统shell】 |
| aliyun CLI | 【Tool：阿里云CLI】 |
| tccli / 腾讯云CLI | 【Tool：腾讯云CLI】 |
| mmx CLI | 【Tool：mmx CLI】 |
| OpenClaw 内置工具（image 等） | 【Tool：image工具】 |
| 扩展技能（qweather / baidu-search / tinyfish / duckduckgo-search 等） | 【Skill：技能名】 |
| nodriver / playwright（自定义脚本） | 【Tool：nodriver】 / 【Tool：Playwright】 |

格式：英文方括号【Tool：】，中文【工具：】是错误格式。

---

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## 爬虫实战记录

### 闲鱼（Xianyu）爬取
**技能**：`xianyu-scraper`（已安装，路径 `~/.openclaw/workspace/skills/xianyu-scraper/`）
**规则**：严格按技能 SKILL.md 规定执行，禁止用自己记忆里的旧脚本。

**正确用法（直接调用技能脚本）：**
```bash
python3 ~/.openclaw/workspace/skills/xianyu-scraper/scripts/scrape.py '<URL>' --scroll 10
```

**SKILL.md 核心原则（与旧脚本冲突时以技能为准）：**
- 核心反检测**只有一行**：`delete navigator.__proto__.webdriver;`
- 关键参数：`--disable-blink-features=AutomationControlled`
- **禁止使用的复杂伪造**（会导致 React 报错 `a.addEventListener is not a function`）：
  - `window.chrome = {...}` ❌
  - `navigator.plugins = [...]` ❌
  - `navigator.mimeTypes = [...]` ❌
  - `navigator.connection = {...}` ❌
- 闲鱼登录墙只是遮罩，商品内容在页面 DOM 里仍存在，用逐步滚动探索。
- 商品详情页需要登录，推荐流不需要。

**执行流程**：收到链接 → 先读 SKILL.md → 按技能规定执行 → 不凭记忆。

### 淘宝/天猫爬取
**技能**：`taobao-scraper`（已安装，路径 `~/.openclaw/workspace/skills/taobao-scraper/`）
**触发词**：淘宝搜索、淘宝爬取、淘宝商品、天猫商品、抓取淘宝

**核心原理**：nodriver 直连 Chrome DevTools，WebSocket 直连，`navigator.webdriver` 默认 false，绕过淘宝第一层反爬检测。

**使用方式**：
```bash
PYTHON=/root/.openclaw/workspace/venvs/nodriver-env/bin/python3
# 首次登录（截取二维码，等待扫码）
$PYTHON ~/.openclaw/workspace/skills/taobao-scraper/scripts/scrape.py --login
# 搜索商品
$PYTHON ~/.openclaw/workspace/skills/taobao-scraper/scripts/scrape.py --search "关键词"
# 商品详情页
$PYTHON ~/.openclaw/workspace/skills/taobao-scraper/scripts/scrape.py --url "<URL>"
```

**cookie 持久化目录**：`/root/.openclaw/workspace/taobao_profile`，登录一次长期复用，约 30 天有效期。

**注意事项**：商品详情页需要登录；推荐流不需要登录可直接爬。

---

## 🌐 WOL 魔术包发送工具（2026-04-22 新增）

**触发指令**："打开公司电脑" / "打开家里电脑"

**工具**：Python socket 脚本（无依赖）

**发送流程（两步确认铁律，凌驾于一切之上）**：
1. 用户说"打开公司电脑"
2. 我汇报计划："我要发魔幻包到 zszn6.kingjinjing.top:44333，MAC D8-5E-D3-DB-ED-C3，确认吗？"
3. 用户说"可以"后，才执行 Python 脚本发送 UDP 魔术包
4. 执行后汇报结果

**禁止行为**：
- 不得在未经用户明确授权的情况下发送任何 WOL 魔术包
- 不得将设备绑定关系理解为"自动执行指令"
- 绑定信息仅用于关联名称与设备，不触发任何操作

**脚本模板**：
```python
import socket
mac_hex = 'D85ED3DBEDC3'
magic = b'\xff' * 6 + bytes.fromhex(mac_hex) * 16  # MAC 重复 16 次，共 102 字节
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock.sendto(magic, ('zszn6.kingjinjing.top', 44333, 0, 0))
sock.close()
```

**设备绑定**：
| 名称 | MAC | 域名 | 端口 |
|------|-----|------|------|
| 公司电脑 | D8-5E-D3-DB-ED-C3 | zszn6.kingjinjing.top | 44333 |
| 家里电脑 | 74-56-3C-74-F4-0F | 9bao.kingjinjing.top | 4343 |
| 丁桥电脑 | 18-F2-2C-E1-07-1D | kingjinjing.vip | 4343 |

**家里电脑 WOL 脚本**：
```python
import socket
mac_hex = '74563C74F40F'
magic = b'\xff' * 6 + bytes.fromhex(mac_hex) * 16
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(magic, ('9bao.kingjinjing.top', 4343))
sock.close()
```

---

## 🖥️ 公司电脑 SMB 远程关机（2026-04-23 新增）

**触发指令**：「关闭公司电脑」

**前提**：公司电脑已开机、Administrator 帐户已启用、SMB1 已启用

**连接信息**：
| 项目 | 值 |
|------|-----|
| 地址 | zszn6.kingjinjing.top:44555 |
| 用户 | Administrator |
| 密码 | 存于 `~/.openclaw/.env` 环境变量 `COMPANY_PC_SMB_PASSWORD` |
| 协议 | SMB over IPv6（Lucky 端口转发 44555→445） |

**关机方法**：通过 SCMR 创建临时服务执行 `shutdown.exe /s /t 0`

**✅ 经验证可用的 Python 脚本（impacket 0.10.0）**：
```python
from impacket.dcerpc.v5 import scmr
from impacket.dcerpc.v5.transport import DCERPCTransportFactory

target = 'zszn6.kingjinjing.top'
port = 44555
username = 'Administrator'
import os
password = os.environ['COMPANY_PC_SMB_PASSWORD']

stringbinding = r'ncacn_np:%s[\pipe\svcctl]' % target
transport = DCERPCTransportFactory(stringbinding)
transport.set_dport(port)
transport.setRemoteHost(target)
transport.set_credentials(username, password, '', '', '', '')

dce = transport.get_dce_rpc()
dce.connect()
dce.bind(scmr.MSRPC_UUID_SCMR)

# 响应字段用 lpScHandle（非 phScManager）
resp = scmr.hROpenSCManagerW(dce)
scm = resp['lpScHandle']  # 注意：不是 phScManager

# 创建并启动 shutdown 服务
resp2 = scmr.hRCreateServiceW(dce, scm, 'ShutDown', 'ShutDown',
                               lpBinaryPathName='shutdown.exe /s /t 0',
                               dwStartType=scmr.SERVICE_DEMAND_START)
svc = resp2['lpServiceHandle']  # 注意：不是 phServiceHandle

try:
    scmr.hRStartServiceW(dce, svc)
except:
    pass  # ERROR_SERVICE_REQUEST_TIMEOUT 是预期行为

scmr.hRDeleteService(dce, svc)
scmr.hRCloseServiceHandle(dce, svc)
scmr.hRCloseServiceHandle(dce, scm)
dce.disconnect()
```

**⚠️ 注意事项**：
- `SMBTransport(smb_connection=conn)` 方式会失败（STATUS_INVALID_PARAMETER），必须用 `DCERPCTransportFactory` 自己建立连接
- Lucky 「源端TLS」关闭时有效（TLS 开启时 SMB named pipe 也有问题，待进一步排查）
- Windows 10 Build 17763 测试通过

**⚠️ 密码铁律**：密码不能含 `$` `#` `!` `` ` `` `\` `"` `'` 等 shell/SMB 易解析符号，否则认证会失败

**🔒 两步确认铁律（与 WOL 同等重要）**：
1. 用户说"关闭公司电脑" → 汇报关机计划（远程执行 shutdown.exe）→ 等用户确认"可以" → 才发送关机命令
2. 执行后汇报结果
3. 未经用户明确确认，绝不发送任何远程关机命令

---

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## IMA 备忘录/知识库

**技能路径**：`~/.openclaw/workspace/skills/ima-skills/`

**触发场景**：笔记、备忘录、知识库、"帮我记一下"、"搜一下知识库里有没有XX"、上传文件到知识库、添加网页到知识库

### 凭证配置
```bash
# 从配置文件读取（优先级：环境变量 > 配置文件）
IMA_CLIENT_ID="${IMA_OPENAPI_CLIENTID:-$(cat ~/.config/ima/client_id 2>/dev/null)}"
IMA_API_KEY="${IMA_OPENAPI_APIKEY:-$(cat ~/.config/ima/api_key 2>/dev/null)}"
```

### API 基础信息
- **Base URL**: `https://ima.qq.com`
- **认证 Header**: `ima-openapi-clientid`, `ima-openapi-apikey`
- **请求方式**: POST + JSON Body

### 核心接口

| 意图 | 模块 | 接口路径 |
|------|------|----------|
| 创建新笔记 | notes | `/openapi/note/v1/import_doc` |
| 追加到已有笔记 | notes | `/openapi/note/v1/append_doc` |
| 搜索笔记 | notes | `/openapi/note/v1/search_note_book` |
| 读取笔记内容 | notes | `/openapi/note/v1/get_doc_content` |
| 列出笔记本 | notes | `/openapi/note/v1/list_note_folder_by_cursor` |
| 上传文件到知识库 | knowledge-base | `/openapi/wiki/v1/check_repeated_names` → `create_media` → COS → `add_knowledge` |
| 添加网页到知识库 | knowledge-base | `/openapi/wiki/v1/import_urls` |
| 搜索知识库 | knowledge-base | `/openapi/wiki/v1/search_knowledge` |

### 调用模板
```bash
ima_api() {
  local path="$1" body="$2"
  curl -s -X POST "https://ima.qq.com/$path" \
    -H "ima-openapi-clientid: $IMA_CLIENT_ID" \
    -H "ima-openapi-apikey: $IMA_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$body"
}

# 创建笔记示例
ima_api "openapi/note/v1/import_doc" '{"content_format": 1, "content": "# 标题\n\n正文"}'
```

### 铁律与注意事项

1. **UTF-8 编码强制要求**（notes 模块写入前）
   - `import_doc`/`append_doc` 前必须确保 `content` 和 `title` 是合法 UTF-8
   - 文件内容需先检测编码再转 UTF-8

2. **PowerShell 5.1 特殊处理**
   - 会静默将 Body 转为 GBK，必须用字节数组模式发送
   - 检测 `$PSVersionTable.PSVersion.Major -le 5`，用 `[System.Text.Encoding]::UTF8.GetBytes($body)`

3. **隐私规则**
   - 群聊场景只展示标题和摘要，禁止展示笔记正文

4. **无重命名接口**
   - 笔记创建后无法修改标题，需删除重建

5. **content_format 固定值**
   - 写入：`1` (Markdown)
   - 读取：`0` (纯文本，推荐)

### 之前犯的错误
- ❌ 域名错误：`api.immomo.com` → ✅ `ima.qq.com`
- ❌ `import_doc` 没有 `title` 字段，标题从 Markdown 的 `# 标题` 解析
- ❌ 未先读 SKILL.md 就盲目尝试 API
