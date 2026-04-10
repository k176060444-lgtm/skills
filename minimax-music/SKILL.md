# MiniMax 音乐生成技能

## 功能描述

使用 MiniMax 的 **music-2.6** 模型生成音乐（MP3 格式）。

## 支持能力

| 能力 | 说明 |
|------|------|
| 纯音乐生成 | 无需歌词，只需描述风格/情绪 |
| 歌词歌曲生成 | 支持自定义歌词（使用 `\n` 分隔行） |
| 结构化歌词 | 支持 `[Verse]`、`[Chorus]`、`[Bridge]` 等标签 |
| 自动歌词生成 | `lyrics_optimizer: true` 可根据 prompt 自动生成歌词 |

## 模型说明

- **默认模型**：`music-2.6`（推荐）
- **其他可选**：`music-2.5+`、`music-2.5`

## 输出格式

- **默认格式**：MP3
- **可选格式**：WAV、PCM
- **采样率**：44100 Hz（默认）
- **比特率**：256000（默认）

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `prompt` | string | 是（纯音乐） | 音乐描述，1-2000字符 |
| `lyrics` | string | 是（非纯音乐） | 歌词，用 `\n` 分隔行，1-3500字符 |
| `is_instrumental` | boolean | 否 | 是否纯音乐，默认 `false` |
| `duration` | integer | 否 | 时长（秒），建议 30-180 秒 |
| `lyrics_optimizer` | boolean | 否 | 自动根据 prompt 生成歌词，默认 `false` |
| `output_format` | string | 否 | 输出格式：`hex`（默认）或 `url` |

## 使用方式

### 命令行调用

```bash
python3 ~/.openclaw/workspace/skills/minimax-music/scripts/minimax_music.py \
  --prompt "独立民谣,忧郁,内省,适合咖啡馆" \
  --is_instrumental true \
  --duration 60 \
  --output ~/.openclaw/workspace/output.mp3
```

### 带歌词调用

```bash
python3 ~/.openclaw/workspace/skills/minimax-music/scripts/minimax_music.py \
  --prompt "流行音乐,欢快,充满活力" \
  --lyrics "[verse]\n街灯微亮晚风轻抚\n影子拉长独自漫步\n\n[chorus]\n推开木门香气弥漫" \
  --duration 120 \
  --output ~/.openclaw/workspace/song.mp3
```

### 自动歌词生成

```bash
python3 ~/.openclaw/workspace/skills/minimax-music/scripts/minimax_music.py \
  --prompt "电子音乐,赛博朋克,未来感,夜间城市" \
  --lyrics_optimizer true \
  --is_instrumental true \
  --duration 90 \
  --output ~/.openclaw/workspace/cyberpunk.mp3
```

## 输出文件

生成的 MP3 文件会保存到指定路径，默认保存到 `/root/.openclaw/workspace/music_{timestamp}.mp3`

## 错误处理

| status_code | 说明 | 处理方式 |
|-------------|------|---------|
| 0 | 成功 | 返回音频文件路径 |
| 1002 | 触发限流 | 稍后重试 |
| 1004 | 账号鉴权失败 | 检查 API Key |
| 1008 | 账号余额不足 | 充值账户 |
| 2013 | 参数异常 | 检查输入参数 |
| 2049 | 无效的 API Key | 检查 Key 配置 |

## 依赖项

- Python 3.7+
- `requests` 库
- MiniMax API Key（环境变量 `MINIMAX_API_KEY`）

## 注意事项

1. **HEX 解码**：MiniMax 返回的是 HEX 编码的音频数据，不是 base64
2. **纯音乐 vs 有歌词**：
   - 纯音乐：`is_instrumental: true`，`prompt` 必填，`lyrics` 非必填
   - 有歌词：`is_instrumental: false`（默认），`lyrics` 必填
3. **输出格式**：默认 MP3，可选 WAV/PCM
4. **URL 有效期**：如果使用 `output_format: url`，有效期 24 小时，请及时下载
