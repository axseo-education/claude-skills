"""계정 목표 확정과 설정 변경 이력."""
import argparse
import math
from pathlib import Path

from runtime import emit, entry, identifier, read_json, state, utcnow, write_json

DEFAULTS = {"l0_spend": 2000, "l1_spend": 0.125, "l1_ctr": 0.5, "l2_spend": 1.0,
            "l3_spend": 1.5, "l4_spend": 2.0, "l4_cpa": 1.5, "l5_spend": 0.5,
            "l5_lpv": 2.0, "run_limit": 10, "day_limit": 20,
            "enabled": ["L0", "L1", "L2", "L3", "L4", "L5"]}


def validate(config: dict) -> dict:
    allowed = set(DEFAULTS) | {"target_cpa", "breakeven_cpa", "target_lpv", "confirmed", "version"}
    if set(config) - allowed:
        raise ValueError("unknown_setting")
    merged = {**DEFAULTS, **config}
    if merged.get("confirmed") is not True:
        raise ValueError("targets_unconfirmed")
    for key in ("target_cpa", "breakeven_cpa", "l0_spend", "l1_spend", "l1_ctr", "l2_spend",
                "l3_spend", "l4_spend", "l4_cpa", "l5_spend", "l5_lpv"):
        value = merged.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError("invalid_positive_setting")
    if "target_lpv" in merged and (isinstance(merged["target_lpv"], bool)
            or not isinstance(merged["target_lpv"], (int, float))
            or not math.isfinite(merged["target_lpv"]) or merged["target_lpv"] <= 0):
        raise ValueError("invalid_lpv_setting")
    for key, maximum in (("run_limit", 10), ("day_limit", 20)):
        value = merged[key]
        if type(value) is not int or not 0 <= value <= maximum:
            raise ValueError("invalid_limit")
    if not isinstance(merged["enabled"], list) or any(v not in DEFAULTS["enabled"] for v in merged["enabled"]):
        raise ValueError("invalid_layers")
    return merged


def load(root, account: str) -> dict:
    return validate(read_json(root / "settings.json")["accounts"][identifier(account)])


def save(root, account: str, config: dict, now) -> dict:
    from ledger import locked
    identifier(account)
    config = validate(config)
    with locked(root):
        path = root / "settings.json"
        data = read_json(path) if path.exists() else {"accounts": {}, "history": []}
        previous = data["accounts"].get(account)
        if previous and (config["run_limit"] > previous["run_limit"] or config["day_limit"] > previous["day_limit"]):
            raise ValueError("limits_can_only_decrease")
        config["version"] = (previous or {}).get("version", 0) + 1
        data["history"].append({"account_id": account, "at": now.isoformat(), "previous": previous,
                                "current": config})
        data["accounts"][account] = config
        write_json(path, data)
    return config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--account", required=True)
    parser.add_argument("--input", type=Path)
    args = parser.parse_args()
    result = save(state(), args.account, read_json(args.input), utcnow()) if args.input else load(state(), args.account)
    emit(result)


if __name__ == "__main__":
    entry(main)
