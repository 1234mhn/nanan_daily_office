#!/bin/bash
cd /root/.openclaw/workspace/huawei2026_F
export IS_SANDBOX=1
export ANTHROPIC_BASE_URL=https://api.lmuai.com
export ANTHROPIC_API_KEY=sk-e572de08dc1238734ae5ecc466d2019302b686239988a46014816ad827a79104
nohup claude -p "$(cat START_TASK.md)" --dangerously-skip-permissions > /tmp/cc_mm_f.log 2>&1 &
echo "PID=$!"
