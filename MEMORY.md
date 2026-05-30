# Long-Term Memory


## 操作规范铁律

**详见 AGENTS.md「二次确认准则」和「行为规范」章节，以下为补充经验。**

### 补充经验
- 用户确认后立刻回复总结
- **给链接前必须验证**:Playwright 打开确认可用才发
- **分析话题必须先搜索**:任何需要查信息的话题 → 先启动搜索技能

### 路由器 API 经验
| 操作 | 方法 | URL | Body |
|------|------|-----|------|
| 登录 | POST | `http://192.168.9.1/` | `{"method":"do","login":{"username":"admin","password":"xxx"}}` |
| 查询 | POST | `http://192.168.9.1/stok=<token>/ds` | `{"method":"get","<模块>":{"name":"<表名>"}}` |
| 设置 | POST | `http://192.168.9.1/stok=<token>/ds` | `{"method":"set","<模块>":{"<表>":{"<字段>":"<值>"}}}` |

---

## 运维经验

### 公司电脑远程操作
- **WOL 开机**:MAC `D8-5E-D3-DB-ED-C3`,目标 `zszn6.kingjinjing.top:44333`,IPv6+UDP
- **SMB/SCMR 关机**:密码存于 `~/.openclaw/.env` 环境变量 `COMPANY_PC_SMB_PASSWORD`
- **流程**:`hROpenSCManagerW` → `hRCreateServiceW` → `hRStartServiceW`,关机后 RPC 超时正常

### SSH 权限教训
- `chmod 777 /home/openclaw` 会破坏公钥认证(sshd StrictModes 拒绝 other 写权限)
- 修复:`chmod 755` + `systemctl restart ssh`

### NAS openclaw 账号
- ChrootDirectory:`/home/openclaw`(root:root,755)
- 绑定挂载:`/vol1/1000/My Document/openclaw/upload` → `/home/openclaw/upload`
- ForceCommand internal-sftp,登录后只有 upload 目录可见

---

## 工具规矩

### 工具标注格式
- 格式:**英文方括号【Tool:xxx】**,中文【工具:】是错误格式
- mmx CLI 单独标注为【Tool:mmx CLI】

