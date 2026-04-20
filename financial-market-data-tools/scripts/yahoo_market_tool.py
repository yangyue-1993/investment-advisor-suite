#!/usr/bin/env python3

import argparse
from datetime import datetime, timezone
from typing import Any

import requests

from common import ToolError, dataframe_to_records, emit, error_payload, ok_payload


YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"
DEFAULT_TIMEOUT = 30


def normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def maybe_load_yfinance() -> Any | None:
    try:
        import yfinance as yf  # type: ignore
    except ImportError:
        return None
    return yf


def to_unix_timestamp(raw: str) -> int:
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        try:
            dt = datetime.strptime(raw, "%Y-%m-%d")
        except ValueError as exc:
            raise ToolError(
                "Invalid date format for --start/--end.",
                hint="Use YYYY-MM-DD or a full ISO datetime.",
                details={"value": raw},
            ) from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def fetch_chart(
    symbol: str,
    *,
    interval: str,
    period: str | None,
    start: str | None,
    end: str | None,
) -> dict[str, Any]:
    params: dict[str, Any] = {"interval": interval}
    if start or end:
        if start:
            params["period1"] = to_unix_timestamp(start)
        if end:
            params["period2"] = to_unix_timestamp(end)
    else:
        params["range"] = period or "1mo"

    try:
        response = requests.get(
            YAHOO_CHART_URL.format(symbol=symbol),
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ToolError(
            "Failed to reach Yahoo Finance.",
            hint="Check network access or install yfinance for the primary path.",
            details=str(exc),
        ) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise ToolError(
            "Yahoo Finance returned a non-JSON response.",
            details=response.text[:500],
        ) from exc

    result = (payload.get("chart") or {}).get("result") or []
    if not result:
        raise ToolError(
            "Yahoo Finance did not return chart data.",
            details=(payload.get("chart") or {}).get("error"),
        )
    return result[0]


def _load_alpha_vantage_key() -> str | None:
    import os
    return os.environ.get("ALPHA_VANTAGE_API_KEY")


def _call_alpha_vantage(function: str, params: dict[str, Any], api_key: str) -> dict[str, Any]:
    params["function"] = function
    params["apikey"] = api_key
    try:
        response = requests.get(ALPHA_VANTAGE_URL, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ToolError(
            "Failed to reach Alpha Vantage.",
            hint="Check network access and API key.",
            details=str(exc),
        ) from exc
    try:
        return response.json()
    except ValueError as exc:
        raise ToolError(
            "Alpha Vantage returned non-JSON.",
            details=response.text[:500],
        ) from exc


def quote_with_alpha_vantage(symbol: str) -> dict[str, Any]:
    api_key = _load_alpha_vantage_key()
    if not api_key:
        raise ToolError(
            "ALPHA_VANTAGE_API_KEY is not set.",
            hint="Set ALPHA_VANTAGE_API_KEY in environment.",
        )
    data = _call_alpha_vantage(
        "GLOBAL_QUOTE",
        {"symbol": symbol},
        api_key,
    )
    quote_data = (data.get("Global Quote") or {}) or (data.get("Note") and {})
    if not quote_data or "Note" in data:
        raise ToolError(
            "Alpha Vantage quota exceeded or invalid symbol.",
            details=data,
        )
    q = quote_data
    return {
        "provider": "alpha_vantage",
        "quote": {
            "symbol": q.get("01. symbol"),
            "last_price": float(q.get("05. price", 0)) or None,
            "previous_close": float(q.get("08. previous close", 0)) or None,
            "open": float(q.get("02. open", 0)) or None,
            "day_high": float(q.get("03. high", 0)) or None,
            "day_low": float(q.get("04. low", 0)) or None,
            "volume": int(q.get("06. volume", 0)) or None,
            "change": float(q.get("09. change", 0)) or None,
            "change_pct": float(q.get("10. change percent", "").rstrip("%")) or None,
        },
    }


def history_with_alpha_vantage(
    symbol: str,
    *,
    interval: str,
    start: str | None,
    end: str | None,
) -> dict[str, Any]:
    api_key = _load_alpha_vantage_key()
    if not api_key:
        raise ToolError(
            "ALPHA_VANTAGE_API_KEY is not set.",
            hint="Set ALPHA_VANTAGE_API_KEY in environment.",
        )

    # Use intraday if interval < 1d, otherwise daily
    if interval in ("1m", "5m", "15m", "30m", "60m"):
        func = "TIME_SERIES_INTRADAY"
        params: dict[str, Any] = {"symbol": symbol, "interval": interval, "outputsize": "compact"}
    else:
        func = "TIME_SERIES_DAILY"
        params = {"symbol": symbol, "outputsize": "compact"}

    data = _call_alpha_vantage(func, params, api_key)

    if "Note" in data:
        raise ToolError(
            "Alpha Vantage rate limit reached.",
            hint="Alpha Vantage free tier allows 25 requests/day and 5/min. Wait and retry.",
            details=data.get("Note"),
        )

    # Pick the time series key
    series_key = next((k for k in data if k.startswith("Time Series")), None)
    if not series_key:
        raise ToolError(
            "Alpha Vantage returned no time series.",
            details=data,
        )

    records = []
    raw_series = data[series_key]
    for date_str, values in raw_series.items():
        records.append(
            {
                "date": date_str,
                "open": float(values.get("1. open", 0)) or None,
                "high": float(values.get("2. high", 0)) or None,
                "low": float(values.get("3. low", 0)) or None,
                "close": float(values.get("4. close", 0)) or None,
                "volume": int(values.get("5. volume", 0)) or None,
            }
        )
    records.sort(key=lambda r: r["date"])
    return {
        "provider": "alpha_vantage",
        "records": records,
        "count": len(records),
    }


def quote_with_yfinance(yf: Any, symbol: str) -> dict[str, Any]:
    ticker = yf.Ticker(symbol)
    fast_info: dict[str, Any] = {}
    info: dict[str, Any] = {}
    try:
        fast_info = dict(ticker.get_fast_info())
    except Exception:
        try:
            fast_info = dict(ticker.fast_info)
        except Exception:
            fast_info = {}
    try:
        info = ticker.get_info()
    except Exception:
        try:
            info = ticker.info
        except Exception:
            info = {}
    if not isinstance(info, dict):
        info = {}

    summary = {
        "symbol": symbol,
        "currency": info.get("currency") or fast_info.get("currency"),
        "exchange": info.get("exchange"),
        "timezone": info.get("exchangeTimezoneName") or fast_info.get("timezone"),
        "last_price": fast_info.get("lastPrice") or info.get("currentPrice"),
        "previous_close": fast_info.get("previousClose") or info.get("previousClose"),
        "open": fast_info.get("open") or info.get("open"),
        "day_high": fast_info.get("dayHigh") or info.get("dayHigh"),
        "day_low": fast_info.get("dayLow") or info.get("dayLow"),
        "market_cap": fast_info.get("marketCap") or info.get("marketCap"),
        "volume": fast_info.get("lastVolume") or info.get("volume"),
        "short_name": info.get("shortName"),
        "long_name": info.get("longName"),
    }
    return {"provider": "yfinance", "quote": summary}


def history_with_yfinance(
    yf: Any,
    symbol: str,
    *,
    period: str,
    interval: str,
    start: str | None,
    end: str | None,
    auto_adjust: bool,
) -> dict[str, Any]:
    ticker = yf.Ticker(symbol)
    kwargs: dict[str, Any] = {
        "interval": interval,
        "auto_adjust": auto_adjust,
    }
    if start or end:
        kwargs["start"] = start
        kwargs["end"] = end
    else:
        kwargs["period"] = period

    frame = ticker.history(**kwargs)
    records = dataframe_to_records(frame)
    return {
        "provider": "yfinance",
        "records": records,
        "count": len(records),
    }


def quote(symbol: str, yf: Any | None) -> dict[str, Any]:
    # auto path: alpha_vantage → yfinance → chart
    try:
        return quote_with_alpha_vantage(symbol)
    except Exception:
        pass
    if yf:
        try:
            result = quote_with_yfinance(yf, symbol)
            if result.get("quote", {}).get("last_price") is not None:
                return result
        except Exception:
            pass
    return quote_with_chart(symbol)


def history(
    symbol: str,
    yf: Any | None,
    *,
    period: str,
    interval: str,
    start: str | None,
    end: str | None,
    auto_adjust: bool,
) -> dict[str, Any]:
    # auto path: alpha_vantage → yfinance → chart
    try:
        return history_with_alpha_vantage(
            symbol,
            interval=interval,
            start=start,
            end=end,
        )
    except Exception:
        pass
    if yf:
        try:
            return history_with_yfinance(
                yf,
                symbol,
                period=period,
                interval=interval,
                start=start,
                end=end,
                auto_adjust=auto_adjust,
            )
        except Exception:
            pass
    return history_with_chart(
        symbol,
        period=period,
        interval=interval,
        start=start,
        end=end,
    )


def quote_with_provider(symbol: str, yf: Any | None, provider: str) -> dict[str, Any]:
    if provider == "alpha_vantage":
        return quote_with_alpha_vantage(symbol)
    if provider == "chart":
        return quote_with_chart(symbol)
    if provider == "yfinance":
        if not yf:
            raise ToolError(
                "yfinance is not installed.",
                hint="Install yfinance or switch to --provider chart.",
            )
        return quote_with_yfinance(yf, symbol)
    return quote(symbol, yf)


def history_with_provider(
    symbol: str,
    yf: Any | None,
    *,
    provider: str,
    period: str,
    interval: str,
    start: str | None,
    end: str | None,
    auto_adjust: bool,
) -> dict[str, Any]:
    if provider == "alpha_vantage":
        return history_with_alpha_vantage(
            symbol,
            interval=interval,
            start=start,
            end=end,
        )
    if provider == "chart":
        return history_with_chart(
            symbol,
            period=period,
            interval=interval,
            start=start,
            end=end,
        )
    if provider == "yfinance":
        if not yf:
            raise ToolError(
                "yfinance is not installed.",
                hint="Install yfinance or switch to --provider chart.",
            )
        return history_with_yfinance(
            yf,
            symbol,
            period=period,
            interval=interval,
            start=start,
            end=end,
            auto_adjust=auto_adjust,
        )
    return history(
        symbol,
        yf,
        period=period,
        interval=interval,
        start=start,
        end=end,
        auto_adjust=auto_adjust,
    )


def quote_with_chart(symbol: str) -> dict[str, Any]:
    result = fetch_chart(symbol, interval="1d", period="5d", start=None, end=None)
    meta = result.get("meta") or {}
    indicators = ((result.get("indicators") or {}).get("quote") or [{}])[0]
    closes = indicators.get("close") or []
    quote = {
        "symbol": symbol,
        "currency": meta.get("currency"),
        "exchange": meta.get("exchangeName"),
        "timezone": meta.get("exchangeTimezoneName"),
        "last_price": meta.get("regularMarketPrice") or (closes[-1] if closes else None),
        "previous_close": meta.get("previousClose"),
        "open": meta.get("regularMarketOpen"),
        "day_high": meta.get("regularMarketDayHigh"),
        "day_low": meta.get("regularMarketDayLow"),
    }
    return {"provider": "yahoo_chart", "quote": quote}


def history_with_chart(
    symbol: str,
    *,
    period: str,
    interval: str,
    start: str | None,
    end: str | None,
) -> dict[str, Any]:
    result = fetch_chart(symbol, interval=interval, period=period, start=start, end=end)
    timestamps = result.get("timestamp") or []
    indicators = ((result.get("indicators") or {}).get("quote") or [{}])[0]
    records = []
    for index, timestamp in enumerate(timestamps):
        records.append(
            {
                "timestamp": timestamp,
                "open": (indicators.get("open") or [None] * len(timestamps))[index],
                "high": (indicators.get("high") or [None] * len(timestamps))[index],
                "low": (indicators.get("low") or [None] * len(timestamps))[index],
                "close": (indicators.get("close") or [None] * len(timestamps))[index],
                "volume": (indicators.get("volume") or [None] * len(timestamps))[index],
            }
        )
    return {
        "provider": "yahoo_chart",
        "records": records,
        "count": len(records),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch US market data from Yahoo Finance and emit JSON."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    quote = subparsers.add_parser("quote", help="Get quote summary")
    quote.add_argument("--symbol", required=True)
    quote.add_argument("--provider", choices=("auto", "yfinance", "chart", "alpha_vantage"), default="auto")

    history = subparsers.add_parser("history", help="Get historical candles")
    history.add_argument("--symbol", required=True)
    history.add_argument("--period", default="6mo")
    history.add_argument("--interval", default="1d")
    history.add_argument("--start")
    history.add_argument("--end")
    history.add_argument("--no-auto-adjust", action="store_true")
    history.add_argument("--provider", choices=("auto", "yfinance", "chart", "alpha_vantage"), default="auto")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    request = vars(args).copy()
    action = args.command
    symbol = normalize_symbol(args.symbol)
    request["symbol"] = symbol

    yf = maybe_load_yfinance()

    try:
        if action == "quote":
            data = quote_with_provider(symbol, yf, args.provider)
        elif action == "history":
            data = history_with_provider(
                symbol,
                yf,
                provider=args.provider,
                period=args.period,
                interval=args.interval,
                start=args.start,
                end=args.end,
                auto_adjust=not args.no_auto_adjust,
            )
        else:
            raise ToolError(f"Unsupported command: {action}")
        return emit(
            ok_payload(
                source="yahoo_finance",
                market="US",
                action=action,
                request=request,
                data=data,
                meta={"provider_preference": "alpha_vantage_then_yfinance_then_yahoo_chart"},
            )
        )
    except ToolError as exc:
        return emit(
            error_payload(
                source="yahoo_finance",
                market="US",
                action=action,
                message=exc.message,
                request=request,
                hint=exc.hint,
                details=exc.details,
            ),
            exit_code=1,
        )


if __name__ == "__main__":
    raise SystemExit(main())
