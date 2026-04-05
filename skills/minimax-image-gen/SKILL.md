---
name: minimax-image-gen
description: MiniMax 文生图图像生成技能，通过 MCP 协议调用 MiniMax API 生成图片
metadata:
  openclaw:
    emoji: "🎨"
    requires:
      bins:
        - python3
        - uv
      env:
        - MINIMAX_API_KEY
---

# MiniMax 图像生成技能

通过 MiniMax MCP 协议调用官方 API 进行文生图图像生成。

## 功能

- **text_to_image**: 文生图，根据提示词生成图片
- 支持多种宽高比（1:1、16:9、4:3、3:2、2:3、3:4、9:16、21:9）
- 支持生成多张图片（1-9张）
- 支持提示词自动优化
- 保存图片到本地并返回 URL 和本地路径

## 配置

### 环境变量

需要在 `~/.openclaw/.env` 中配置：

```bash
MINIMAX_API_KEY=your-api-key-here
```

### API 端点

默认使用国内端点：`https://api.minimaxi.com`

如果使用国际版，需要设置环境变量：
```bash
MINIMAX_API_HOST=https://api.minimax.io
```

## 使用方法

### 直接调用脚本

```bash
python3 skills/minimax-image-gen/scripts/generate.py "一只猫正在晒太阳睡觉"
```

### 指定参数

```bash
python3 skills/minimax-image-gen/scripts/generate.py \
  --prompt "一只猫正在晒太阳睡觉" \
  --aspect-ratio "16:9" \
  --n 2 \
  --output-dir "/path/to/output"
```

## 参数说明

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `--prompt` | 是 | - | 生成图片的提示词 |
| `--model` | 否 | `image-01` | 模型名称，目前只有 `image-01` |
| `--aspect-ratio` | 否 | `1:1` | 宽高比，可选：1:1, 16:9, 4:3, 3:2, 2:3, 3:4, 9:16, 21:9 |
| `--n` | 否 | `1` | 生成图片数量，1-9张 |
| `--no-optimizer` | 否 | false | 禁用提示词优化 |
| `--output-dir` | 否 | `~/minimax-output` | 输出目录 |

## 输出

生成成功后返回：
- 图片 URL（有效期 24 小时）
- 本地文件路径

## 依赖安装

首次运行会自动通过 uv 安装 `minimax-mcp`，不需要手动安装。

## 可用工具（MCP）

除了文生图，这个 MCP 服务器还提供：

| 工具 | 说明 |
|------|------|
| `text_to_image` | 文生图 |
| `text_to_audio` | 文本转语音 |
| `generate_video` | 文本生成视频 |
| `music_generation` | 音乐生成 |
| `voice_clone` | 声音克隆 |
| `voice_design` | 声音设计 |
| `list_voices` | 列出可用音色 |

## 费用提示

- 每次调用都会消耗 MiniMax API 配额
- 请确认你的 Coding Plan 有足够额度

## 示例

```bash
# 生成一只晒太阳的猫，正方形 1:1
python3 skills/minimax-image-gen/scripts/generate.py "一只猫，正在阳光下的窗台晒太阳睡觉，温馨舒适的氛围"

# 生成风景图，宽屏 16:9
python3 skills/minimax-image-gen/scripts/generate.py \
  --prompt "秋日森林，阳光透过枫叶洒下，小鹿在林间漫步" \
  --aspect-ratio "16:9"
```

## 故障排查

### 连接超时

- 检查网络是否能访问 `api.minimaxi.com`
- 确认 `MINIMAX_API_KEY` 正确且未过期

### 认证失败

```
Error: invalid api key
```

- 检查 API Key 是否正确
- 确认 `MINIMAX_API_HOST` 和 API Key 匹配（国内版 vs 国际版）

### 生成失败

- 检查提示词是否违反内容政策
- 确认配额充足，可以用 `minimax-usage` 技能查询用量
