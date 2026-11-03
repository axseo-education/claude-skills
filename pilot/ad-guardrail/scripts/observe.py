"""구매 관측 상태. 호출자가 전달한 시각만 사용한다."""
from runtime import instant


def account_observation(snapshot: dict, now) -> dict:
    alive = False
    for pixel in snapshot["pixels"]:
        try:
            age = (now - instant(pixel["last_fired_time"])).total_seconds()
            alive = alive or 0 <= age <= 48 * 3600
        except (KeyError, ValueError, TypeError):
            continue
    values = snapshot["reconciliation"]
    tolerance = max(1, values["account_purchase"] * 0.02)
    reconciled = abs(values["ad_purchase"] - values["account_purchase"]) <= tolerance
    return {"state": "missing" if not alive else ("valid" if reconciled else "contested"),
            "pixel_alive": alive, "reconciled": reconciled, "tolerance": tolerance, **values}


def ad_observation(ad: dict, account: dict) -> str:
    if any(window["alias_mismatch"] for window in ad["windows"].values()):
        return "contested"
    return account["state"]
