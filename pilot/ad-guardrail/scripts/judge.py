"""순수 판정: 네트워크, 파일, 현재 시각 접근 없이 입력만 평가한다."""
from datetime import timedelta
from statistics import median

from observe import account_observation, ad_observation
from runtime import MATURE_HOUR, MAX_AGE_SECONDS, account_timezone, instant
from settings import validate

PRIORITY = ("L3", "L4", "L2", "L5", "L1", "L0")


def gate(snapshot: dict, config: dict, now) -> list:
    errors = []
    if snapshot.get("complete") is not True:
        errors.append("incomplete")
    try:
        age = (now - instant(snapshot["collected_at"])).total_seconds()
        if not 0 <= age <= MAX_AGE_SECONDS:
            errors.append("stale")
        account_timezone(snapshot["account"])
    except (KeyError, ValueError, TypeError):
        errors.append("time_invalid")
    if snapshot.get("account", {}).get("currency") != "KRW":
        errors.append("currency")
    if snapshot.get("account", {}).get("account_status") != 1:
        errors.append("account_inactive")
    try:
        validate(config)
    except (ValueError, TypeError):
        errors.append("targets_unconfirmed")
    ads = snapshot.get("ads", [])
    if snapshot.get("active_sales_count") != len(ads) or len({a["id"] for a in ads}) != len(ads):
        errors.append("coverage")
    return errors


def maturity(ad: dict, local_now) -> dict:
    windows = ad["windows"]
    yesterday = windows["yesterday"]["spend"] if local_now.hour < MATURE_HOUR else 0
    return {"maximum": max(0, windows["maximum"]["spend"] - windows["today"]["spend"] - yesterday),
            "last_7d": max(0, windows["last_7d"]["spend"] - yesterday)}


def evaluate(ad: dict, config: dict, observation: dict, baseline, local_now) -> dict:
    windows = ad["windows"]
    cold = windows["maximum"]["purchase"] == 0
    selected = "maximum" if cold else "last_7d"
    w = windows[selected]
    matured = maturity(ad, local_now)
    cpa = config["target_cpa"]
    ctr = w["clicks"] / w["impressions"] if w["impressions"] else 0
    lpv = w["spend"] / w["lpv"] if w["lpv"] else None
    observed = ad_observation(ad, observation)
    zero = w["purchase"] == 0 and windows["today"]["purchase"] == 0
    try:
        start = max(instant(ad["created_time"]), instant(ad["adset"]["start_time"]))
        age = (local_now - start).total_seconds() / 3600
    except (KeyError, ValueError, TypeError, AttributeError):
        age = None
    conditions = {
        "L0": (age is not None, age is not None and age > 72
               and windows["maximum"]["spend"] < config["l0_spend"], None),
        "L1": (cold and baseline is not None, zero and w["impressions"] >= 2000
               and baseline is not None and ctr < baseline * config["l1_ctr"], config["l1_spend"] * cpa),
        "L2": (True, zero and w["ic"] == 0 and windows["today"]["ic"] == 0, config["l2_spend"] * cpa),
        "L3": (True, zero, config["l3_spend"] * cpa),
        "L4": (not cold, w["purchase"] >= 3 and w["spend"] / max(1, w["purchase"]) > config["l4_cpa"] * cpa,
               config["l4_spend"] * cpa),
        "L5": (cold and "target_lpv" in config, zero and
               (lpv is None or lpv > config["l5_lpv"] * config.get("target_lpv", 0)), config["l5_spend"] * cpa)}
    layers, blocked, details = [], [], {}
    active = ad.get("status") == "ACTIVE" and ad.get("effective_status") == "ACTIVE"
    active = active and ad.get("campaign", {}).get("objective") == "OUTCOME_SALES"
    for layer, (applicable, condition, threshold) in conditions.items():
        reasons = []
        if layer == "L0" and not applicable and layer in config["enabled"]:
            reasons.append("l0_start_unknown")
            blocked.append("l0_start_unknown")
        elif layer not in config["enabled"] or not applicable:
            reasons.append("disabled_or_unavailable")
        elif condition and (threshold is None or w["spend"] > threshold):
            if layer in ("L1", "L2", "L3", "L5"):
                if observed != "valid":
                    reasons.append("observation")
                if matured[selected] <= threshold:
                    reasons.append("maturing")
            if not active:
                reasons.append("gate")
            if not reasons:
                layers.append(layer)
            blocked.extend(r for r in reasons if r not in blocked)
        details[layer] = {"window": "maximum" if layer == "L0" else selected,
                          "spend_threshold": threshold, "applicable": applicable, "blocked": reasons}
    missing_inputs = (cold and baseline is None and "L1" in config["enabled"]
                      or cold and "target_lpv" not in config and "L5" in config["enabled"])
    if missing_inputs and not blocked:
        blocked.append("gate")
    return {"ad_id": ad["id"], "ad_name": ad.get("name", ""),
            "campaign_name": ad.get("campaign", {}).get("name", ""),
            "state": "cold_start" if cold else "stable", "window": selected,
            "decision": "off_recommend" if layers else ("watch" if blocked else "ok"),
            "reasons": blocked, "layers": layers, "primary": next((l for l in PRIORITY if l in layers), None),
            "observation": observed, "inputs": windows, "matured_spend": matured,
            "baseline_ctr": baseline, "thresholds": config, "layer_details": details,
            "settings_version": config.get("version", 0)}


def judge(snapshot: dict, config: dict, now) -> dict:
    errors = gate(snapshot, config, now)
    if errors:
        return {"status": "watch", "reason": "gate", "gate_errors": errors, "decisions": []}
    config = validate(config)
    local = now.astimezone(account_timezone(snapshot["account"]))
    observation = account_observation(snapshot, now)
    ctrs = [r["clicks"] / r["impressions"] for r in snapshot["daily"] if r["impressions"] > 0]
    baseline = median(ctrs) if ctrs else None
    cutoff = local.date() - timedelta(days=1 if local.hour >= MATURE_HOUR else 2)
    return {"status": "evaluated", "account_id": snapshot["account_id"], "observation": observation,
            "mature_through": cutoff.isoformat(), "settings_version": config.get("version", 0),
            "decisions": [evaluate(ad, config, observation, baseline, local) for ad in snapshot["ads"]]}
