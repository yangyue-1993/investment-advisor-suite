#!/usr/bin/env python3

import json
import sys
from datetime import datetime, timezone
from typing import Any


class ToolError(Exception):
    def __init__(self, message: str, *, hint: str | None = None, details: Any = None):
        super().__init__(message)
        self.message = message
        self.hint = hint
        self.details = details


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def emit(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    sys.stdout.write("\n")
    return exit_code


def ok_payload(
    *,
    source: str,
    market: str,
    action: str,
    request: dict[str, Any],
    data: Any,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "ok": True,
        "source": source,
        "market": market,
        "action": action,
        "as_of": utc_now_iso(),
        "request": request,
        "meta": meta or {},
        "data": data,
    }


def error_payload(
    *,
    source: str,
    market: str,
    action: str,
    message: str,
    request: dict[str, Any] | None = None,
    hint: str | None = None,
    details: Any = None,
) -> dict[str, Any]:
    return {
        "ok": False,
        "source": source,
        "market": market,
        "action": action,
        "as_of": utc_now_iso(),
        "request": request or {},
        "error": {
            "message": message,
            "hint": hint,
            "details": details,
        },
    }


def parse_json_arg(raw: str | None, *, default: Any) -> Any:
    if raw is None:
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ToolError(
            f"Invalid JSON argument: {exc}",
            hint="Pass a valid JSON object or array.",
            details={"raw": raw},
        ) from exc


def split_csv(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def dataframe_to_records(frame: Any) -> list[dict[str, Any]]:
    if hasattr(frame, "reset_index"):
        frame = frame.reset_index()
    if hasattr(frame, "to_dict"):
        return frame.to_dict(orient="records")
    raise ToolError("Object does not support DataFrame conversion.")
