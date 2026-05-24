---
name: modelscope-image-gen
description: ModelScope Qwen-Image-2512 文生图技能，通过 ModelScope API 生成图片。触发词：生成图片/生成一张图/画一张/mota生图
metadata:
  openclaw:
    emoji: "🎨"
    requires:
      bins:
        - python3
        - requests
        - Pillow
      env:
        - MODELSCOPE_API_KEY
---

# ModelScope 文生图技能

通过 ModelScope API 调用 Qwen-Image-2512 模型进行文生图图像生成。

## 功能

- **文生图**：根据提示词生成图片
- 支持异步生成模式（适合大图）
- 支持 LoRA 微调模型（可选）
- 支持中英文提示词

## 模型信息

- **模型**：`Qwen/Qwen-Image-2512`
- **参数量**：28.85B（288.5 亿）
- **开源协议**：Apache-2.0
- **语言**：英文 + 中文

## 使用方法

### 基本用法

```bash
python3 ~/.openclaw/workspace/skills/modelscope-image-gen/scripts/generate.py "一只猫在晒太阳"
```

### 指定参数

```bash
python3 ~/.openclaw/workspace/skills/modelscope-image-gen/scripts/generate.py \
  --prompt "一只猫在晒太阳" \
  --output "/root/.openclaw/workspace/generated.png"
```

## 参数说明

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `--prompt` | 是 | - | 生成图片的提示词 |
| `--output` | 否 | 自动生成 | 输出文件路径 |
| `--loras` | 否 | 无 | LoRA 模型 ID（可选） |

## 输出

生成成功后返回：
- 图片保存路径
- 图片 URL

## 费用

- ModelScope API 调用**免费**（已配置 API Key）

## 示例

```bash
# 生成一只晒太阳的猫
python3 ~/.openclaw/workspace/skills/modelscope-image-gen/scripts/generate.py "A cat sunbathing in the sunshine, photorealistic"

# 生成赛博朋克城市夜景
python3 ~/.openclaw/workspace/skills/modelscope-image-gen/scripts/generate.py "Cyberpunk city at night, neon lights, rainy streets, photorealistic"
```
