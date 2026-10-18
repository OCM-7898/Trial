import json
import random

import pandas as pd

SRC = "grpo/data/train_steps.jsonl"
SEED = 20261006


def main():
    rows = [json.loads(l) for l in open(SRC, encoding="utf-8")]
    rng = random.Random(SEED)
    held = {}
    for site in sorted({r["site"] for r in rows}):
        ids = sorted({r["task_id"] for r in rows if r["site"] == site})
        held[site] = rng.choice(ids)
    out = {"train": [], "val": []}
    for r in rows:
        gt = {"reference": r["reference"], "links": r["links"], "forms": r["forms"],
              "answer_checks": r.get("answer_checks") or []}
        out["val" if held[r["site"]] == r["task_id"] else "train"].append({
            "data_source": "loweb",
            "prompt": r["messages"],
            "ability": "web_agent",
            "reward_model": {"style": "rule", "ground_truth": json.dumps(gt, ensure_ascii=False)},
            "extra_info": {"task_id": r["task_id"], "site": r["site"], "lang": r["lang"],
                           "step": r["step"], "type": r["type"]},
        })
    for split, recs in out.items():
        pd.DataFrame(recs).to_parquet(f"grpo/data/{split}.parquet", index=False)
        print(f"grpo/data/{split}.parquet: {len(recs)} steps")
    print("held-out validation tasks:", held)


if __name__ == "__main__":
    main()
