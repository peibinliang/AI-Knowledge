# AI-Knowledge

面向企业技术团队、CSM 与项目经理的 AI、科技产品与工程实践资讯仓库。

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

## 企业产品资讯快报

新增一条独立于综合日报的企业产品资讯专线，面向 **CSM / 客户成功 / 项目经理**，重点跟踪：

- 钉钉 / DingTalk
- 飞书 / Feishu / Lark
- 企业微信 / WeCom
- TRAE Work
- 千问办公 / Qwen Work
- WorkBuddy / Work Buddy
- 腾讯会议、腾讯文档
- WPS / 金山办公
- Microsoft 365 / Teams
- Google Workspace
- Slack
- 其他主流企业协作、AI 办公和企业服务产品

关注内容包括：**新功能、版本升级、AI/Agent 能力、开放平台/API、身份与安全、套餐与价格、兼容性与下线计划、客户案例和行业解决方案**。

每条资讯优先回答：

1. 发生了什么；
2. 对企业客户有什么影响；
3. CSM 是否需要主动通知、培训、续费或方案升级跟进；
4. 项目经理是否需要做兼容性测试、排期调整或需求评估；
5. 官方或高可信来源是什么。

详细格式见 [`enterprise-products/README.md`](enterprise-products/README.md)。

## 自动推送到钉钉

仓库目前有两条相互独立的 GitHub Actions 推送链路。

### 1. 综合 AI / 科技日报

当新增或更新 `daily/YYYY-MM-DD.md` 时：

```text
ChatGPT 定时任务
    ↓
生成并更新 daily/YYYY-MM-DD.md
    ↓
GitHub push
    ↓
.github/workflows/daily-ai-briefing.yml
    ↓
scripts/push_dingtalk.py
    ↓
钉钉群机器人
```

钉钉消息自动整理：**今日摘要、五大栏目重点、今日行动点、GitHub 完整简报链接**。

### 2. 企业产品资讯专线

当新增或更新 `enterprise-products/YYYY-MM-DD.md` 时：

```text
企业产品资讯生成/维护
    ↓
enterprise-products/YYYY-MM-DD.md
    ↓
GitHub push
    ↓
.github/workflows/enterprise-product-briefing.yml
    ↓
scripts/push_enterprise_products.py
    ↓
CSM / 项目经理钉钉群
```

该消息只聚焦企业产品变化，并突出：**客户影响、CSM 关注、项目交付影响和可跟进行动**。

### GitHub Secrets

综合日报使用：

- `DINGTALK_WEBHOOK`
- `DINGTALK_SECRET`（启用加签时）

企业产品资讯推荐单独使用：

- `ENTERPRISE_DINGTALK_WEBHOOK`
- `ENTERPRISE_DINGTALK_SECRET`（启用加签时）

如果没有配置企业专用 Secret，企业产品推送脚本会自动回退到 `DINGTALK_WEBHOOK` / `DINGTALK_SECRET`。

> 不要把 Webhook access token 或签名密钥提交到仓库文件中。

### 手动测试

综合日报：`Actions → Push Daily Briefing to DingTalk → Run workflow`。

企业产品资讯：`Actions → Push Enterprise Product Briefing to DingTalk → Run workflow`。

企业产品 workflow 可指定例如：

```text
enterprise-products/2026-08-17.md
```

留空时自动选择 `enterprise-products/` 中日期最新的快报。

## 目录结构

```text
AI-Knowledge/
├── .github/
│   └── workflows/
│       ├── daily-ai-briefing.yml
│       └── enterprise-product-briefing.yml
├── scripts/
│   ├── push_dingtalk.py
│   └── push_enterprise_products.py
├── daily/
│   └── YYYY-MM-DD.md
├── enterprise-products/
│   ├── README.md
│   └── YYYY-MM-DD.md
└── README.md
```

## 内容原则

- 优先引用官方公告、厂商技术文档、Release Notes、主流通讯社、权威科技媒体等可信来源。
- 区分事实、分析与趋势判断，不把传闻写成确定事实。
- 对同一事件多来源去重，优先保留一手来源并用高可信媒体交叉验证。
- 综合日报中，国内与全球 AI 目标各筛选 10 条；当高价值确证信息不足时可以少于目标数量。
- 企业产品资讯只记录有实质产品、功能、API、定价、兼容性、交付或商业化影响的变化，不为了凑数重复旧闻。
- GitHub 推荐不仅参考总 Star，还关注近期提交、方向代表性和企业可落地性。
