# CLI 示例

## Tushare Pro

查询 A 股日线：

```bash
python3 scripts/tushare_pro_tool.py daily \
  --ts-code 600519.SH \
  --start-date 20250101 \
  --end-date 20250415
```

查询每日指标：

```bash
python3 scripts/tushare_pro_tool.py daily-basic \
  --ts-code 600519.SH \
  --start-date 20250101 \
  --end-date 20250415
```

直接调用任意接口：

```bash
python3 scripts/tushare_pro_tool.py query \
  --api-name stock_basic \
  --params '{"exchange":"","list_status":"L"}' \
  --fields 'ts_code,symbol,name,area,industry,list_date'
```

## Futu OpenD

先启动 OpenD：

```bash
cd /root/tools/Futu_OpenD_10.2.6208_Ubuntu18.04/Futu_OpenD_10.2.6208_Ubuntu18.04
./FutuOpenD
```

如果终端提示：

```bash
input_phone_verify_code -code=123456
```

就在同一个终端输入真实验证码，例如：

```bash
input_phone_verify_code -code=885129
```

查询港股快照：

```bash
env FUTU_HOST=127.0.0.1 FUTU_PORT=11111 python3 scripts/futu_opend_tool.py snapshot --code 00700 --code 09988
```

查询历史 K 线：

```bash
env FUTU_HOST=127.0.0.1 FUTU_PORT=11111 python3 scripts/futu_opend_tool.py history-kline \
  --code HK.00700 \
  --start 2025-01-01 \
  --end 2025-04-15 \
  --ktype K_DAY
```

## Yahoo / yfinance / Alpha Vantage

### Alpha Vantage（首选）

查询美股报价：

```bash
python3 scripts/yahoo_market_tool.py quote --symbol AAPL --provider alpha_vantage
```

查询美股历史 K 线：

```bash
python3 scripts/yahoo_market_tool.py history \
  --symbol MSFT \
  --period 6mo \
  --interval 1d \
  --provider alpha_vantage
```

### Yahoo Chart

查询美股报价（无需 API Key）：

```bash
python3 scripts/yahoo_market_tool.py quote --symbol AAPL --provider chart
```

查询美股历史 K 线：

```bash
python3 scripts/yahoo_market_tool.py history \
  --symbol MSFT \
  --period 6mo \
  --interval 1d \
  --provider chart
```

### yfinance

查询美股报价：

```bash
python3 scripts/yahoo_market_tool.py quote --symbol AAPL --provider yfinance
```
