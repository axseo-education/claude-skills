"""로컬 경로, 실행 규약과 변경할 수 없는 안전 상수."""
import json
import math
import os
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

GRAPH_VERSION = "v22.0"
RUN_LIMIT = 10
DAY_LIMIT = 20
MATURE_HOUR = 12
MAX_AGE_SECONDS = 3600
ERROR_MESSAGES = {
    "rate_limited": "메타 호출 한도에 걸렸습니다. {wait} 다시 실행하세요",
    "graph_error": "메타 조회에 실패했습니다. 오류 코드를 관리자에게 전달하세요",
    "collect_deadline": "수집 제한 시간을 넘었습니다. 잠시 후 다시 실행하세요",
    "operation_failed_check_local_inputs": "로컬 입력과 설정 파일을 확인하세요",
    "operation_failed": "작업에 실패했습니다. 관리자에게 확인하세요",
}


class GraphError(RuntimeError):
    def __init__(self, reason: str = "graph_error", code: int | None = None):
        super().__init__("graph_error")
        self.code = code if type(code) is int else None


class GraphRateLimited(GraphError):
    def __init__(self, retry_after_minutes: int | float | None = None, code: int | None = None):
        super().__init__(code=code)
        self.retry_after_minutes = retry_after_minutes


def error_output(error: Exception) -> dict:
    extra = {}
    if isinstance(error, GraphRateLimited):
        reason = "rate_limited"
        minutes = error.retry_after_minutes
        extra["retry_after_minutes"] = minutes
        wait = f"{minutes}분 뒤" if minutes is not None else "잠시 후"
    elif isinstance(error, GraphError):
        reason = "graph_error"
        if error.code is not None:
            extra["code"] = error.code
    elif isinstance(error, CollectDeadline):
        reason = "collect_deadline"
    elif isinstance(error, (ValueError, TypeError, KeyError, OSError)):
        reason = "operation_failed_check_local_inputs"
    else:
        reason = "operation_failed"
    message = ERROR_MESSAGES[reason]
    if reason == "rate_limited":
        message = message.format(wait=wait)
    return {"status": "error", "reason": reason, **extra, "message": message}


class CollectDeadline(RuntimeError):
    def __init__(self):
        super().__init__("collect_deadline")


def account_timezone(account: dict) -> timezone:
    value = account.get("timezone_offset_hours_utc")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("timezone_offset_invalid")
    if not math.isfinite(value) or not -24 < value < 24:
        raise ValueError("timezone_offset_invalid")
    return timezone(timedelta(hours=value))


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def instant(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("timezone_required")
    return result


def identifier(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", value):
        raise ValueError("invalid_identifier")
    return value


def state(home: Path | None = None) -> Path:
    return (Path(home) if home is not None else Path.home()) / ".ad-guardrail"


def read_json(path: Path) -> dict:
    def reject_constant(value):
        raise ValueError("invalid_json_constant")
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream, parse_constant=reject_constant)
    if not isinstance(value, dict):
        raise ValueError("json_object_required")
    return value


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex[:8] + ".tmp")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def emit(value: dict) -> None:
    print(json.dumps(value, ensure_ascii=False, allow_nan=False))


def entry(main) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        main()
    except Exception as error:
        # 외부 예외 문자열에는 URL, 응답 본문 또는 토큰이 섞일 수 있다.
        emit(error_output(error))
        raise SystemExit(1) from None


def run_id(now: datetime) -> str:
    return now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ") + "_" + uuid.uuid4().hex[:4]
