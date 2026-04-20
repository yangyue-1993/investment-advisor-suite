# 数据源说明

## Tushare Pro

本技能按官方 HTTP 方式封装，请求体包含：

- `api_name`
- `token`
- `params`
- `fields`

返回体中的 `data.fields` 与 `data.items` 会被脚本转换成 `rows` 结构，方便上游技能直接读取。

## Futu OpenD

本技能按 Futu OpenD + Python SDK 的模式封装。
港股默认使用：

- `get_market_snapshot`
- `request_history_kline`

若本地缺少 `futu` SDK 或 OpenD 未启动，脚本会返回明确错误信息。
如果 OpenD 还未完成手机验证码验证，脚本通常会拿到“需要手机验证码”或连接初始化失败。

## Yahoo / yfinance

优先路径：

- `yfinance.Ticker.get_fast_info()`
- `yfinance.Ticker.history()`

回退路径：

- Yahoo Finance Chart 接口

建议：

- 做在线联调或轻量报价时，优先显式使用 `--provider chart`
- 需要更多字段时，再尝试 `--provider yfinance` 或默认 `auto`

回退路径只覆盖基础报价和 K 线，不承诺完整基本面字段。
当 `yfinance` 返回空对象或网络异常时，脚本会尝试继续回退，而不是直接崩溃。
