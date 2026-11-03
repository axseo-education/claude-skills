"""한 호출, 한 광고. 하네스 승인 이후에도 재판정과 원장 상한을 강제한다."""
import argparse
import subprocess

from collect import collect
from graph import Graph, GraphError
from judge import judge
from ledger import append, reserve
from preflight import authorize, meta_path
from runtime import MAX_AGE_SECONDS, account_timezone, emit, entry, error_output, identifier, instant, read_json, state, utcnow
from settings import load


def pause(root, run_id: str, ad_id: str, graph, cli: str, clock=utcnow,
          collector=collect, executor=subprocess.run) -> dict:
    identifier(run_id)
    identifier(ad_id)
    account = None

    def finish(status, reason, error=None):
        result = {"event": "execution", "run_id": run_id, "ad_id": ad_id, "account_id": account,
                  "at": clock().isoformat(), "status": status, "reason": reason}
        if error is not None:
            result["error"] = error_output(error)
        append(root, result)
        return result

    try:
        if (root / "STOP").exists():
            return finish("rejected", "emergency_stop")
        run = read_json(root / "runs" / (run_id + ".json"))
        account = identifier(run["account_id"])
        now = clock()
        if not 0 <= (now - instant(run["created_at"])).total_seconds() <= MAX_AGE_SECONDS:
            return finish("rejected", "stale_run")
        candidates = run["result"]["decisions"]
        if not any(r["ad_id"] == ad_id and r["decision"] == "off_recommend" for r in candidates):
            return finish("rejected", "not_recommended")
        if not authorize(graph):
            return finish("rejected", "permission")
        config = load(root, account)
        if config != run["settings"]:
            return finish("rejected", "settings_changed")
        day = now.astimezone(account_timezone(run)).date().isoformat()
        rejection = reserve(root, run_id, account, ad_id, day, config, now.isoformat())
        if rejection:
            return finish("rejected", rejection)
        fresh = collector(graph, account, clock())
        if fresh["account_id"] != account or account_timezone(fresh["account"]) != account_timezone(run):
            return finish("rejected", "account_context_changed")
        # 공통 수집의 3조회 조인 결과로 ACTIVE 및 전환 캠페인을 재확인한다.
        meta = next((ad for ad in fresh["ads"] if ad["id"] == ad_id), {})
        if meta.get("status") != "ACTIVE" or meta.get("effective_status") != "ACTIVE" or meta.get("campaign", {}).get("objective") != "OUTCOME_SALES":
            return finish("rejected", "ad_not_active_sales")
        decision = judge(fresh, config, clock())
        if not any(r["ad_id"] == ad_id and r["decision"] == "off_recommend" for r in decision["decisions"]):
            return finish("rejected", "recheck")
        final_now = clock()
        if (root / "STOP").exists():
            return finish("rejected", "emergency_stop")
        if not 0 <= (final_now - instant(run["created_at"])).total_seconds() <= MAX_AGE_SECONDS:
            return finish("rejected", "stale_run")
        if final_now.astimezone(account_timezone(run)).date().isoformat() != day:
            return finish("rejected", "day_changed_retry_new_run")
        if load(root, account) != config:
            return finish("rejected", "settings_changed")
        if not cli:
            return finish("rejected", "meta_cli_missing")
        process = executor([cli, "ads", "ad", "update", ad_id, "--status", "PAUSED"],
                           shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
        if process.returncode != 0:
            return finish("failed", "cli_failed")
        try:
            status = graph.get("/" + ad_id, {"fields": "status,effective_status"})
        except GraphError as error:
            return finish("not_verified", "status_lookup_failed", error)
        except Exception:
            return finish("not_verified", "status_lookup_failed")
        if status.get("status") == "PAUSED":
            return finish("success", "status_paused")
        return finish("not_verified", "status_not_paused")
    except GraphError as error:
        return finish("failed", error_output(error)["reason"], error)
    except Exception:
        return finish("failed", "operation_failed")


def main() -> None:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--run", required=True, type=identifier, action="append")
    parser.add_argument("--ad", required=True, type=identifier, action="append")
    args = parser.parse_args()
    if len(args.run) != 1 or len(args.ad) != 1:
        parser.error("exactly one --run and one --ad required")
    result = pause(state(), args.run[0], args.ad[0], Graph(), meta_path())
    emit(result.get("error", result))
    if result["status"] != "success":
        raise SystemExit(1)


if __name__ == "__main__":
    entry(main)
