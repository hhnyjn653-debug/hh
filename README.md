# hh

自动化电商增长编排（OpenClaw / OpenCloud 接入）。

## 快速开始
```bash
python3 src/orchestrator.py
```

## 你只需要提供
- 小红书/抖音/闲鱼/拼多多账号
- OpenClaw/OpenCloud API 地址和密钥
- （可选）DeepSeek API 密钥（用于任务智能规划）

## 环境变量
- `OPENCLOW_BASE_URL`：OpenClaw/OpenCloud 基础地址
- `OPENCLOW_API_KEY`：OpenClaw/OpenCloud 鉴权
- `DEEPSEEK_API_KEY`：DeepSeek 鉴权（可选但推荐）
- `DEEPSEEK_MODEL`：默认 `deepseek-chat`
- `DEEPSEEK_BASE_URL`：默认 `https://api.deepseek.com`

## 核心能力
- 自动定位与简介优化
- 自动比价与蓝海需求发现
- 自动上架与活动匹配报名
- 自动客服转化与售后反馈优化
- DeepSeek 驱动的任务参数优化（避免红海、优先蓝海）

详见：`docs/opclaw_workflow.md`
