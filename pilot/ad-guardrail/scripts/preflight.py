"""자격 확인과 토큰으로 보이는 계정 선택."""
import argparse
import os
import shutil
from pathlib import Path

from graph import Graph, GraphError
from runtime import emit, entry, state


def meta_path() -> str | None:
    return shutil.which("meta.exe" if os.name == "nt" else "meta")


def authorize(graph: Graph) -> bool:
    graph.get("/me", {"fields": "id"})
    return any(row.get("permission") == "ads_management" and row.get("status") == "granted"
               for row in graph.pages("/me/permissions", {"limit": 500}))


def check(graph: Graph, root: Path, cli: str | None) -> dict:
    checks = {"token_identity_permission": "fail", "meta_cli": "pass" if cli else "fail",
              "emergency_stop": "fail" if (root / "STOP").exists() else "pass"}
    try:
        checks["token_identity_permission"] = "pass" if authorize(graph) else "fail"
    except GraphError:
        raise
    except Exception:
        pass
    return {"status": "pass" if all(v == "pass" for v in checks.values()) else "fail",
            "checks": checks}


def accounts(graph: Graph) -> list:
    return [row for row in graph.pages("/me/adaccounts", {"fields": "id,name,currency,account_status", "limit": 500})
            if row.get("currency") == "KRW"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accounts", action="store_true")
    args = parser.parse_args()
    graph = Graph()
    result = check(graph, state(), meta_path())
    if args.accounts and result["status"] == "pass":
        result["accounts"] = accounts(graph)
    emit(result)
    if result["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    entry(main)
