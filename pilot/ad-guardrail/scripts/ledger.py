"""별도 잠금 파일로 원장 읽기, 예약, append를 직렬화한다."""
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path

from runtime import DAY_LIMIT, RUN_LIMIT


@contextmanager
def locked(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    # ponytail: 시범 1명·계정 일 20회, 원장 읽기가 10초에 접근하면 계정별 분할 검토.
    path = root / "ledger.lock"
    deadline = time.monotonic() + 10
    while True:
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            break
        except FileExistsError:
            try:
                stale = time.time() - path.stat().st_mtime > 60
            except FileNotFoundError:
                continue
            # 오래된 파일도 살아 있는 소유자의 잠금일 수 있어 자동 탈취하지 않는다.
            if stale:
                raise RuntimeError("ledger_stale_lock_check_owner") from None
            if time.monotonic() >= deadline:
                raise RuntimeError("ledger_lock_timeout") from None
            time.sleep(0.01)
    try:
        os.close(descriptor)
        yield
    finally:
        path.unlink()


def read_unlocked(root: Path) -> list:
    path = root / "log.jsonl"
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as stream:
        rows = [json.loads(line) for line in stream if line.strip()]
    if any(not isinstance(row, dict) or "event" not in row for row in rows):
        raise ValueError("ledger_corrupt")
    return rows


def append_unlocked(root: Path, event: dict) -> None:
    line = json.dumps(event, ensure_ascii=False, allow_nan=False)
    with (root / "log.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(line + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def append(root: Path, event: dict) -> None:
    with locked(root):
        read_unlocked(root)
        append_unlocked(root, event)


def read(root: Path) -> list:
    with locked(root):
        return read_unlocked(root)


def reserve(root: Path, run: str, account: str, ad: str, day: str, config: dict, at: str) -> str | None:
    with locked(root):
        if (root / "STOP").exists():
            return "emergency_stop"
        attempts = [row for row in read_unlocked(root) if row["event"] == "attempt"]
        if any(row["run_id"] == run and row["ad_id"] == ad for row in attempts):
            return "already_attempted"
        run_limit = min(RUN_LIMIT, max(0, int(config.get("run_limit", RUN_LIMIT))))
        day_limit = min(DAY_LIMIT, max(0, int(config.get("day_limit", DAY_LIMIT))))
        if sum(row["run_id"] == run for row in attempts) >= run_limit:
            return "run_limit"
        if sum(row["account_id"] == account and row["day"] == day for row in attempts) >= day_limit:
            return "day_limit"
        append_unlocked(root, {"event": "attempt", "run_id": run, "account_id": account,
                               "ad_id": ad, "day": day, "at": at})
    return None
