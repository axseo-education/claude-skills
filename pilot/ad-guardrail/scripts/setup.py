"""실행기 탐지 및 권한 규칙의 멱등 병합. dry-run은 파일을 쓰지 않는다."""
import argparse
import shutil
import subprocess
import uuid
from pathlib import Path

from runtime import emit, entry, read_json, state, utcnow, write_json

RUNNERS = [["py", "-3"], ["python3"], ["python"], ["uv", "run", "--python", "3.12", "--no-project"]]


def detect(which=shutil.which, execute=subprocess.run) -> list:
    for runner in RUNNERS:
        executable = which(runner[0])
        if not executable:
            continue
        command = [executable, *runner[1:]]
        probe = command + (["--offline", "--no-python-downloads", "python"] if runner[0] == "uv" else [])
        try:
            result = execute(probe + ["-c", "import sys; print('%d.%d' % sys.version_info[:2])"],
                             shell=False, capture_output=True, text=True, encoding="utf-8", timeout=30)
            version = tuple(int(part) for part in result.stdout.strip().split("."))
            if result.returncode == 0 and len(version) == 2 and version >= (3, 10):
                return command
        except (OSError, ValueError, subprocess.SubprocessError):
            continue
    raise ValueError("python_310_required")


def merge(existing: dict, rules: dict) -> dict:
    import copy
    result = copy.deepcopy(existing)
    permissions = result.setdefault("permissions", {})
    if not isinstance(permissions, dict):
        raise ValueError("invalid_permissions")
    for key in ("ask", "deny"):
        current = permissions.setdefault(key, [])
        if not isinstance(current, list) or any(not isinstance(rule, str) for rule in current):
            raise ValueError("invalid_permission_rules")
        for rule in rules["permissions"][key]:
            if rule not in current:
                current.append(rule)
    return result


def setup(home: Path, dry_run: bool, detector=detect) -> dict:
    settings = home / ".claude" / "settings.json"
    existing = read_json(settings) if settings.exists() else {}
    rules = read_json(Path(__file__).resolve().parents[1] / "install" / "permissions.json")
    combined = merge(existing, rules)
    runner = detector()
    runtime = {"runner": runner, "minimum_python": "3.10"}
    backup = None
    changed = combined != existing
    if not dry_run:
        if changed and settings.exists():
            suffix = utcnow().strftime("%Y-%m-%dT%H-%M-%S") + "_" + uuid.uuid4().hex[:4]
            backup = settings.with_name("settings.json.backup-" + suffix)
            shutil.copy2(settings, backup)
        if changed:
            write_json(settings, combined)
        write_json(state(home) / "runtime.json", runtime)
    return {"status": "ok", "dry_run": dry_run, "runner": runner, "permissions_changed": changed,
            "backup": str(backup) if backup else None, "home": str(home)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    emit(setup(args.home, args.dry_run))


if __name__ == "__main__":
    entry(main)
