# Financial Market Data Tools

跨市场行情数据抓取技能，封装 A 股、港股和美股数据源。

## 安装

### 前置要求

- Python 3.10+
- pip

### 1. 安装 Python 包

```bash
# 基础安装
pip install .

# 安装全部依赖（含港股和美股数据源）
pip install ".[all]"
```

**跨平台说明**:
- **Linux/macOS**: 终端运行 `pip install .` 或 `pip3 install .`
- **Windows**: 打开 PowerShell 或 CMD，运行相同命令

### 2. 配置环境变量

根据你需要使用的数据源，配置以下环境变量：

#### A 股 — Tushare Pro

```bash
# Linux/macOS
export TUSHARE_TOKEN="你的Token"

# Windows PowerShell
$env:TUSHARE_TOKEN="你的Token"
```

**获取方式**: 注册 https://tushare.pro/register

#### 港股 — Futu OpenD

**第一步**: 下载安装 Futu OpenD 网关
- Linux: https://www.futunn.com/down?lang=cn (选择 Linux 版本)
- macOS: https://www.futunn.com/down?lang=cn (选择 macOS 版本)
- Windows: https://www.futunn.com/down?lang=cn (选择 Windows 版本)

**第二步**: 启动 Futu OpenD 并登录账号

**第三步**: 配置环境变量（默认已启动在本机）

```bash
# Linux/macOS
export FUTU_HOST="127.0.0.1"
export FUTU_PORT="11111"

# Windows PowerShell
$env:FUTU_HOST="127.0.0.1"
$env:FUTU_PORT="11111"
```

#### 美股 — Alpha Vantage (可选)

```bash
# Linux/macOS
export ALPHA_VANTAGE_API_KEY="你的APIKey"

# Windows PowerShell
$env:ALPHA_VANTAGE_API_KEY="你的APIKey"
```

**获取方式**: 免费注册 https://www.alphavantage.co/support/#api-key

**备选方案**: 无需 API Key，使用 yfinance (已包含在 `pip install ".[all]"` 中)

## 手动安装为 Skills 技能包

### Claude Code (Linux/macOS/Windows)

将本目录复制到 Claude Code 技能目录：

```bash
# Linux/macOS
cp -r financial-market-data-tools ~/.claude/skills/

# Windows (PowerShell)
Copy-Item -Recurse financial-market-data-tools "$env:USERPROFILE\.claude\skills\"
```

### Codex Skills

```bash
# Linux/macOS
cp -r financial-market-data-tools ~/.codex/skills/

# Windows (PowerShell)
Copy-Item -Recurse financial-market-data-tools "$env:USERPROFILE\.codex\skills\"
```

## Skills 市场安装 (Coming Soon)

> **待完善**: OpenClaw / Codex / Claude Code Skills Market 安装说明

## 数据源支持

| 市场 | 数据源 | 必需工具 | 依赖包 |
|------|--------|----------|--------|
| A 股 | Tushare Pro | 无 | requests |
| 港股 | Futu OpenD | OpenD 网关 | futu-api |
| 美股 | Alpha Vantage / yfinance | 无 / 无 | requests / yfinance |
