"""run 시드 표본 및 추천/비추천 응답 기록."""
import argparse
import random

from ledger import append
from runtime import emit, entry, identifier, read_json, state, utcnow


def select(result: dict, run_id: str) -> list:
    eligible = [row for row in result["decisions"] if row["decision"] in ("ok", "watch")
                and row["matured_spend"][row["window"]] > row["thresholds"]["target_cpa"] * 0.5]
    eligible.sort(key=lambda r: r["ad_id"])
    return random.Random(run_id).sample(eligible, min(3, len(eligible)))


def record(root, run: dict, ad: str, kind: str, response: str, now) -> dict:
    if response not in ("yes", "no", "skip") or kind not in ("recommendation", "sample"):
        raise ValueError("invalid_response")
    eligible = run["samples"] if kind == "sample" else [r for r in run["result"]["decisions"]
                                                        if r["decision"] == "off_recommend"]
    row = next((r for r in eligible if r["ad_id"] == ad), None)
    if row is None:
        raise ValueError("response_not_eligible")
    event = {"event": "response", "run_id": run["run_id"], "ad_id": ad, "kind": kind,
             "response": response, "layers": row["layers"], "at": now.isoformat()}
    append(root, event)
    return event


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True, type=identifier)
    parser.add_argument("--ad", type=identifier)
    parser.add_argument("--kind", choices=("recommendation", "sample"))
    parser.add_argument("--response", choices=("yes", "no", "skip"))
    args = parser.parse_args()
    run = read_json(state() / "runs" / (args.run + ".json"))
    if args.ad or args.kind or args.response:
        if not all((args.ad, args.kind, args.response)):
            parser.error("ad, kind, response required together")
        emit(record(state(), run, args.ad, args.kind, args.response, utcnow()))
    else:
        emit({"samples": run["samples"]})


if __name__ == "__main__":
    entry(main)
