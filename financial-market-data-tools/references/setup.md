# 环境准备

## A 股：Tushare Pro

需要环境变量：

```bash
export TUSHARE_TOKEN="你的 tushare token"
```

说明：

- 脚本直接调用 Tushare Pro 的 HTTP 接口
- 常见入口是 `daily`、`daily_basic`、`stock_basic`
- 也可以通过 `query` 直接访问其他 `api_name`

## 港股：Futu OpenD

需要：

```bash
pip install futu-api
```

以及本地或远端已启动 OpenD，常用环境变量：

```bash
export FUTU_HOST="127.0.0.1"
export FUTU_PORT="11111"
```

如果使用当前这台机器上已经下载好的 OpenD，命令行版位置是：

```bash
/root/tools/Futu_OpenD_10.2.6208_Ubuntu18.04/Futu_OpenD_10.2.6208_Ubuntu18.04/FutuOpenD
```

配置文件位置是：

```bash
/root/tools/Futu_OpenD_10.2.6208_Ubuntu18.04/Futu_OpenD_10.2.6208_Ubuntu18.04/FutuOpenD.xml
```

说明：

- 快照用 `get_market_snapshot`
- 历史 K 线用 `request_history_kline`
- 实时 K 线需要订阅，当前脚本优先暴露更稳的快照和历史 K 线能力
- 首次登录或风控触发时，命令行 OpenD 可能提示 `input_phone_verify_code -code=你的验证码`

当前这套环境的已验证情况：

- `TUSHARE_TOKEN` 已验证可用
- `FutuOpenD` 已完成账号密码与手机验证码登录
- 美股路径优先用 `yfinance`，不可用时回退 Yahoo Chart

## 美股：Alpha Vantage / Yahoo / yfinance

### Alpha Vantage（首选）

免费注册 API Key：https://www.alphavantage.co/support/#api-key

```bash
export ALPHA_VANTAGE_API_KEY="你的 Alpha Vantage API Key"
```

说明：

- 免费额度：每日 25 次请求，5 次/分钟
- 支持美股即时报价（GLOBAL_QUOTE）和日线历史（TIME_SERIES_DAILY）
- 数据稳定，适合日常投研查询
- 调用示例：`--provider alpha_vantage`

### yfinance（备选）

可选安装：

```bash
pip install yfinance
```

说明：

- Yahoo Finance Python 客户端，数据完整
- 可能被 rate limit（当前 IP 已被 Yahoo 限制）
- 使用：`--provider yfinance`

### Yahoo Chart（最后保底）

无需额外依赖，直接请求 Yahoo Finance Chart 接口。
使用：`--provider chart`

默认 provider 优先级为：`alpha_vantage` → `yfinance` → `chart`。
