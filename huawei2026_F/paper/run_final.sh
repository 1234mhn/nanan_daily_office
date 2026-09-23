#!/bin/bash
cd /root/.openclaw/workspace/huawei2026_F/paper
export ANTHROPIC_BASE_URL=https://api.lmuai.com
export ANTHROPIC_MODEL=claude-sonnet-4-5
claude -p "$(cat TASK_收尾.md)" --allowedTools "Bash,Read,Write,Edit,Glob,Grep" 2>&1
