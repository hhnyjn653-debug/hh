# hh 自动化中台（Playwright + Ozon API）

一个最小可用模板：

- 用 **Playwright** 处理必须走网页 UI 的流程（例如妙手/TEMU/TK 的页面操作）
- 用 **Ozon API** 直接拉取结构化数据（商品、库存、订单等）
- 预留任务队列与 AI 调用位，只在需要文本生成时用模型，减少 token 消耗

## 1. 环境准备

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## 2. 配置环境变量

复制并填写：

```bash
cp .env.example .env
```

关键配置：

- `OZON_CLIENT_ID` / `OZON_API_KEY`：Ozon Seller API 凭证
- `MS_USERNAME` / `MS_PASSWORD`：妙手登录账号（示例）
- `BASE_HEADLESS`：`true/false`，是否无头模式

## 3. 运行示例

### 3.1 拉取 Ozon 商品列表（API 直连）

```bash
python -m src.main ozon-products
```

### 3.2 跑一个浏览器自动化任务（妙手登录示例）

```bash
python -m src.main browser-login
```

## 4. 目录结构

```text
src/
  main.py                  # 统一入口
  config.py                # 配置加载
  clients/
    ozon_client.py         # Ozon API 客户端
  automations/
    browser_flow.py        # Playwright 自动化流程
```

## 5. 设计建议（降本）

1. **能 API 就 API**：优先直连 Ozon，减少页面抓取。
2. **UI 自动化只做“最后一公里”**：只跑无法 API 化的动作。
3. **LLM 只做决策，不做搬运**：结构化数据处理走代码逻辑。
4. **任务切分**：采集 / 清洗 / 发布解耦，失败可重试。
