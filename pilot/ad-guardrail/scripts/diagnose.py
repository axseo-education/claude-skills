"""항목별 진단 및 사람이 확정하기 전의 목표 제안."""
import argparse
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from statistics import median

from observe import account_observation, ad_observation
from runtime import emit, entry, read_json, utcnow

ALL = ["L0", "L1", "L2", "L3", "L4", "L5"]
ZERO = ["L1", "L2", "L3", "L5"]


def diagnose(snapshot: dict, now, breakeven: float | None, permission: str = "unknown") -> dict:
    obs = account_observation(snapshot, now)
    ads, daily = snapshot["ads"], snapshot["daily"]
    items = {}

    def item(name, status, blocks, value=None):
        items[name] = {"status": status, "blocks": blocks if status != "pass" else [], "value": value}

    item("permission", permission, ALL)
    item("account", "pass" if snapshot["account"].get("account_status") == 1 else "fail", ALL)
    item("currency", "pass" if snapshot["account"].get("currency") == "KRW" else "fail", ALL)
    item("complete", "pass" if snapshot.get("complete") is True else "fail", ALL)
    item("pixel", "pass" if obs["pixel_alive"] else "fail", ZERO)
    item("reconciliation", "pass" if obs["reconciled"] else "fail", ZERO, obs)
    mismatch = sum(ad_observation(ad, {"state": "valid"}) == "contested" for ad in ads)
    item("aliases", "fail" if mismatch else "pass", ZERO, mismatch)
    attribution = sorted({w["attribution"] for ad in ads for w in ad["windows"].values()})
    item("attribution", "unknown" if "unknown" in attribution else "pass", [],
         {"types": attribution, "warning": len(attribution) > 1})
    item("structure", "pass", [], {"campaigns": len({a["campaign"]["id"] for a in ads}),
         "adsets": len({a["adset_id"] for a in ads}), "ads": len(ads)})
    ratios = {"cpa": ("spend", "purchase", 1), "ctr": ("clicks", "impressions", 1),
              "cpm": ("spend", "impressions", 1000), "lpv_cost": ("spend", "lpv", 1),
              "aov": ("revenue", "purchase", 1), "roas": ("revenue", "spend", 1)}
    baseline = {}
    for name, (numerator, denominator, factor) in ratios.items():
        values = [r[numerator] / r[denominator] * factor for r in daily if r[denominator] > 0]
        baseline[name] = median(values) if values else None
        item("baseline_" + name, "pass" if values else "unknown", ["L1"] if name == "ctr" else [], baseline[name])
    purchases = sum(r["purchase"] for r in daily)
    days = len({r["date"] for r in daily if r["purchase"] > 0})
    suggestion = None
    if purchases >= 20 and days >= 7 and breakeven is not None and breakeven > 0:
        raw = min(breakeven, sum(r["spend"] for r in daily) / purchases * 1.2)
        suggestion = int((Decimal(str(raw)) / 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * 1000)
    item("target_proposal", "pass" if suggestion is not None else "unknown", ALL,
         {"target_cpa": suggestion, "purchases": purchases, "purchase_days": days, "requires_confirmation": True})
    item("breakeven", "pass" if breakeven is not None and breakeven > 0 else "unknown", ALL)
    return {"items": items, "baseline": baseline, "target_cpa_proposal": suggestion,
            "blocked_layers": sorted({layer for value in items.values() for layer in value["blocks"]})}


def main() -> None:
    from graph import Graph, GraphError
    from preflight import authorize
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--breakeven", type=float)
    args = parser.parse_args()
    permission = "unknown"
    try:
        permission = "pass" if authorize(Graph()) else "fail"
    except GraphError:
        raise
    except Exception:
        pass
    emit(diagnose(read_json(args.snapshot), utcnow(), args.breakeven, permission))


if __name__ == "__main__":
    entry(main)
