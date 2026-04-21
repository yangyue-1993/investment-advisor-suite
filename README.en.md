# Investment Advisor Suite

[中文说明](README.zh-CN.md)

An investment skills suite that provides cross-market financial data tools and Chinese-first investment Q&A capabilities.

## Skill Packages

### 1. Financial Market Data Tools

[financial-market-data-tools/](financial-market-data-tools/)

Cross-market market data tools for A-shares, Hong Kong stocks, and U.S. stocks.

**Supported data sources**:

| Market | Data Source | Dependency |
|--------|-------------|------------|
| A-shares | Tushare Pro | None |
| Hong Kong | Futu OpenD | OpenD gateway |
| U.S. | Alpha Vantage / yfinance | None |

### 2. Using Financial Advisor Codex

[using-financial-advisor/](using-financial-advisor/)

A Chinese-first investment Q&A skill focused on task routing and structured information intake.

**Trigger condition**: The user is asking from an investor perspective, such as market quotes, product comparison, portfolio diagnosis, or trading decisions.

## Quick Start

### 1. Install the Python package

```bash
# Basic installation
pip install .

# Install all optional dependencies, including Hong Kong and U.S. market support
pip install ".[all]"
```

### 2. Configure environment variables for data sources

Set only the variables required by the data sources you want to use:

```bash
# A-shares
export TUSHARE_TOKEN="your_token"

# Hong Kong market (requires Futu OpenD)
export FUTU_HOST="127.0.0.1"
export FUTU_PORT="11111"

# U.S. market
export ALPHA_VANTAGE_API_KEY="your_api_key"
```

See each skill package README for detailed setup instructions.

### 3. Install as skills

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

## Skills Marketplace Installation

> Coming soon: installation guidance for OpenClaw / Codex / Claude Code skill marketplaces.

## Platform Support

- **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 10+
- **macOS**: macOS 10.15+
- **Windows**: Windows 10/11

## License

MIT License
