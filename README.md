# Influencer-Product Matching System

本项目用于达人（KOL/网红）与商品的智能匹配，支持达人属性标签、视频内容标签自动提取、搜索与排序等功能，便于品牌方或平台高效筛选合适的达人。

## 目录结构

```
matching/
├── __init__.py
├── influencer_product_matching.py  # 主逻辑，达人数据结构、标签匹配、排序等
├── video_to_text.py                # 视频转文本/标签，调用多模态大模型
└── README.md
```

## 主要功能

- **达人数据模型**：支持任意扩展属性（如粉丝数、曝光量、预算等），标签（hash tag）、视频分析标签。
- **视频标签自动提取**：集成大模型（如 Qwen2.5-VL），可自动分析达人视频内容，抽取有用 hash tag。
- **用户输入过滤与标签匹配**：支持对用户搜索内容进行关键词提取，与达人标签进行匹配筛选。
- **灵活排序**：可按粉丝数、曝光量、预算等任意属性排序。
- **可扩展性**：数据结构、标签提取、排序逻辑均易于扩展。

## 依赖环境

- Python 3.8+
- torch
- transformers
- qwen_vl_utils（需自备或参考 Qwen2.5-VL 官方仓库）

## 快速开始

1. **安装依赖**（建议在 conda 虚拟环境中）：
   ```bash
   pip install torch transformers
   # 需准备 Qwen2.5-VL-32B-Instruct-AWQ 权重和 qwen_vl_utils
   ```

2. **准备模型权重**
   - 将 Qwen2.5-VL-32B-Instruct-AWQ 权重放在 `./models/Qwen2.5-VL-32B-Instruct-AWQ` 目录下。

3. **运行示例**
   在项目根目录下运行：
   ```bash
   python -m matching.influencer_product_matching
   ```
   - 会自动演示达人数据库、视频标签提取、标签添加、搜索与排序。

## 主要模块说明

### influencer_product_matching.py
- `Influencer`：达人数据结构，支持任意属性和标签。
- `extract_video_tags(videos: List[str])`：批量调用大模型分析视频，抽取 hash tag。
- `add_video_tags_to_influencer(influencer, video_tags)`：将标签添加到达人。
- `filter_user_input`、`match_influencers`、`sort_influencers`：搜索与排序逻辑。

### video_to_text.py
- `video_to_text(video_url: str, prompt: str)`：调用 Qwen2.5-VL 多模态模型，将视频内容转为文本（可用于标签抽取、内容理解等）。

## 扩展建议
- 可对接真实达人数据库、商品库。
- 可扩展更复杂的标签提取、语义匹配、排序权重。
- 可集成前端或 API 服务，实现交互式达人筛选。

## 注意事项
- 需保证模型权重和依赖齐全，显卡显存充足。
- 视频标签抽取依赖大模型推理，速度受硬件影响。

---
如有问题或需求，欢迎 issue 或联系开发者。 

# 以上无用

服务端启动：
gunicorn -w 1 -b 0.0.0.0:5000 matching.video_to_text_server:app --timeout 600

服务器视频下载（国内服务器需要vpn）：
sudo ./clash -d .（clash和配置文件在同一路径下）
python download_specific_video.py
实质上是用cmd = [
                'yt-dlp',
                '--proxy', 'http://127.0.0.1:7890',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '-o', output_filename,
                url
            ]
从url下载视频到服务器本地

11条视频内容分析用例：
python batch_curl_requests.py
结果存储在batch_results.json中

