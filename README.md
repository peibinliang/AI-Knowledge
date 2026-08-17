# AI-Knowledge

面向企业技术团队与技术管理者的 AI、科技产品与工程实践每日资讯仓库。

## 每日简报

每日简报固定跟踪以下 5 个方向：

1. **中国 AI / 大模型 / 智能体资讯**：模型发布、Agent、AI Coding、产业政策、AI 基础设施与商业化动态。
2. **全球 AI / 大模型 / Agent 应用资讯**：OpenAI、Anthropic、Google、Microsoft、Meta、NVIDIA、AWS 等全球厂商以及重要创业公司与研究机构。
3. **中国重点科技企业产品迭代**：重点跟踪钉钉、飞书、企业微信、阿里云、火山引擎、智谱、月之暗面、DeepSeek，以及百度智能云、腾讯云、华为云、MiniMax 等。
4. **全球 3C / 消费电子动态**：手机、电脑、平板、可穿戴、XR/AR、AI PC、AI 手机、智能家居以及重要发布会。
5. **GitHub AI 项目推荐**：Agent、AI Coding、RAG、MCP、模型部署、推理、知识库和多 Agent 编排等近期高价值项目。

内容优先覆盖过去 24 小时的重要变化，必要时补充过去一周仍具有持续影响的事件。各栏目按**时效、技术价值、企业可落地性**筛选，不为了固定数量重复旧闻或低价值更新。

### 最新简报

- [2026-08-17｜AI 与科技每日简报（新版）](daily/2026-08-17.md)
- [2026-08-16｜AI 与科技每日简报](daily/2026-08-16.md)
- [2026-08-15｜AI 与科技每日简报](daily/2026-08-15.md)
- [2026-08-14｜AI 与科技每日简报](daily/2026-08-14.md)
- [2026-08-13｜AI 与科技每日简报](daily/2026-08-13.md)
- [2026-08-12｜AI 与科技每日简报](daily/2026-08-12.md)

## 自动推送到钉钉

仓库通过 GitHub Actions 将新增或更新的 `daily/YYYY-MM-DD.md` 自动推送到钉钉群机器人。

执行链路：

```text
ChatGPT 定时任务
    ↓
生成并更新 daily/YYYY-MM-DD.md
    ↓
GitHub push 事件
    ↓
.github/workflows/daily-ai-briefing.yml
    ↓
scripts/push_dingtalk.py
    ↓
钉钉群机器人
```

钉钉消息不会复制完整长文，而是自动整理：**今日摘要、五大栏目重点、今日行动点、GitHub 完整简报链接**。

### 必需的 GitHub Secret

进入仓库：`Settings → Secrets and variables → Actions → New repository secret`，配置：

- `DINGTALK_WEBHOOK`：钉钉自定义机器人完整 Webhook 地址，必填。
- `DINGTALK_SECRET`：如果机器人开启“加签”安全设置，则填写机器人签名密钥；未开启加签可不配置。

> 不要把 Webhook access token 或签名密钥提交到仓库文件中。

### 手动测试

配置 Secret 后，可以进入 `Actions → Push Daily Briefing to DingTalk → Run workflow`。

- `briefing` 留空：自动选择 `daily/` 中日期最新的简报。
- 或指定路径，例如 `daily/2026-08-17.md`。

正常情况下，Action 会显示 `Sent DingTalk message 1/1`；若钉钉返回关键词、签名、IP 白名单或限流错误，workflow 会失败并在日志中保留钉钉返回信息。

## 目录结构

```text
AI-Knowledge/
├── .github/
│   └── workflows/
│       └── daily-ai-briefing.yml
├── scripts/
│   └── push_dingtalk.py
├── daily/
│   └── YYYY-MM-DD.md
└── README.md
```

## 内容原则

- 优先引用官方公告、厂商技术文档、主流通讯社、权威科技媒体、研究论文等可信来源。
- 区分事实、分析与趋势判断，不把传闻写成确定事实。
- 对同一事件多来源去重，优先保留一手来源并用高可信媒体交叉验证。
- 国内与全球 AI 目标各筛选 10 条；当高价值确证信息不足时可以少于目标数量，并明确说明。
- 中国重点科技企业只记录有实质产品、模型、API、定价或商业化变化的更新。
- GitHub 推荐不仅参考总 Star，还关注近期提交、方向代表性和企业可落地性。
- 每期最后给出 **5 个值得立即行动、架构评估或持续观察的方向**。
