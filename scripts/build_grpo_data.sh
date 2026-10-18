#!/bin/bash
set -euo pipefail
source "$(dirname "$0")/common.sh"

mkdir -p grpo/data/steps
for site in $ALL_SITES; do
    for lang in $ALL_LANGS; do
        suite=$(suite_name "$site" "$lang")
        echo "[$(date +%T)] $suite"
        python -m grpo.build_train_data --lang "$suite"
    done
done
cat grpo/data/steps/*.jsonl > grpo/data/train_steps.jsonl
python -m grpo.make_parquet
