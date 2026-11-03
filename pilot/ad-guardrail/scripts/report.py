"""응답률 분모에 skip과 무응답을 남기는 시범 집계."""
from ledger import read
from runtime import emit, entry, state


def report(events: list) -> dict:
    invitations, responses, days, executions, attempts = {}, {}, set(), {}, set()
    for event in events:
        run = event.get("run_id")
        if event["event"] == "run":
            days.add(event["day"])
            for row in event["result"]["decisions"]:
                if row["decision"] == "off_recommend":
                    invitations[(run, row["ad_id"], "recommendation")] = row["layers"]
            for row in event["samples"]:
                applicable = [layer for layer, detail in row.get("layer_details", {}).items()
                              if detail["applicable"] and layer in row.get("thresholds", {}).get("enabled", [])]
                invitations[(run, row["ad_id"], "sample")] = applicable or ["none"]
        elif event["event"] == "response":
            responses[(run, event["ad_id"], event["kind"])] = event["response"]
        elif event["event"] == "attempt":
            attempts.add((run, event["ad_id"]))
        elif event["event"] == "execution":
            executions[(run, event["ad_id"])] = event["status"]

    def summarize(keys):
        counts = {key: 0 for key in ("yes", "no", "skip", "unanswered")}
        for key in keys:
            counts[responses.get(key, "unanswered")] += 1
        answered = counts["yes"] + counts["no"]
        return {**counts, "total": len(keys), "answered": answered,
                "response_rate": answered / len(keys) if keys else None,
                "yes_rate_answered": counts["yes"] / answered if answered else None,
                "yes_rate_all": counts["yes"] / len(keys) if keys else None}

    groups = {kind: summarize([k for k in invitations if k[2] == kind]) for kind in ("recommendation", "sample")}
    layers = {layer: {kind: summarize([k for k, values in invitations.items() if layer in values and k[2] == kind])
                     for kind in groups} for layer in ("L0", "L1", "L2", "L3", "L4", "L5", "none")}
    rec, sample = groups["recommendation"], groups["sample"]
    eligible = rec["answered"] >= 30 and sample["answered"] >= 30
    met = eligible and rec["yes_rate_answered"] >= 0.8 and sample["yes_rate_answered"] <= 0.1
    return {"groups": groups, "layers": layers, "execution_days": len(days),
            "execution_counts": {s: sum(v == s for v in executions.values())
                                 for s in ("success", "failed", "not_verified", "rejected")},
            "not_attempted": sum((k[0], k[1]) not in attempts for k in invitations if k[2] == "recommendation"),
            "pending_attempts": len(attempts - {k for k, v in executions.items() if v != "not_attempted"}),
            "ac8": {"provisional_thresholds": True, "enough_responses": eligible, "met": met}}


if __name__ == "__main__":
    entry(lambda: emit(report(read(state()))))
