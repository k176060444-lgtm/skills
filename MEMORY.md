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




## Promoted From Short-Term Memory (2026-05-30)

<!-- openclaw-memory-promotion:memory:memory/2026-04-09.md:502:524 -->
- `format_24h`：24h逐时温度 → 珊瑚红 - tomorrow/aftertomorrow：概况温度 → 珊瑚红 **天气查询三命令（已就绪）**： | 命令 | 日期 | 空气质量 | 天气指数 | 说明 | |------|------|---------|---------|------| | `weather` | 今天 | ✅ AQI | ✅ 今天的 | 默认/不指定时用 | | `tomorrow` | 明天 | ✅ AQI | ✅ 明天的 | 明确要求明天时用 | | `aftertomorrow` | 后天 |暂无预报 | ✅ 后天的 | 明确要求后天时用 | **空气日报UTC对齐规则**： - days[0].forecastStartTime = "2026-04-08T16:00Z" = 北京 04-09 00:00 = **今天** - days[1].forecastStartTime = "2026-04-09T16:00Z" = 北京 04-10 00:00 = **明天** - today查 days[0]，tomorrow查 days[1]，aftertomorrow无数据 --- ## HEARTBEAT 补充记录 | 时间 | 检查结果 | 发现事项 | 处理结果 | |------|---------|---------|---------| | 2026-04-09 21:44 | ✅ 正常 | SESSION-STATE无待汇报 | 无需处理 | [score=0.845 recalls=4 avg=0.619 source=memory/2026-04-09.md:502-524]

## Promoted From Short-Term Memory (2026-05-31)

<!-- openclaw-memory-promotion:memory:memory/2026-05-27.md:39:39 -->
- **违规行为：** [score=0.859 recalls=0 avg=0.620 source=memory/2026-05-27.md:39-39]
<!-- openclaw-memory-promotion:memory:memory/2026-04-17.md:218:254 -->
- |------|------|------| | `-it` | Instruction Tuned | 指令微调版，适合对话/问答 | | `E4B`/`E2B` | 统一多模态架构 | 4B/2B 参数，支持文本 + 图像 + 音频 + 视频全模态 | | `31B`/`26B-A4B` | 视觉多模态 | 仅支持文本 + 图像，不支持音频/视频 | **结论：** 带 **E** 的是新一代全模态，带 **it** 的能对话，不带的是基座版。 --- ### 2. 智谱 GLM-5.1-FP8 **FP8 = 8-bit Floating Point（8 位浮点量化版）** | 版本 | 精度 | 显存 | 速度 | 推荐 | |------|------|------|------|------| | `GLM-5.1` | FP16（100%） | 36GB+ | 标准 | A100/H100 | | `GLM-5.1-FP8` | FP8（98-99%） | 18GB | 快 1.5-2 倍 | ✅ 消费级显卡 | **结论：** FP8 是量化压缩版，不是能力削弱版。显存减半，速度更快，日常使用几乎无精度损失。 --- ### 3. DeepSeek-V3.2 四个版本 | 版本 | 类型 | 稳定性 | 推荐度 | |------|------|--------|--------| | `V3.2` | 正式版 | ⭐⭐⭐⭐⭐ | ✅ 首选 | | `V3.2-Exp` | 实验版 | ⭐⭐⭐ | 尝鲜 | | `V3.2-Speciale` | 特别优化版 | ⭐⭐⭐⭐ | 特定需求 | | `V3.2-Exp-Base` | 实验版基座 | ⭐⭐⭐⭐ | 开发用 | **结论：** 无脑选 `DeepSeek-V3.2`（正式标准版）—— 发布时间最新、点赞最多、最稳定。 --- ## 今日迷你主机对比结论 [score=0.836 recalls=5 avg=0.532 source=memory/2026-04-17.md:218-254]
<!-- openclaw-memory-promotion:memory:memory/2026-05-27.md:5:5 -->
- 用户发来一份详细的故障复盘文档，关于 SolidWorks PDM 2020 中双击 PDF 无反应的问题。 [score=0.828 recalls=0 avg=0.620 source=memory/2026-05-27.md:5-5]
<!-- openclaw-memory-promotion:memory:memory/2026-05-27.md:8:8 -->
- Windows 10 文件关联"三层打架"： [score=0.828 recalls=0 avg=0.620 source=memory/2026-05-27.md:8-8]
<!-- openclaw-memory-promotion:memory:memory/2026-05-27.md:13:13 -->
- PDM 2020 的双击/右键打开走的是老的 `assoc` 链路（`HKCR\.pdf → ProgId → shell\open\command`），不完全走 UserChoice，所以旧关联残留导致打不开。 [score=0.828 recalls=0 avg=0.620 source=memory/2026-05-27.md:13-13]
<!-- openclaw-memory-promotion:memory:memory/2026-05-27.md:17:20 -->
- assoc .pdf=FoxitReaderPlus.Document ftype FoxitReaderPlus.Document="D:\Foxit Software\Foxit Reader Plus\FoxitReaderPlus.exe" "%1" reg add "HKCR\.pdf" /ve /d "FoxitReaderPlus.Document" /f taskkill /f /im explorer.exe && start explorer.exe [score=0.828 recalls=0 avg=0.620 source=memory/2026-05-27.md:17-20]
