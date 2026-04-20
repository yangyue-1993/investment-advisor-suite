---
name: financial-market-data-tools
description: 为投资分析和市场问答提供跨市场行情数据工具，按市场路由到 Tushare Pro、Futu OpenD、Yahoo/yfinance 和 Alpha Vantage，适用于需要查询 A 股、港股、美股的近期价格、K 线、基础信息和快照数据时。
---

# 使用 Financial Market Data Tools

## 概览

这套技能把跨市场数据获取拆成 3 个独立脚本工具：

- A 股：`scripts/tushare_pro_tool.py`
- 港股：`scripts/futu_opend_tool.py`
- 美股：`scripts/yahoo_market_tool.py`（支持 Alpha Vantage、yfinance、Yahoo Chart 三种 provider）

默认先按市场选源，再选命令。
输出统一为 JSON，便于上游技能直接引用、总结或二次处理。

## 市场路由

- A 股、ETF、指数、基金的中国市场数据：优先用 `scripts/tushare_pro_tool.py`
- 港股实时快照和港股 K 线：优先用 `scripts/futu_opend_tool.py`
- 美股行情和历史 K 线：优先用 `scripts/yahoo_market_tool.py`，provider 优先级为 `alpha_vantage` → `yfinance` → `chart`

如果用户没有明确市场：

- `600519.SH`、`000001.SZ`、`510300.SH` 这类代码按 A 股处理
- `00700.HK`、`700`、`HK.00700` 这类代码按港股处理
- `AAPL`、`MSFT`、`SPY` 这类代码按美股处理

## 工具目录

### 1. Tushare Pro

脚本：`scripts/tushare_pro_tool.py`

适合：

- A 股日线
- A 股基础资料
- A 股每日指标
- 其他 Tushare Pro 可用接口的泛化查询

首次运行前，先确认 `TUSHARE_TOKEN` 已配置。
如果要查非常规接口，优先使用 `query` 子命令直接传 `api_name` 和 `params`。

### 2. Futu OpenD

脚本：`scripts/futu_opend_tool.py`

适合：

- 港股实时快照
- 港股历史 K 线
- 需要 OpenD 本地网关支持的行情查询

首次运行前，先确认：

- 本机已安装 `futu` Python SDK
- OpenD 已启动
- `FUTU_HOST` 和 `FUTU_PORT` 可连通
- 如触发风控或首次登录，按 OpenD 终端提示输入手机验证码

### 3. Yahoo / yfinance / Alpha Vantage

脚本：`scripts/yahoo_market_tool.py`

适合：

- 美股即时概览
- 美股历史 K 线
- ETF 或指数类美股标的的基础行情

该脚本支持三种 provider，按以下优先级自动选择：

1. `alpha_vantage`（`--provider alpha_vantage`）：Alpha Vantage API，免费注册，稳定可靠，适合日常查询（每日 25 次限制）。需配置 `ALPHA_VANTAGE_API_KEY` 环境变量。
2. `yfinance`（`--provider yfinance`）：Yahoo Finance Python 客户端，数据完整，但可能被 rate limit。需本地安装 `yfinance`。
3. `chart`（`--provider chart`）：直接请求 Yahoo Finance Chart 接口，无需额外依赖，但稳定性较低。

使用 `--provider auto`（默认）时，按上述优先级自动尝试。

## 运行规则

1. 任何“今天、最新、最近、当前价格”类问题，都在回答里写出脚本实际核验时刻。
2. 如果数据源不可用，不要假装拿到了数据；明确说出缺的是 token、SDK、OpenD 还是网络。
3. 优先用最小够用命令，不要为了简单报价调用过重接口。
4. 对于需要复盘、比较区间表现或技术分析的问题，优先拉历史 K 线而不是只看单点报价。
5. 当多个数据源都能覆盖时，以用户指定的数据源优先；否则按本技能的市场路由处理。

## 常用命令

具体示例见：

- [references/setup.md](references/setup.md)
- [references/cli-examples.md](references/cli-examples.md)
- [references/source-notes.md](references/source-notes.md)

如果是本机当前这套环境，OpenD 命令行可执行文件在：

- `/root/tools/Futu_OpenD_10.2.6208_Ubuntu18.04/Futu_OpenD_10.2.6208_Ubuntu18.04/FutuOpenD`

## 给上游技能的调用约定

上游技能需要时效性市场数据时：

1. 先读取本技能
2. 选择对应市场脚本
3. 执行脚本并读取 JSON 输出
4. 在最终回答里写清楚数据源和日期

如果上游技能是 `using-financial-advisor`，优先遵循这里的市场路由，不要自行编造实时数据获取流程。
