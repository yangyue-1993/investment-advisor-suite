#!/usr/bin/env python3

import argparse
import os
from typing import Any

import requests

from common import ToolError, emit, error_payload, ok_payload, parse_json_arg


TUSHARE_URL = "http://api.tushare.pro"
DEFAULT_TIMEOUT = 30


def build_rows(fields: list[str], items: list[list[Any]]) -> list[dict[str, Any]]:
    return [dict(zip(fields, item)) for item in items]


def call_tushare(api_name: str, params: dict[str, Any], fields: str | None) -> dict[str, Any]:
    token = os.environ.get("TUSHARE_TOKEN")
    if not token:
        raise ToolError(
            "TUSHARE_TOKEN is not set.",
            hint="Export TUSHARE_TOKEN before running the A-share tool.",
        )

    payload = {
        "api_name": api_name,
        "token": token,
        "params": params,
        "fields": fields or "",
    }

    try:
        response = requests.post(TUSHARE_URL, json=payload, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ToolError(
            "Failed to reach Tushare Pro.",
            hint="Check network connectivity and your Tushare endpoint access.",
            details=str(exc),
        ) from exc

    try:
        body = response.json()
    except ValueError as exc:
        raise ToolError(
            "Tushare returned a non-JSON response.",
            details=response.text[:500],
        ) from exc

    code = body.get("code")
    if code not in (0, None):
        raise ToolError(
            "Tushare returned an application error.",
            hint="Check token permissions and api_name/params/fields values.",
            details={"code": code, "msg": body.get("msg")},
        )

    data = body.get("data") or {}
    fields_list = data.get("fields") or []
    items = data.get("items") or []
    rows = build_rows(fields_list, items) if fields_list else items
    return {
        "fields": fields_list,
        "items": items,
        "rows": rows,
        "count": len(rows),
        "raw": body,
    }


def handle_query(args: argparse.Namespace) -> dict[str, Any]:
    params = parse_json_arg(args.params, default={})
    if not isinstance(params, dict):
        raise ToolError("--params must be a JSON object.")
    return call_tushare(args.api_name, params, args.fields)


def handle_daily(args: argparse.Namespace) -> dict[str, Any]:
    params = {
        "ts_code": args.ts_code,
        "start_date": args.start_date,
        "end_date": args.end_date,
    }
    params = {key: value for key, value in params.items() if value}
    return call_tushare("daily", params, args.fields)


def handle_daily_basic(args: argparse.Namespace) -> dict[str, Any]:
    params = {
        "ts_code": args.ts_code,
        "trade_date": args.trade_date,
        "start_date": args.start_date,
        "end_date": args.end_date,
    }
    params = {key: value for key, value in params.items() if value}
    return call_tushare("daily_basic", params, args.fields)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch A-share data from Tushare Pro and emit JSON."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    query = subparsers.add_parser("query", help="Call any Tushare Pro api_name")
    query.add_argument("--api-name", required=True)
    query.add_argument("--params", help="JSON object for Tushare params")
    query.add_argument("--fields", help="Comma-separated fields")

    daily = subparsers.add_parser("daily", help="Fetch A-share daily bars")
    daily.add_argument("--ts-code", required=True)
    daily.add_argument("--start-date")
    daily.add_argument("--end-date")
    daily.add_argument(
        "--fields",
        default="ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount",
    )

    daily_basic = subparsers.add_parser("daily-basic", help="Fetch A-share daily_basic data")
    daily_basic.add_argument("--ts-code")
    daily_basic.add_argument("--trade-date")
    daily_basic.add_argument("--start-date")
    daily_basic.add_argument("--end-date")
    daily_basic.add_argument(
        "--fields",
        default="ts_code,trade_date,close,turnover_rate,volume_ratio,pe,pb,total_mv,circ_mv",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    request = vars(args).copy()
    action = args.command

    try:
        if action == "query":
            data = handle_query(args)
        elif action == "daily":
            data = handle_daily(args)
        elif action == "daily-basic":
            data = handle_daily_basic(args)
        else:
            raise ToolError(f"Unsupported command: {action}")
        return emit(
            ok_payload(
                source="tushare_pro",
                market="CN",
                action=action,
                request=request,
                data=data,
            )
        )
    except ToolError as exc:
        return emit(
            error_payload(
                source="tushare_pro",
                market="CN",
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
