# Investment Advisor Suite

投资分析技能套件，提供跨市场行情数据和中文投资问答能力。

## 技能包

### 1. Financial Market Data Tools

[financial-market-data-tools/](financial-market-data-tools/)

跨市场行情数据工具，支持 A 股、港股和美股数据源。

**支持数据源**:

| 市场 | 数据源 | 依赖工具 |
|------|--------|----------|
| A 股 | Tushare Pro | 无 |
| 港股 | Futu OpenD | OpenD 网关 |
| 美股 | Alpha Vantage / yfinance | 无 |

### 2. Using Financial Advisor Codex

[using-financial-advisor/](using-financial-advisor/)

中文优先的投资问答技能，提供任务分流和信息收集能力。

**触发条件**: 用户以投资者视角提问（行情查询、产品比较、组合诊断、交易决策等）

## 快速开始

### 1. 安装 Python 包

```bash
# 基础安装
pip install .

# 安装全部依赖（含港股和美股）
pip install ".[all]"
```

### 2. 配置数据源环境变量

根据你需要的数据源配置：

```bash
# A 股
export TUSHARE_TOKEN="your_token"

# 港股 (需先安装 Futu OpenD)
export FUTU_HOST="127.0.0.1"
export FUTU_PORT="11111"

# 美股
export ALPHA_VANTAGE_API_KEY="your_api_key"
```

详细配置请参考各技能包 README。

### 3. 安装为 Skills 技能包

#### Claude Code

```bash
# Linux/macOS
cp -r financial-market-data-tools using-financial-advisor ~/.claude/skills/

# Windows
Copy-Item -Recurse financial-market-data-tools, using-financial-advisor "$env:USERPROFILE\.claude\skills\"
```

#### Codex Skills

```bash
# Linux/macOS
cp -r financial-market-data-tools using-financial-advisor ~/.codex/skills/

# Windows
Copy-Item -Recurse financial-market-data-tools, using-financial-advisor "$env:USERPROFILE\.codex\skills\"
```

## Skills 市场安装 (Coming Soon)

> **待完善**: OpenClaw / Codex / Claude Code Skills Market 安装说明

## 跨平台支持

- **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 10+
- **macOS**: macOS 10.15+
- **Windows**: Windows 10/11

## License

MIT License