### cron prompt 污染问题
- JSON 中的反引号(`` ` ``)会被 bash 的 `$(...)` 和反引号展开解析
- 解决:整个 prompt 用单引号包裹

### MiniMax 用量字段
- `usage_count` = **剩余配额**,不是已用量
- 已用量 = 总配额 - usage_count
- 回答用量类问题前必须先查确认,不得凭直觉

---

## 技术经验

### qweather Bug 教训
- 函数名拼写错误(`format_indices3` → `format_indices3d`)
- **修复后必须运行原命令验证**,不能只看退出码 0
- Python 报错 `NameError` 时会提示正确函数名,要信它

### 新闻推送铁律(2026-04-20/21 定稿)
- **搜索**:按 AGENTS.md「全网搜索规则」选择主引擎,百度默认 `freshness:"pd"`
- **链接**:禁止搜索命令文本/占位符/平台首页,必须 `https://` 开头的实际文章 URL
- **国际版块白名单**:BBC + Guardian + Al Jazeera + CNN + Reuters + AP News,禁止今日头条/腾讯新闻/新浪
- **本地版块 4 个已验证来源**:潮新闻(必须有 `id=` 参数)、杭州网、浙江新闻、浙江日报数字报
- **5 要素**:标题 + 摘要(≥30字)+ 来源 + 精确时间 + 原始链接
- **超时处理**:工具超时 → 该条直接丢弃,禁止占位符填充
- **MiniMax 429 误报**:cron 报 429 是阿里云内容审核误杀("inappropriate content"),非额度用完

### 淘宝/京东 Playwright 登录流程
1. 导航到登录页(淘宝:`login.taobao.com`,京东:`passport.jd.com`)
2. 截图二维码 → 发给用户扫码
3. 循环检测 URL 变化(从登录页跳转到用户中心)
4. 保存 cookie

### SolidWorks BOM 批量转图(v8 宏)
- 代码位置:`D:\pythonproject\SWexport\batch_sw_to_dxf_v8.py`
- BOM 两种结构:29 行(无起订量列,`BOM(0,3)`=物料图号)和 30 行(有起订量列,`BOM(0,4)`=物料图号)
- 导出逻辑:先 DXF,DXF 失败才 fallback DWG
- 绿盾(天盾):DLL 注入法绕过,`GREENSHIELD_EXPORT_DXF=1`

### VBA 编码规范
- 中文双引号("")与 VBA 字符串双引号("")冲突 → 只用英文引号
- `&` 前后加空格:`str1 & str2`
- `Is Nothing` 而不是 `== Nothing`
- `For Each` 遍历集合,不要用 `For i = 1 To ...`
- 数组越界用 `UBound(arr) + 1` 动态扩展

### 路由协议抓包方法
遇到未知协议 → 用 Playwright 浏览器上下文观察实际请求 → curl 重放

### SolidWorks PDM 文件关联故障排查
- **PDM 两条调用链**:`查看文件` 走 PDM Viewer 配置,`双击/打开` 走 Windows 底层文件关联(`HKCR\.pdf → ProgId → shell\open\command`),两者独立
- **Windows 文件关联三层**:`HKCU UserChoice`(现代,Win10 设置走这里) / `assoc` + `HKCR`(传统,老软件走这里) / `HKCR 默认值`(可为空)
- **典型故障**:UserChoice 指向 A,assoc 残留指向 B → 新软件正常但 PDM 等老软件双击无反应
- **排查口诀**:查看文件能开+打开方式能开+双击不行 = 文件关联问题,不是 PDM Viewer 问题
- **PDM Viewer 参数 `%1%` vs ftype 的 `%1`**:不同场景参数格式不同,混用会出错
- **修复命令**:`assoc .pdf=XXX.Document` + `ftype XXX.Document="path" "%1"` + `reg add HKCR\.pdf` + 重启 explorer
- **关联经验**:i5-8300U 不存在,8代 U 系列只有 8250U/8350U;i5-8300H 是 45W 标压,4核8线程,基础 2.3G 睿频 4.0G

---

## 硬件参考

### N100 vs 二手 i5 电费对比(24H 开机,0.5元/度)
- TDP:N100 6W vs i5-7500T 35W(差距 29W)
- 年电费差(70% 负载估算):约 88 元/年
- 5 年累计差:约 440-640 元

### i5-8500 vs i5-9500
- 核心/线程/缓存/TDP/核显/内存支持:完全一致
- 唯一差异:单核睿频(4.1G vs 4.4G)
- i5-9500 溢价 ¥130(15%),性能提升仅 5-8%,性价比不如 i5-8500

---




## Promoted From Short-Term Memory (2026-05-29)

<!-- openclaw-memory-promotion:memory:memory/2026-04-20.md:21:47 -->
- 英文内容翻译规矩 - 国际版块来源规定 - 本地版块4个来源列表 **TOOLS.md 更新：** - 搜索首选方案：三工具并行 + 代理配置 + 执行格式 - 百度搜索：新增 card_limit（阿拉丁卡片）、freshness 参数说明，默认加 freshness:"pd" - 闲鱼爬取：完整 Playwright 反检测脚本（最简版，只有 delete navigator.__proto__.webdriver;） - 天气推送格式：已修正，今日概况每项另起一行 ### GitHub skills 仓库更新 - 仓库：k176060444-lgtm/skills - 新增 baidu-search/（今日推送） - 新增 xianyu-scraper/（今日推送） - 现有 minimax-lyrics/ + minimax-music/ + qweather/ - 合并方式：所有 skill 以子目录形式合入 main 分支 ### 咸鱼爬取验证 - 验证成功：只用一行 `delete navigator.__proto__.webdriver;` + `--disable-blink-features=AutomationControlled` - 抓取商品信息完整（标题、价格、配置表、卖家信息） - MEMORY.md 里的复杂伪造版是错的（会导致React报错），以 xianyu-scraper SKILL.md 最简版为准 ## 教训 - 天气推送格式：今日概况每项必须换行（天气/气温/湿度/风力各自一行），不是连成一段 - 气温数值不加 Markdown 粗体，纯文字即可 - 天气 emoji 图标：晴 ☀️、多云 ⛅、阴天 🌥️、小雨 🌧️、中雨 🌧️、大雨 🌧️、雷阵雨 ⛈️、雾 🌫️ [score=0.855 recalls=13 avg=0.433 source=memory/2026-04-20.md:21-47]
<!-- openclaw-memory-promotion:memory:memory/2026-04-21.md:1:24 -->
- # 2026-04-21 日记 ## 今日教训：新闻推送质量严重下滑（永久规则已更新） ### 事件 用户早上反馈定时新闻推送"完全是糊弄"，发现以下严重问题： 1. 链接用搜索命令文本占位符（`https://mmx search query`）充数 2. 本地版块用了列表页 `tidenews.com.cn/news.html`（无 `id=` 参数）而非文章详情页 3. 国际版块出现了"今日头条"（不在白名单） 4. 推送了大量昨天（04-20）的旧闻 5. 热搜版块用了微博首页而非详情页 ### 根因 cron 执行时搜索工具超时/失败，AI 直接用占位符文本填充链接，没有降级处理规则。 ### 已修复 1. 三个文件（AGENTS.md/SOUL.md/MEMORY.md）同步更新了新闻推送铁律： - 链接：禁止搜索命令文本/占位符/平台首页，必须是 `https://` 开头实际 URL - 国际版块白名单：BBC + Guardian + Al Jazeera，禁止今日头条/腾讯新闻/新浪 - 本地版块潮新闻链接：必须有 `id=` 参数，无 id 的是列表页严禁使用 - 逐项勾选校验清单：日期✔ / 链接有效✔ / 来源合规✔ / 五要素齐全✔ - 工具超时处理：该条直接丢弃，禁止占位符填充 - 推送必须分多条发送（QQ 500字符限制） 2. 同步更新了早晚新闻 cron prompt（强制自检 + 分多条发送） [score=0.851 recalls=7 avg=0.438 source=memory/2026-04-21.md:1-24]
<!-- openclaw-memory-promotion:memory:memory/2026-04-20.md:1:27 -->
- # 2026-04-20 Daily Memory ## 今日主要工作 ### 新闻推送配置大更新（今天核心任务） **cron prompt 更新（早间7时 + 晚间19时，同步更新）：** - 搜索规则改为三工具并行：百度 + DuckDuckGo（英文，需翻译成中文）+ mmx search - 百度搜索默认加 `freshness:"pd"`（只返回今日内容） - 5要素格式强制要求：标题 + 摘要 + 来源 + 精确时间 + 链接 - 超时从15分钟延长到20分钟 - 国际版块来源：BBC + Guardian + Al Jazeera + DuckDuckGo英文搜索（WSJ/FT/NYT因服务器直连403排除） - 本地版块来源（4个，已验证全部可访问）： - 潮新闻（tidenews.com.cn/news.html?id=XXXXXXXX） - 杭州网（hznews.hangzhou.com.cn/shehui/content/日期/content_xxxx.htm） - 浙江新闻（zjnews.zjol.com.cn/zjnews/日期/t日期_XXXXXXXX.shtml） - 浙江日报数字报纸（zjrb.zjol.com.cn/html/日期/content_XXXXXXX.htm?div=-1） **三个规则文件同步更新（AGENTS.md + SOUL.md）：** - 三工具并行搜索规矩（所有"两工具"表述已清除） - 英文内容翻译规矩 - 国际版块来源规定 - 本地版块4个来源列表 **TOOLS.md 更新：** - 搜索首选方案：三工具并行 + 代理配置 + 执行格式 - 百度搜索：新增 card_limit（阿拉丁卡片）、freshness 参数说明，默认加 freshness:"pd" [score=0.839 recalls=17 avg=0.422 source=memory/2026-04-20.md:1-27]
<!-- openclaw-memory-promotion:memory:memory/2026-04-21.md:561:574 -->
- 不需要修改服务器权限，直接在 NAS 侧操作：把 `ZOCH21041 生产清单.xlsx` 从 `/vol1/1000/My Document/openclaw/upload/` 剪切到 `/vol1/1000/My Document/openclaw/` - 这样文件会自动出现在我的 SFTP 根目录，无需改服务器配置 ### 最终稳定权限状态（当前） 1. `/home/openclaw`：root:root，755，符合 Chroot 安全要求 2. `/home/openclaw/upload`：openclaw:openclaw，771，我有完整读写删权限 3. 所有功能正常：SFTP连接、文件上传下载、读取已上传的三个核心文件（AGENTS/MEMORY/SOUL.md） 4. NAS绑定挂载正常：我在 `/upload/` 下的所有操作都会同步到 NAS 真实路径 5. xlsx文件：权限660，属主kingjinjing，我暂时无读权限（需要加ACL） ### 教训记录 1. **永远不要给用户home目录设777权限**，会触发SSH安全机制直接锁死公钥登录 2. **修改权限前先查SSH安全规则**，StrictModes会验证home目录、.ssh目录、authorized_keys的权限是否合规 3. **优先用NAS侧操作代替服务器权限修改**，避免破坏SSH服务可用性 [score=0.812 recalls=3 avg=0.618 source=memory/2026-04-21.md:561-574]
<!-- openclaw-memory-promotion:memory:memory/2026-04-08.md:97:120 -->
- 天气指数要用Markdown表格呈现 - 日期格式：04月10日 周五（不要"明天/后天"标签） - 每次推送都要先检查配置正确性 ## 服务器文件操作二次确认规矩（2026-04-08 补充） **二次确认流程：** 1. 操作前先说"我要改/删/新建XXX，确认吗？" 2. 用户说"可以"后再执行 3. 操作完成后汇报并验证 **适用范围：** - 服务器文件的新建/修改/删除 - 配置文件修改 - cron任务配置修改 - 日志清理 **例外：** - `.learnings/` 目录内文件（技能内部行为） - 纯读取操作 这是铁律，违者自断。 [score=0.810 recalls=13 avg=0.457 source=memory/2026-04-08.md:97-120]

## Promoted From Short-Term Memory (2026-05-30)

<!-- openclaw-memory-promotion:memory:memory/2026-04-09.md:502:524 -->
- `format_24h`：24h逐时温度 → 珊瑚红 - tomorrow/aftertomorrow：概况温度 → 珊瑚红 **天气查询三命令（已就绪）**： | 命令 | 日期 | 空气质量 | 天气指数 | 说明 | |------|------|---------|---------|------| | `weather` | 今天 | ✅ AQI | ✅ 今天的 | 默认/不指定时用 | | `tomorrow` | 明天 | ✅ AQI | ✅ 明天的 | 明确要求明天时用 | | `aftertomorrow` | 后天 |暂无预报 | ✅ 后天的 | 明确要求后天时用 | **空气日报UTC对齐规则**： - days[0].forecastStartTime = "2026-04-08T16:00Z" = 北京 04-09 00:00 = **今天** - days[1].forecastStartTime = "2026-04-09T16:00Z" = 北京 04-10 00:00 = **明天** - today查 days[0]，tomorrow查 days[1]，aftertomorrow无数据 --- ## HEARTBEAT 补充记录 | 时间 | 检查结果 | 发现事项 | 处理结果 | |------|---------|---------|---------| | 2026-04-09 21:44 | ✅ 正常 | SESSION-STATE无待汇报 | 无需处理 | [score=0.845 recalls=4 avg=0.619 source=memory/2026-04-09.md:502-524]
