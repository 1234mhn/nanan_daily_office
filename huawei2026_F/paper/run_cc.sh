#!/bin/bash
export ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
export ANTHROPIC_BASE_URL="$ANTHROPIC_BASE_URL"
export ANTHROPIC_MODEL="$ANTHROPIC_MODEL"
cd /root/.openclaw/workspace/huawei2026_F/paper
exec claude --dangerously-skip-permissions
