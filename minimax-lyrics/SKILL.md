# MiniMax 歌词生成技能

## 功能描述

使用 MiniMax 歌词生成 API 创作歌曲歌词，支持**完整歌曲创作**和**歌词编辑/续写**两种模式。

## API 信息

- **接口**: `POST https://api.minimaxi.com/v1/lyrics_generation`
- **文档**: https://platform.minimaxi.com/docs/api-reference/lyrics-generation.md

## 生成模式

| 模式 | 说明 |
|------|------|
| `write_full_song` | 写完整歌曲（默认） |
| `edit` | 编辑/续写已有歌词 |

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--mode` / `-m` | 否 | 生成模式，默认 `write_full_song` |
| `--prompt` / `-p` | 否 | 歌曲主题/风格描述，最多2000字 |
| `--lyrics` / `-l` | 否 | 现有歌词（仅 edit 模式），最多3500字 |
| `--title` / `-t` | 否 | 指定歌曲标题 |
| `--output` / `-o` | 否 | 输出文件路径（默认输出到标准输出） |

## 支持的结构标签（14种）

`[Intro]` `[Verse]` `[Pre-Chorus]` `[Chorus]` `[Hook]` `[Drop]` `[Bridge]` `[Solo]` `[Build-up]` `[Instrumental]` `[Breakdown]` `[Break]` `[Interlude]` `[Outro]`

## 使用方式

### 生成完整歌曲歌词

```bash
python3 ~/.openclaw/workspace/skills/minimax-lyrics/scripts/minimax_lyrics.py \
  --prompt "一首关于夏日海边的轻快情歌" \
  --title "夏日约定"
```

### 编辑/续写已有歌词

```bash
python3 ~/.openclaw/workspace/skills/minimax-lyrics/scripts/minimax_lyrics.py \
  --mode edit \
  --lyrics "[Verse 1]\n阳光洒满了海面..." \
  --prompt "继续写一个更有活力的版本"
```

### 输出示例

```
🎵 歌名: 夏日海风的约定
🏷️ 风格: Mandopop, Summer Vibe, Romance, Lighthearted, Beach Pop

📝 歌词:
----------------------------------------
[Intro]
(Ooh-ooh-ooh)
(Yeah)
阳光洒满了海面

[Verse 1]
海风轻轻吹拂你发梢
...
----------------------------------------

💡 使用提示: 将上述歌词作为 --lyrics 参数配合 mmx music generate 生成歌曲
```

## 常见错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1002 | 触发限流，请稍后再试 |
| 1004 | 账号鉴权失败 |
| 1008 | 账号余额不足 |
| 1026 | 输入包含敏感内容 |
| 2013 | 参数异常 |
| 2049 | 无效的 API Key |

## 注意事项

1. 生成的歌词包含结构标签，可直接用于 `mmx music generate --lyrics`
2. `--lyrics` 参数使用 `\n` 分隔行
3. 建议搭配 `minimax-music` 技能使用，先生成歌词再生成歌曲
