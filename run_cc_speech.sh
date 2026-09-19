#!/bin/bash
cd /www/korean_course
claude --dangerously-skip-permissions -p "$(cat /root/.openclaw/workspace/task_speech_write.md)" 2>&1 | tail -80
