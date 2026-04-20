# Using Financial Advisor Codex

中文优先的投资分析与市场问答技能，适用于股票、基金、ETF、债券、指数等投资场景。

## 触发条件

当用户以投资者视角提问时触发，例如：

- 查询行情或产品信息
- 比较股票/基金/ETF
- 解读财务或市场信息
- 诊断投资组合
- 讨论买入、卖出、持有、仓位、配置和再平衡

**不触发**: 纯会计、记账、或泛公司金融讨论（除非用户在做投资判断）

## 前置依赖

本技能依赖 `financial-market-data-tools` 提供市场数据。

请先完成 [financial-market-data-tools](../financial-market-data-tools/) 的安装。

## 手动安装为 Skills 技能包

### Claude Code (Linux/macOS/Windows)

将本目录复制到 Claude Code 技能目录：

```bash
# Linux/macOS
cp -r using-financial-advisor ~/.claude/skills/

# Windows (PowerShell)
Copy-Item -Recurse using-financial-advisor "$env:USERPROFILE\.claude\skills\"
```

### Codex Skills

```bash
# Linux/macOS
cp -r using-financial-advisor ~/.codex/skills/

# Windows (PowerShell)
Copy-Item -Recurse using-financial-advisor "$env:USERPROFILE\.codex\skills\"
```

## Skills 市场安装 (Coming Soon)

> **待完善**: OpenClaw / Codex / Claude Code Skills Market 安装说明

## 使用示例

在 Claude Code 或 Codex 中，当用户以投资者身份提问时，技能自动激活并调用 `financial-market-data-tools` 获取实时数据，给出分析结论和风险提示。
