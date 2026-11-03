"""전 페이지 성공 시에만 ACTIVE 전환 광고의 완전한 스냅샷을 반환한다."""
import argparse
import json
import math
import queue
import threading
import time

from graph import Graph
from runtime import CollectDeadline, account_timezone, emit, entry, identifier, state, utcnow, write_json

WINDOWS = ("maximum", "last_7d", "yesterday", "today")
FILTER = json.dumps([{"field": "campaign.objective", "operator": "IN", "value": ["OUTCOME_SALES"]}])
ACTIVE_FILTER = json.dumps(json.loads(FILTER) + [
    {"field": "ad.effective_status", "operator": "IN", "value": ["ACTIVE"]}])
COLLECT_SECONDS = 120
FIELDS = "spend,impressions,inline_link_clicks,actions,action_values,frequency,attribution_setting"


def number(value) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError("invalid_metric")
    return result


def normalize(row: dict) -> dict:
    actions = {a["action_type"]: number(a["value"]) for a in row.get("actions", [])}
    values = {a["action_type"]: number(a["value"]) for a in row.get("action_values", [])}
    alias, pixel = actions.get("purchase"), actions.get("offsite_conversion.fb_pixel_purchase")
    return {"spend": number(row.get("spend", 0)), "impressions": number(row.get("impressions", 0)),
            "clicks": number(row.get("inline_link_clicks", 0)),
            "purchase": pixel if pixel is not None else (alias or 0),
            "ic": actions.get("offsite_conversion.fb_pixel_initiate_checkout", actions.get("initiate_checkout", 0)),
            "lpv": actions.get("landing_page_view", 0),
            "revenue": values.get("offsite_conversion.fb_pixel_purchase", values.get("purchase", 0)),
            "alias_mismatch": alias is not None and pixel is not None and alias != pixel,
            "attribution": row.get("attribution_setting", "unknown"),
            "frequency": number(row.get("frequency", 0))}


def collect(graph: Graph, account: str, now) -> dict:
    deadline = time.monotonic() + COLLECT_SECONDS
    result = queue.Queue(maxsize=1)

    def worker():
        graph.deadline = deadline
        try:
            result.put((True, collect_data(graph, account, now)))
        except Exception as error:
            result.put((False, error))

    # Worker는 파일을 쓰지 않는다. 시한 뒤 결과는 폐기한다.
    threading.Thread(target=worker, daemon=True).start()
    try:
        ok, value = result.get(timeout=max(0, deadline - time.monotonic()))
    except queue.Empty:
        raise CollectDeadline() from None
    graph.deadline = None
    if time.monotonic() >= deadline:
        raise CollectDeadline()
    if not ok:
        raise value
    return value


def collect_ads(graph: Graph, account: str) -> tuple[list, bool]:
    filtering = json.dumps([{"field": "effective_status", "operator": "IN", "value": ["ACTIVE"]}])
    def rows(edge: str, fields: str) -> list:
        return graph.pages(f"/{account}/{edge}", {"limit": 500, "fields": fields, "filtering": filtering})

    ads = rows("ads", "id,name,status,effective_status,created_time,adset_id,campaign_id")
    adsets = {row["id"]: row for row in rows("adsets", "id,name,start_time")}
    campaigns = {row["id"]: row for row in rows("campaigns", "id,name,objective")}
    selected, complete = [], True
    for ad in ads:
        if ad.get("effective_status") != "ACTIVE":
            continue
        campaign = campaigns.get(ad.get("campaign_id"), {"id": ad.get("campaign_id")})
        if not campaign.get("objective"):
            complete = False
        elif campaign["objective"] != "OUTCOME_SALES":
            continue
        adset = adsets.get(ad.get("adset_id"), {"id": ad.get("adset_id")})
        selected.append({**ad, "adset": {k: adset[k] for k in ("id", "start_time") if k in adset},
                         "campaign": {k: campaign[k] for k in ("id", "name", "objective") if k in campaign}})
    return selected, complete


def collect_data(graph: Graph, account: str, now) -> dict:
    identifier(account)
    info = graph.get("/" + account, {"fields": "name,currency,account_status,timezone_name,timezone_offset_hours_utc"})
    if info.get("currency") != "KRW":
        raise ValueError("currency_not_krw")
    account_timezone(info)
    ads, complete = collect_ads(graph, account)
    if len({ad["id"] for ad in ads}) != len(ads):
        raise ValueError("duplicate_ad")
    windows = {}
    for window in WINDOWS:
        rows = graph.pages("/" + account + "/insights", {
            "level": "ad", "date_preset": window, "limit": 500,
            "fields": "ad_id," + FIELDS, "filtering": ACTIVE_FILTER})
        if len({row["ad_id"] for row in rows}) != len(rows):
            raise ValueError("duplicate_insight")
        windows[window] = {row["ad_id"]: normalize(row) for row in rows}
    reconciliation = graph.pages("/" + account + "/insights", {
        "level": "ad", "date_preset": "last_7d", "limit": 500,
        "fields": "ad_id," + FIELDS, "filtering": FILTER})
    totals = graph.pages("/" + account + "/insights", {
        "level": "account", "limit": 500, "date_preset": "last_7d", "fields": FIELDS, "filtering": FILTER})
    daily = graph.pages("/" + account + "/insights", {
        "level": "account", "limit": 500, "date_preset": "last_14d", "time_increment": 1,
        "fields": FIELDS, "filtering": FILTER})
    pixels = graph.pages("/" + account + "/adspixels", {"fields": "id,last_fired_time", "limit": 500})
    for ad in ads:
        ad["windows"] = {window: windows[window].get(ad["id"], normalize({})) for window in WINDOWS}
    return {"complete": complete, "collected_at": now.isoformat(), "account_id": account,
            "account": info, "ads": ads, "active_sales_count": len(ads), "pixels": pixels,
            "reconciliation": {"ad_purchase": sum(normalize(r)["purchase"] for r in reconciliation),
                               "account_purchase": sum(normalize(r)["purchase"] for r in totals)},
            "daily": [{"date": r["date_start"], **normalize(r)} for r in daily]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--account", required=True)
    parser.add_argument("--judge", action="store_true")
    args = parser.parse_args()
    snapshot = collect(Graph(), args.account, utcnow())
    path = state() / "snapshots" / (identifier(args.account) + ".json")
    write_json(path, snapshot)
    if args.judge:
        from judge import judge
        from ledger import append
        from runtime import run_id
        from sample import select
        from settings import load
        now = utcnow()
        config = load(state(), args.account)
        result = judge(snapshot, config, now)
        rid = run_id(now)
        run = {"run_id": rid, "created_at": now.isoformat(), "account_id": args.account,
               "timezone": snapshot["account"].get("timezone_name"),
               "timezone_offset_hours_utc": snapshot["account"]["timezone_offset_hours_utc"], "settings": config,
               "result": result, "samples": select(result, rid)}
        write_json(state() / "runs" / (rid + ".json"), run)
        append(state(), {"event": "run", **run,
                         "day": now.astimezone(account_timezone(run)).date().isoformat()})
        for row in result["decisions"]:
            if row["decision"] == "off_recommend":
                append(state(), {"event": "execution", "run_id": rid, "ad_id": row["ad_id"],
                                 "status": "not_attempted", "reason": "awaiting_human", "at": now.isoformat()})
        emit(run)
        return
    emit({"snapshot": str(path), "complete": snapshot["complete"], "count": len(snapshot["ads"])})


if __name__ == "__main__":
    entry(main)
