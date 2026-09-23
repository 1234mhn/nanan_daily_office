#!/bin/bash
# 用法: ./ask_cc.sh "指令文件路径"
cd /root/.openclaw/workspace/huawei2026_F/paper
claude -p "$(cat "$1")" --allowedTools "Bash,Read,Write,Edit,Glob,Grep" 2>&1
