# 企业产品资讯快报

本目录用于沉淀面向 **CSM（客户成功）与项目经理** 的企业级产品资讯，和 `daily/` 下的综合 AI / 科技日报相互独立。

## 固定跟踪范围

优先持续跟踪以下企业协作、AI 办公与企业服务产品：

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
- 其他出现重大功能升级、商业化调整或企业客户影响的同类产品

## 收录标准

只收录对企业客户、交付项目或客户成功工作有实际价值的信息，重点包括：

1. 新产品、新版本、新功能或重大体验升级；
2. AI 助手、Agent、知识库、会议、文档、搜索、自动化等能力升级；
3. API、开放平台、Webhook、身份认证、权限、安全、集成能力变化；
4. 价格、套餐、计费、免费额度、商业化策略变化；
5. 兼容性、下线计划、迁移要求、产品限制或重大 Bug / 风险；
6. 对企业客户采购、续费、实施、交付、培训和推广可能产生影响的变化；
7. 具有代表性的客户案例、生态合作或行业解决方案更新。

不为了凑数量重复旧闻；同一事件优先引用官方公告、产品文档、Release Notes、官方公众号或官方开发者文档，并可用可信媒体补充验证。

## 文件命名

```text
enterprise-products/YYYY-MM-DD.md
```

只有符合 `YYYY-MM-DD.md` 格式的文件才会自动触发独立的企业产品资讯 GitHub Action；本 README 不会触发推送。

## 推荐内容结构

```markdown
# YYYY-MM-DD｜企业产品资讯快报

## 今日摘要

- 今天最值得 CSM / 项目经理关注的 3—5 个变化。

## 产品动态

### 钉钉

**发生了什么**：...

**客户影响**：...

**CSM 建议**：...

**项目经理关注**：...

来源：[官方来源](...)

### 飞书
...

### 企业微信
...

### TRAE Work
...

### 千问办公
...

### WorkBuddy
...

## CSM 重点关注

1. 哪些变化需要主动通知客户；
2. 哪些变化可以形成增购、续费、培训或方案升级机会；
3. 哪些客户可能需要重新评估产品能力。

## 项目经理重点关注

1. 哪些变化会影响当前项目范围、接口、排期或验收；
2. 哪些版本升级需要安排兼容性测试；
3. 哪些新功能可纳入后续迭代或客户方案。

## 今日行动建议

1. ...
2. ...
3. ...
```

## GitHub Actions 推送

独立工作流：

```text
.github/workflows/enterprise-product-briefing.yml
```

推送脚本：

```text
scripts/push_enterprise_products.py
```

当 `enterprise-products/YYYY-MM-DD.md` 被新增或更新到 `main` 后，Action 会自动将企业产品快报精简后推送到钉钉群。

### Secret 配置

推荐为企业产品专线单独创建：

- `ENTERPRISE_DINGTALK_WEBHOOK`
- `ENTERPRISE_DINGTALK_SECRET`（机器人启用加签时配置）

如果没有单独配置，脚本会回退使用综合日报已有的：

- `DINGTALK_WEBHOOK`
- `DINGTALK_SECRET`

这样既可以让企业产品情报发送到独立群，也可以复用现有群机器人。
