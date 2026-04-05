# TOOLS.md - Local Notes

## Minimax 用量查询

查询命令（正确域名）：
```bash
curl -s "https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains?GroupId=2029851692941451645" \
  -H "Authorization: Bearer $MINIMAX_API_KEY" \
  -H "Content-Type: application/json"
```

**注意**：域名是 `www.minimaxi.com`，不是 `platform.minimax.io`。

## Minimax 网络搜索

**搜索命令：**
```bash
python3 ~/.openclaw/workspace/skills/minimax-web-search/scripts/web_search.py "<搜索内容>"
```

**示例：**
```bash
python3 ~/.openclaw/workspace/skills/minimax-web-search/scripts/web_search.py "今日要闻"
```

## Minimax 图像理解

**分析命令：**
```bash
python3 ~/.openclaw/workspace/skills/minimax-understand-image/scripts/understand_image.py "<图片路径或URL>" "<提示词>"
```

**示例：**
```bash
python3 ~/.openclaw/workspace/skills/minimax-understand-image/scripts/understand_image.py "/root/.openclaw/qqbot/downloads/xxx.png" "描述这张图片"
```

## 注意事项

- 脚本已内置国内镜像（pypi.tuna.tsinghua.edu.cn），无需手动设置
- 环境变量 MINIMAX_API_KEY 已配置在 ~/.openclaw/.env

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

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

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
