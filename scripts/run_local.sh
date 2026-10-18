#!/bin/bash
set -uo pipefail
source "$(dirname "$0")/common.sh"

MODEL=${MODEL:?set MODEL=<HF id or path>}
SITES=${SITES:-$ALL_SITES}
LANGS=${LANGS:-$ALL_LANGS}
TAG=${TAG:-$(lowercase "$(basename "$MODEL")")}
NAME=$TAG
[ "${STRICT:-0}" = 1 ] && export MWA_STRICT_PARSE=1 && TAG=${TAG}_strict
POP=${POPUPS:-0}
[ "$POP" = 1 ] && TAG=${TAG}_popups
if [ -n "${LIMIT:-}" ]; then OUT=trial/$(date +%Y%m%d_%H%M%S); else OUT=results; fi

start_vllm "$MODEL" "$NAME"
echo "model $MODEL · sites: $SITES · langs: $LANGS · limit: ${LIMIT:-all} · logs: $OUT/$TAG/"

run_lane() {
    local site=$1 lang suite log
    for lang in $LANGS; do
        suite=$(suite_name "$site" "$lang") || continue
        mkdir -p "$OUT/$TAG/$site"
        log=$OUT/$TAG/$site/$lang.log
        local -a pop=()
        [ "$POP" = 1 ] && pop=(--popups --popup-log "$OUT/$TAG/$site/$lang.popups.jsonl")
        echo "[$(date +%T)] start $suite -> $log"
        python -u -m benchmark.run_benchmark --agent local --lang "$suite" --autostart --trace \
            ${LIMIT:+--limit $LIMIT} ${pop[@]+"${pop[@]}"} > "$log" 2>&1
        echo "[$(date +%T)] done  $suite: $(grep -h '^Score:' "$log" || echo 'NO SCORE — see log')"
    done
}

LANES=()
for site in $SITES; do run_lane "$site" & LANES+=($!); done
wait "${LANES[@]}"
echo; echo "== summary ($TAG)"
grep -rH -e "^Score:" -e "^Pop-ups:" "$OUT/$TAG" --include=*.log | sort
