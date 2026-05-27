# Long-Term Memory


## 操作规范铁律

### 未授权禁止操作(八大类)
1. 外部服务接入(API 集成、OAuth、Webhook)
2. 服务器配置修改(防火墙、SSH、nginx、Cron)
3. 软件安装/卸载
4. 云资源操作(创建、删除、计费类)
5. 定时任务/自动化创建
6. 系统级变更
7. 主动外发消息(邮件、社交平台)
8. 产生费用操作(任何要花钱的事)

### 任务完成汇报规矩
- 完成立即汇报,不许装死
- 遇到问题立即汇报,不许隐瞒
- 用户确认后立刻回复总结
- 出错时诚实说原因,不甩锅不抱怨

### 链接/数据规矩
- **不发明 URL**:从搜索结果里找,不自己构造
- **给链接前必须验证**:Playwright 打开确认可用才发
- **不捏造数据**:不知道就说不知道,不编造
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
- **SMB/SCMR 关机**:密码 `e3y3S3Gof7f2`(不能含 `$#!\` 等特殊符号,bash→SMB 传输会解析)
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
- **搜索**:三工具并行(百度 + DuckDuckGo + mmx),百度默认 `freshness:"pd"`
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



