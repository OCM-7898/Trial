#!/bin/bash
set -euo pipefail
source "$(dirname "$0")/common.sh"

CKPT=${CKPT:?set CKPT=<.../global_step_N>}
BASE=${BASE:?set BASE=<path to the base model the run started from>}
OUT=${OUT:?set OUT=<output model dir>}
TMP=${OUT}_merger_tmp
rm -rf "$TMP"
python -m verl.model_merger merge --backend fsdp --local_dir "$CKPT/actor" --target_dir "$TMP"
ADAPTER=$(dirname "$(find "$TMP" -name adapter_config.json | head -1)")
[ -n "$ADAPTER" ] || { echo "no LoRA adapter found in $TMP"; exit 1; }

python - "$BASE" "$ADAPTER" "$OUT" <<'EOF'
import json, os, shutil, sys, torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoModelForImageTextToText, AutoTokenizer
base, adapter, out = sys.argv[1:]
arch = json.load(open(os.path.join(base, "config.json")))["architectures"][0]
vlm = arch.endswith("ForConditionalGeneration")
auto = AutoModelForImageTextToText if vlm else AutoModelForCausalLM
model = auto.from_pretrained(base, torch_dtype=torch.bfloat16)
model = PeftModel.from_pretrained(model, adapter).merge_and_unload()
model.save_pretrained(out, safe_serialization=True)
AutoTokenizer.from_pretrained(base).save_pretrained(out)
for f in ("preprocessor_config.json", "processor_config.json", "chat_template.json", "chat_template.jinja"):
    if os.path.exists(os.path.join(base, f)):
        shutil.copy(os.path.join(base, f), out)
print(f"[done] merged model at {out}")
EOF
rm -rf "$TMP"
