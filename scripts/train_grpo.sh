#!/bin/bash
set -euo pipefail
source "$(dirname "$0")/common.sh"

MODEL=${MODEL:?set MODEL=<path to the base model>}
NAME=${NAME:-$(lowercase "$(basename "$MODEL")")_grpo}
OUT_ROOT=${OUT_ROOT:-checkpoints}
NGPU=${NGPU:-$(nvidia-smi -L | wc -l)}
EPOCHS=${EPOCHS:-5}
BATCH=${BATCH:-64}
GROUP=${GROUP:-8}
LR=${LR:-1e-5}
LORA_RANK=${LORA_RANK:-32}
MAX_PROMPT=${MAX_PROMPT:-32768}
MAX_RESPONSE=256
N_TRAIN=$(python -c "import pandas as pd; print(len(pd.read_parquet('grpo/data/train.parquet')))")
PER_EPOCH=$(( N_TRAIN / BATCH ))
SAVE_FREQ=${SAVE_FREQ:-$PER_EPOCH}
OUTDIR=$OUT_ROOT/$NAME
mkdir -p "$OUTDIR"
export VERL_USE_UV=0 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
export PYTHONPATH=$ROOT:${PYTHONPATH:-}

echo "GRPO · $MODEL · $NGPU GPU · batch $BATCH x group $GROUP · lr $LR · LoRA r$LORA_RANK · $EPOCHS epochs ($PER_EPOCH updates each) · -> $OUTDIR"
python -m verl.trainer.main_ppo \
    algorithm.adv_estimator=grpo \
    algorithm.use_kl_in_reward=False \
    data.train_files="$ROOT/grpo/data/train.parquet" \
    data.val_files="$ROOT/grpo/data/val.parquet" \
    data.train_batch_size=$BATCH \
    data.max_prompt_length=$MAX_PROMPT \
    data.max_response_length=$MAX_RESPONSE \
    data.filter_overlong_prompts=True \
    data.truncation=error \
    actor_rollout_ref.model.path="$MODEL" \
    actor_rollout_ref.model.lora_rank=$LORA_RANK \
    actor_rollout_ref.model.lora_alpha=$((2 * LORA_RANK)) \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.optim.lr=$LR \
    actor_rollout_ref.actor.ppo_mini_batch_size=$BATCH \
    actor_rollout_ref.actor.use_dynamic_bsz=True \
    actor_rollout_ref.actor.ppo_max_token_len_per_gpu=$((MAX_PROMPT + MAX_RESPONSE + 1024)) \
    actor_rollout_ref.actor.use_kl_loss=True \
    actor_rollout_ref.actor.kl_loss_coef=0.001 \
    actor_rollout_ref.actor.kl_loss_type=low_var_kl \
    actor_rollout_ref.actor.entropy_coeff=0 \
    actor_rollout_ref.actor.fsdp_config.param_offload=False \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=False \
    actor_rollout_ref.actor.fsdp_config.model_dtype=bfloat16 \
    actor_rollout_ref.rollout.name=vllm \
    actor_rollout_ref.rollout.tensor_model_parallel_size=$NGPU \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.5 \
    actor_rollout_ref.rollout.n=$GROUP \
    actor_rollout_ref.rollout.load_format=safetensors \
    actor_rollout_ref.rollout.layered_summon=True \
    actor_rollout_ref.rollout.enforce_eager=True \
    actor_rollout_ref.rollout.free_cache_engine=True \
    actor_rollout_ref.rollout.checkpoint_engine.update_weights_bucket_megabytes=2048 \
    actor_rollout_ref.rollout.log_prob_use_dynamic_bsz=True \
    actor_rollout_ref.rollout.log_prob_max_token_len_per_gpu=$((MAX_PROMPT + MAX_RESPONSE + 1024)) \
    actor_rollout_ref.ref.log_prob_use_dynamic_bsz=True \
    actor_rollout_ref.ref.log_prob_max_token_len_per_gpu=$((MAX_PROMPT + MAX_RESPONSE + 1024)) \
    actor_rollout_ref.ref.fsdp_config.param_offload=False \
    reward.custom_reward_function.path="$ROOT/grpo/reward.py" \
    reward.custom_reward_function.name=compute_score \
    trainer.balance_batch=True \
    trainer.logger='["console"]' \
    trainer.project_name=loweb_grpo \
    trainer.experiment_name="$NAME" \
    trainer.default_local_dir="$OUTDIR" \
    trainer.n_gpus_per_node=$NGPU \
    trainer.nnodes=1 \
    trainer.val_before_train=True \
    trainer.save_freq=$SAVE_FREQ \
    trainer.test_freq=$PER_EPOCH \
    trainer.total_epochs=$EPOCHS \
    "+ray_kwargs.ray_init.num_gpus=$NGPU" \
    "+ray_kwargs.ray_init.object_store_memory=17179869184" \
    ray_kwargs.ray_init.runtime_env.py_executable=null \
    ${EXTRA:-}
