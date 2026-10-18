#!/bin/bash
set -uo pipefail
source "$(dirname "$0")/common.sh"

AGENT=${AGENT:-local}
SITES=${SITES:-"ministore gari reddit"}
LANGS=${LANGS:-$ALL_LANGS}
case $AGENT in
    local)  MODEL=${MODEL:?set MODEL=<HF id or path> (or AGENT=gemini|openai)}
            DEFAULT_TAG=$(lowercase "$(basename "$MODEL")") ;;
    gemini) DEFAULT_TAG=${MWA_GEMINI_MODEL:-gemini-3.1-flash-lite} ;;
    openai) DEFAULT_TAG=${MWA_OPENAI_MODEL:-gpt-4o-mini} ;;
    *) echo "unknown AGENT=$AGENT (local|gemini|openai)"; exit 1 ;;
esac
if [ -z "${TAG:-}" ]; then
    TAG=$DEFAULT_TAG
    [ "$AGENT" != local ] && [ -n "${MWA_THINK_BUDGET:-}" ] && TAG=${TAG}-think${MWA_THINK_BUDGET}
    [ "$AGENT" != local ] && [ -n "${MWA_REASONING_EFFORT:-}" ] && TAG=${TAG}-${MWA_REASONING_EFFORT}
fi
if [ -n "${LIMIT:-}" ]; then OUT=trial/$(date +%Y%m%d_%H%M%S)/screenshot; else OUT=results/screenshot; fi

[ "$AGENT" = local ] && start_vllm "$MODEL" "$TAG" --limit-mm-per-prompt '{"image": 8}'
echo "agent $AGENT-screenshot · sites: $SITES · langs: $LANGS · limit: ${LIMIT:-all} · logs: $OUT/$TAG/"

run_lane() {
    local site=$1 lang log
    mkdir -p "$OUT/$TAG/$site"
    for lang in $LANGS; do
        log=$OUT/$TAG/$site/$lang.log
        echo "[$(date +%T)] start $site/$lang -> $log"
        python -u -m benchmark.screenshot.run_screenshot_benchmark --agent "$AGENT-screenshot" \
            --site "$site" --lang "$lang" --autostart --trace ${LIMIT:+--limit $LIMIT} > "$log" 2>&1
        echo "[$(date +%T)] done  $site/$lang: $(grep -h '^Score:' "$log" || echo 'NO SCORE — see log')"
    done
}

PIDS=()
for site in $SITES; do run_lane "$site" & PIDS+=($!); done
wait "${PIDS[@]}"
echo; echo "== summary ($TAG, visual tasks)"
grep -rH -e "^Score:" -e "^API usage:" -e "^Screenshot failures:" "$OUT/$TAG" --include=*.log | sort
