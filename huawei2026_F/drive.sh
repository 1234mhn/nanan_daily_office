#!/bin/bash
# 分段驱动 Claude Code，避免长连接被掐断
# 用法: ./drive.sh "任务内容" [超时秒]

cd /root/.openclaw/workspace/huawei2026_F
export IS_SANDBOX=1
export ANTHROPIC_BASE_URL=https://api.lmuai.com
export ANTHROPIC_API_KEY=sk-e572de08dc1238734ae5ecc466d2019302b686239988a46014816ad827a79104

TASK="$1"
LOG="${2:-/tmp/cc_step.log}"

timeout 900 claude -p "$TASK" --dangerously-skip-permissions 2>&1 | tee "$LOG"
echo "=== EXIT: $? ==="
