#!/bin/bash
set -uo pipefail
source "$(dirname "$0")/common.sh"

AGENT=${AGENT:?set AGENT=gemini|openai|llm}
SITES=${SITES:-$ALL_SITES}
LANGS=${LANGS:-$ALL_LANGS}
LANES=${LANES:-6}
case $AGENT in
    gemini) MODEL_ID=${MWA_GEMINI_MODEL:-gemini-3.1-flash-lite} ;;
    openai) MODEL_ID=${MWA_OPENAI_MODEL:-gpt-4o-mini} ;;
    llm)    MODEL_ID=${MWA_ANTHROPIC_MODEL:-claude-sonnet-4-5} ;;
    *) echo "unknown AGENT=$AGENT (gemini|openai|llm)"; exit 1 ;;
esac
if [ -z "${TAG:-}" ]; then
    TAG=$MODEL_ID
    [ -n "${MWA_THINK_BUDGET:-}" ] && TAG=${TAG}-think${MWA_THINK_BUDGET}
    [ -n "${MWA_REASONING_EFFORT:-}" ] && TAG=${TAG}-${MWA_REASONING_EFFORT}
fi
POP=${POPUPS:-0}
[ "$POP" = 1 ] && TAG=${TAG}_popups
if [ -n "${LIMIT:-}" ]; then OUT=trial/$(date +%Y%m%d_%H%M%S); else OUT=results; fi
echo "agent $AGENT · model $MODEL_ID · sites: $SITES · langs: $LANGS · limit: ${LIMIT:-all} · logs: $OUT/$TAG/"

run_lane() {
    local site=$1 lang suite log
    for lang in $LANGS; do
        suite=$(suite_name "$site" "$lang") || continue
        mkdir -p "$OUT/$TAG/$site"
        log=$OUT/$TAG/$site/$lang.log
        local -a pop=()
        [ "$POP" = 1 ] && pop=(--popups --popup-log "$OUT/$TAG/$site/$lang.popups.jsonl")
        echo "[$(date +%T)] start $suite -> $log"
        python -u -m benchmark.run_benchmark --agent "$AGENT" --lang "$suite" --autostart --trace \
            ${LIMIT:+--limit $LIMIT} ${pop[@]+"${pop[@]}"} > "$log" 2>&1
        echo "[$(date +%T)] done  $suite: $(grep -h '^Score:' "$log" || echo 'NO SCORE — see log')"
    done
}

PIDS=()
for site in $SITES; do
    while [ "$(jobs -rp | wc -l)" -ge "$LANES" ]; do sleep 5; done
    run_lane "$site" & PIDS+=($!)
done
wait "${PIDS[@]}"
echo; echo "== summary ($TAG)"
grep -rH -e "^Score:" -e "^API usage:" -e "^Pop-ups:" "$OUT/$TAG" --include=*.log | sort
