ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
mkdir -p logs

ALL_SITES="portal selam rail ministore gari reddit"
ALL_LANGS="en bn hi ur am"

suite_name() {
    local pre
    case $1 in
        portal) pre=portal ;; selam) pre=selam ;; rail) pre=rail ;;
        ministore) pre=visual ;; gari) pre=visualgari ;; reddit) pre=visualreddit ;;
        *) echo "unknown site $1" >&2; return 1 ;;
    esac
    [ "$2" = en ] && echo "$pre" || echo "$pre$2"
}

start_vllm() {
    local model=$1 name=$2; shift 2
    PORT=${PORT:-8000}
    local log=logs/vllm_${name//\//_}.log
    vllm serve "$model" --served-model-name "$name" --host 127.0.0.1 --port "$PORT" \
        --tensor-parallel-size "${TP:-1}" --max-model-len "${MAX_LEN:-131072}" \
        --gpu-memory-utilization "${GPU_UTIL:-0.90}" "$@" ${VLLM_ARGS:-} > "$log" 2>&1 &
    VLLM_PID=$!
    trap 'kill $VLLM_PID 2>/dev/null' EXIT
    echo -n "waiting for vLLM ($log)"
    for i in $(seq 1 180); do
        if curl -sf "http://127.0.0.1:$PORT/v1/models" >/dev/null; then echo " up after $((i * 10))s"; break; fi
        if ! kill -0 $VLLM_PID 2>/dev/null; then echo; echo "vLLM died:"; tail -30 "$log"; exit 1; fi
        echo -n "."; sleep 10
    done
    curl -sf "http://127.0.0.1:$PORT/v1/models" >/dev/null || { echo "vLLM never came up"; exit 1; }
    export MWA_LOCAL_BASE_URL=http://127.0.0.1:$PORT/v1
    export MWA_LOCAL_MODEL=$name
}

lowercase() { echo "$1" | tr '[:upper:]' '[:lower:]'; }
