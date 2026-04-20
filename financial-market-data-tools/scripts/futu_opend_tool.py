#!/usr/bin/env python3

import argparse
import os
from typing import Any

from common import ToolError, dataframe_to_records, emit, error_payload, ok_payload


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 11111


def normalize_code(code: str) -> str:
    raw = code.strip().upper()
    if raw.startswith("HK."):
        return raw
    if raw.endswith(".HK"):
        numeric = raw[:-3]
        return f"HK.{numeric.zfill(5)}"
    if raw.isdigit():
        return f"HK.{raw.zfill(5)}"
    return raw


def load_sdk() -> Any:
    try:
        import futu  # type: ignore
    except ImportError as exc:
        raise ToolError(
            "The futu SDK is not installed.",
            hint="Install it with `pip install futu-api` and make sure OpenD is running.",
        ) from exc
    return futu


def open_quote_context(futu_module: Any, host: str, port: int) -> Any:
    try:
        return futu_module.OpenQuoteContext(host=host, port=port)
    except Exception as exc:
        raise ToolError(
            "Failed to connect to OpenD.",
            hint="Check FUTU_HOST/FUTU_PORT and ensure OpenD is running.",
            details=str(exc),
        ) from exc


def snapshot(args: argparse.Namespace) -> dict[str, Any]:
    futu = load_sdk()
    codes = [normalize_code(code) for code in args.code]
    ctx = open_quote_context(futu, args.host, args.port)
    try:
        ret, data = ctx.get_market_snapshot(codes)
        if ret != futu.RET_OK:
            raise ToolError(
                "Futu get_market_snapshot failed.",
                details=str(data),
            )
        return {
            "records": dataframe_to_records(data),
            "count": len(data.index),
        }
    finally:
        ctx.close()


def history_kline(args: argparse.Namespace) -> dict[str, Any]:
    futu = load_sdk()
    code = normalize_code(args.code)
    ctx = open_quote_context(futu, args.host, args.port)
    records: list[dict[str, Any]] = []
    page_req_key = None
    pages = 0
    try:
        while True:
            ret, data, page_req_key = ctx.request_history_kline(
                code,
                start=args.start,
                end=args.end,
                ktype=getattr(futu.KLType, args.ktype),
                autype=getattr(futu.AuType, args.autype),
                max_count=args.max_count,
                page_req_key=page_req_key,
                extended_time=args.extended_time,
            )
            if ret != futu.RET_OK:
                raise ToolError(
                    "Futu request_history_kline failed.",
                    details=str(data),
                )
            records.extend(dataframe_to_records(data))
            pages += 1
            if page_req_key is None or pages >= args.max_pages:
                break
        return {
            "records": records,
            "count": len(records),
            "pages_fetched": pages,
            "normalized_code": code,
        }
    finally:
        ctx.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch Hong Kong market data from Futu OpenD and emit JSON."
    )
    parser.add_argument("--host", default=os.environ.get("FUTU_HOST", DEFAULT_HOST))
    parser.add_argument("--port", type=int, default=int(os.environ.get("FUTU_PORT", DEFAULT_PORT)))

    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot_parser = subparsers.add_parser("snapshot", help="Get market snapshots")
    snapshot_parser.add_argument("--code", action="append", required=True)

    history_parser = subparsers.add_parser("history-kline", help="Get historical candlesticks")
    history_parser.add_argument("--code", required=True)
    history_parser.add_argument("--start")
    history_parser.add_argument("--end")
    history_parser.add_argument("--ktype", default="K_DAY")
    history_parser.add_argument("--autype", default="QFQ")
    history_parser.add_argument("--max-count", type=int, default=1000)
    history_parser.add_argument("--max-pages", type=int, default=20)
    history_parser.add_argument("--extended-time", action="store_true")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    request = vars(args).copy()
    action = args.command

    try:
        if action == "snapshot":
            data = snapshot(args)
        elif action == "history-kline":
            data = history_kline(args)
        else:
            raise ToolError(f"Unsupported command: {action}")
        return emit(
            ok_payload(
                source="futu_opend",
                market="HK",
                action=action,
                request=request,
                data=data,
                meta={"host": args.host, "port": args.port},
            )
        )
    except ToolError as exc:
        return emit(
            error_payload(
                source="futu_opend",
                market="HK",
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
